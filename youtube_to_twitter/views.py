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
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import YouTubeToTwitterInputSerializer, YouTubeToTwitterOutputSerializer

class YouTubeToTwitterView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    # serializer_class = YouTubeToTwitterInputSerializer

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

    # @extend_schema(
    #     request=YouTubeToTwitterInputSerializer,
    #     responses={200: YouTubeToTwitterOutputSerializer},
    #     description='Generate a Twitter thread from a YouTube video',
    #     tags=['YouTube to Twitter'],
    # )
    
    def post(self, request):
        youtube_url = request.data.get('youtube_url')
        if not youtube_url:
            raise ValidationError({'youtube_url': 'YouTube URL is required'})

        video_id = self.extract_video_id(youtube_url)
        if not video_id:
            raise ValidationError({'youtube_url': 'Invalid YouTube URL'})

        try:
            transcript = self.get_youtube_transcript(video_id)
        except Exception as e:
            raise ValidationError({'error': f'Error getting transcript: {str(e)}'})

        raw_transcript = YouTubeTranscriptApi.get_transcript(video_id)
        video_length = sum([float(entry['duration']) for entry in raw_transcript])
        # Convert video_length to hours and minutes
        hours = int(video_length // 3600)
        minutes = int((video_length % 3600) // 60)
        formatted_length = f"{hours} hour(s) {minutes} minutes"

        try:
            twitter_thread = self.generate_twitter_thread(transcript)
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
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([entry['text'] for entry in transcript])
        except Exception as e:
            return str(e)
    
    def generate_twitter_thread(self, transcript):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates Twitter threads from YouTube video transcripts. Format your response as a JSON array of numbered tweets. Each tweet should be a JSON object with a number as the key and the tweet content as the value. For example: [{'1': 'First tweet content'}, {'2': 'Second tweet content'}]"},
            {"role": "user", "content": f"Generate a Twitter thread from the following YouTube video transcript:\n\n{transcript}\n\nTwitter Thread:"}
        ]
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages,
                max_tokens=1000,
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

# class VideoInfoView(APIView):
#     authentication_classes = [APIKeyAuthentication]
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         manual_parameters=[
#             openapi.Parameter('youtube_url', openapi.IN_QUERY, description="YouTube video URL", type=openapi.TYPE_STRING, required=True),
#         ],
#         responses={
#             200: openapi.Response(
#                 description="Successful response",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'video_id': openapi.Schema(type=openapi.TYPE_STRING),
#                         'length': openapi.Schema(type=openapi.TYPE_STRING),
#                         'transcript_available': openapi.Schema(type=openapi.TYPE_BOOLEAN),
#                     },
#                 )
#             ),
#             400: 'Bad Request'
#         }
#     )
#     def get(self, request):
#         youtube_url = request.query_params.get('youtube_url')
#         if not youtube_url:
#             raise ValidationError({'youtube_url': 'YouTube URL is required'})

#         video_id = self.extract_video_id(youtube_url)
#         if not video_id:
#             raise ValidationError({'video_id': 'Invalid YouTube URL'})

#         try:
#             transcript = YouTubeTranscriptApi.get_transcript(video_id)
#             video_length = sum([float(entry['duration']) for entry in transcript])
            
#             # Convert video_length to hours and minutes
#             hours = int(video_length // 3600)
#             minutes = int((video_length % 3600) // 60)
#             formatted_length = f"{hours} hour(s) {minutes} minutes"
            
#             return Response({
#                 'video_id': video_id,
#                 'length': formatted_length,
#                 'transcript_available': True
#             })
#         except Exception as e:
#             return Response({
#                 'video_id': video_id,
#                 'error': str(e),
#                 'transcript_available': False
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#     def extract_video_id(self, url):
#         video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
#         if video_id_match:
#             return video_id_match.group(1)
#         return None
        
# class CustomThreadView(APIView):
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