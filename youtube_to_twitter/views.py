from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from youtube_transcript_api import YouTubeTranscriptApi
import re
import openai
import os
import json
from django.http import JsonResponse
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from .authentication import APIKeyAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import anthropic
from youtube_transcript_api._errors import TranscriptsDisabled
from googleapiclient.discovery import build
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from .mailgun_mailer import send_simple_summary
import logging
from .ses_mailer import send_summary_email
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt

# Create an instance of the Anthropics API client
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
logger = logging.getLogger(__name__)

class YouTubeToTwitterView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['youtube_url'],
            properties={
                'youtube_url': openapi.Schema(type=openapi.TYPE_STRING, description='YouTube video URL')
            },
        ),
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'video_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'video_length': openapi.Schema(type=openapi.TYPE_STRING),
                        'transcript_available': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'twitter_thread': openapi.Schema(type=openapi.TYPE_STRING, description='Generated Twitter thread')
                    },
                )
            ),
            400: 'Bad Request',
            500: 'Internal Server Error'
        }
    )
    
    def post(self, request):
        youtube_url = request.data.get('youtube_url')
        if not youtube_url:
            raise ValidationError({'youtube_url': 'YouTube URL is required'})

        video_id = self.extract_video_id(youtube_url)
        if not video_id:
            raise ValidationError({'youtube_url': 'Invalid YouTube URL'})

        try:
            transcript, raw_transcript = self.get_youtube_transcript(video_id)
        except Exception as e:
            raise ValidationError({'error': f'Error getting transcript: {str(e)}'})

        # raw_transcript = YouTubeTranscriptApi.get_transcript(video_id)
        video_length = sum([float(entry['duration']) for entry in raw_transcript])
        # Convert video_length to hours and minutes
        hours = int(video_length // 3600)
        minutes = int((video_length % 3600) // 60)
        formatted_length = f"{hours} hour(s) {minutes} minutes"

        try:
            twitter_thread = self.generate_twitter_thread_using_openai(transcript)
            return Response({   
                                'video_id' : video_id,
                                'video_length': formatted_length,
                                'transcript_available': True,
                                'twitter_thread': twitter_thread,
                            })
        except Exception as e:
            raise ValidationError({'error': f'Error generating Twitter thread: {str(e)}'})

    def extract_video_id(self, url):
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        if video_id_match:
            return video_id_match.group(1)
        return None

    def get_youtube_transcript(self, video_id):
        try:
            raw_transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join([entry['text'] for entry in raw_transcript])
            return transcript, raw_transcript
        except Exception as e:
            return str(e)

    def xget_youtube_transcript(self, video_id):
        youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        youtube = build('youtube', 'v3', developerKey=youtube_api_key)

        try:
            # Retrieve the video information
            video_response = youtube.videos().list(
                part='snippet,contentDetails',
                id=video_id
            ).execute()

            # Check if the video exists and has captions
            if not video_response['items']:
                return {"error": "Video not found"}

            captions_response = youtube.captions().list(
                part='snippet',
                videoId=video_id
            ).execute()

            # Check if captions are available
            if not captions_response['items']:
                return {"error": "No captions available for this video"}

            # Retrieve captions (transcript)
            caption_id = captions_response['items'][0]['id']
            caption_track = youtube.captions().download(id=caption_id).execute()

            return caption_track.decode('utf-8')

        except Exception as e:
            return {"error": str(e)}

    def generate_twitter_thread_using_openai(self, transcript):
        openai.api_key = os.getenv("OPENAI_API_KEY")

        user_prompt = f"Generate a Twitter thread from the following YouTube video transcript:\n\n{transcript}\n\nTwitter Thread:"
        
        system_prompt = '''
        You are a helpful assistant that generates Twitter threads from YouTube video transcripts.
        All your response should be in nothing but a key-value JSON format. Do not add any newline(i.e / n) between your response.
        Do not add any other text other than the JSON response. Format the JSON in the following format:
        {
            "1": "This is the first tweet of the thread...",
            "2": "This is the second tweet of the thread...",
            "3": "This is the third tweet of the thread...",
        }
                        '''

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.0,
                top_p=1,
                frequency_penalty=0.1,
                presence_penalty=0.1,
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def generate_twitter_thread_using_anthropic(self, transcript):

        user_prompt = f"Generate a Twitter thread from the following YouTube video transcript:\n\n{transcript}\n\nTwitter Thread:"
        
        system_prompt = '''
        You are a helpful assistant that generates Twitter threads from YouTube video transcripts.
        Do not start with any preamble or opening sentence or whatever e.g: "Here's a Twitter thread summarizing the key points from the YouTube video transcript:",
        Respond only in the following JSON format without any additional text or newlines:
        {
            "1": "This is the first tweet of the thread...",
            "2": "This is the second tweet of the thread...",
            "3": "This is the third tweet of the thread..."
        }
                        '''
        
        try:
            response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.9
            )
            
            # Extract the text from the response content
            content_text = response.content[0].text

            return content_text
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

# @method_decorator(csrf_exempt, name='dispatch')
class SummaryThread(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    @swagger_auto_schema(
        operation_description="Summarize a YouTube video transcript",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['youtube_url'],
            properties={
                'youtube_url': openapi.Schema(type=openapi.TYPE_STRING, description="URL of the YouTube video"),
            },
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Summary & Thread generated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'thread': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Invalid input",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'youtube_url': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                    },
                ),
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description="Server error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
        },
    )

    def post(self, request):
        youtube_url = request.data.get('youtube_url')
        
        if not youtube_url:
            raise ValidationError({'youtube_url': 'YouTube URL is required'})
                
        video_id = self.extract_video_id(youtube_url)
        if not video_id:
            raise ValidationError({'youtube_url': 'Invalid YouTube URL'})
        
        try:
            # Get transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join([entry['text'] for entry in transcript])
            
            # Summarize text
            summary = self.summarize_text(full_text)

            thread = self.generate_twitter_thread_using_openai(summary)
            
            return JsonResponse({'message': f'{summary}', 'thread': f'{thread}'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def generate_twitter_thread_using_openai(self, summary):
        openai.api_key = os.getenv("OPENAI_API_KEY")

        user_prompt = f"Generate a Twitter thread from the following YouTube video transcript summary:\n\n{summary}\n\nTwitter Thread:"
        
        system_prompt = '''
        You are a helpful assistant that generates Twitter threads from YouTube video transcripts summary.
        All your response should be in simple english. Do not be verbose.
                        '''

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.0,
                top_p=1,
                frequency_penalty=0.1,
                presence_penalty=0.1,
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def summarize_text(self, transcript):
        openai.api_key = os.getenv("OPENAI_API_KEY")

        user_prompt = f"Generate a detailed summary from the following YouTube video transcript:\n\n{transcript}\n\n"
        
        system_prompt = '''
        You are a helpful assistant that generates summaries from YouTube video transcripts.
        Format your response in simple english
                        '''

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.0,
                top_p=1,
                frequency_penalty=0.1,
                presence_penalty=0.1,
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def extract_video_id(self, url):
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        if video_id_match:
            return video_id_match.group(1)
        return None

class VideoInfoView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('youtube_url', openapi.IN_QUERY, description="YouTube video URL", type=openapi.TYPE_STRING, required=True),
        ],
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'video_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'length': openapi.Schema(type=openapi.TYPE_STRING),
                        'transcript_available': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                )
            ),
            400: 'Bad Request'
        }
    )
    def get(self, request):
        youtube_url = request.query_params.get('youtube_url')
        if not youtube_url:
            raise ValidationError({'youtube_url': 'YouTube URL is required'})

        video_id = self.extract_video_id(youtube_url)
        if not video_id:
            raise ValidationError({'video_id': 'Invalid YouTube URL'})

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            video_length = sum([float(entry['duration']) for entry in transcript])
            
            # Convert video_length to hours and minutes
            hours = int(video_length // 3600)
            minutes = int((video_length % 3600) // 60)
            formatted_length = f"{hours} hour(s) {minutes} minutes"
            
            return Response({
                'video_id': video_id,
                'length': formatted_length,
                'transcript_available': True
            })
        except Exception as e:
            return Response({
                'video_id': video_id,
                'error': str(e),
                'transcript_available': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
    def extract_video_id(self, url):
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        if video_id_match:
            return video_id_match.group(1)
        return None
        
class CustomThreadView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        youtube_url = request.data.get('youtube_url')
        tweet_count = request.data.get('tweet_count', 5)
        style = request.data.get('style', 'informative')

        # ... validate inputs ...
        video_id = 1

        transcript = self.get_youtube_transcript(video_id)
        twitter_thread = self.generate_custom_thread(transcript, tweet_count, style)

        return Response({'twitter_thread': twitter_thread})

    def generate_custom_thread(self, transcript, tweet_count, style):
        # Implement custom thread generation using OpenAI API
        # Adjust the prompt to include tweet_count and style parameters
        pass