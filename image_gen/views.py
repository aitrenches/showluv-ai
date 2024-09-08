from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import json
from django.http import JsonResponse
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from youtube_to_twitter.authentication import APIKeyAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.conf import settings
from openai import OpenAI
import base64
from io import BytesIO
from PIL import Image
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class ImageGenerator(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def __init__(self):
        super().__init__()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def post(self, request, size):
        prompt = request.data.get('prompt')

        if not prompt:
            return Response({"error": "A prompt is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Parse size parameter (e.g., 1024x1024)
        try:
            width, height = map(int, size.lower().split('x'))
        except ValueError:
            return Response({"error": "Invalid size format. Use WIDTHxHEIGHT (e.g., 1024x1024)."}, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            # Generate the initial image
            image_data = self.generate_image_using_openai_dalle(prompt)

            # Generate three variations from the initial image
            variations_data = self.generate_three_variations_from_image_using_openai_dalle(image_data['image'])

            # Resize the images to the requested size
            resized_variations = self.resize_images(variations_data['images'], width, height)

            return Response(resized_variations, status=status.HTTP_200_OK)
        except Exception as e:
            # Log the exception for debugging purposes
            logger.error(f"Error occurred: {str(e)}")
            # Return a simple error response
            return Response({"error": "An internal server error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_image_using_openai_dalle(self, prompt):
        """Generates a single image using DALL-E 3."""
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            response_format="b64_json",
        )
        return {"image": response.data[0].b64_json}

    def generate_three_variations_from_image_using_openai_dalle(self, base64_image):
        """Generates three variations from a base64 image using DALL-E 3."""
        image_data = base64.b64decode(base64_image)
        response = self.client.images.create_variation(
            image=image_data,
            n=3,
            response_format="b64_json",
        )
        return {"images": [img.b64_json for img in response.data]}
    
    def resize_images(self, base64_images, width, height):
        """Resizes the base64 images to the specified dimensions."""
        images = []

        for image in base64_images:
            # Decode the base64 image to bytes
            image_data = base64.b64decode(image)
            
            # Open the image from bytes using Pillow
            image = Image.open(BytesIO(image_data))
            
            # Resize the image to the specified dimensions
            resized_image = image.resize((width, height))
            
            # Convert the resized image back to base64
            buffered = BytesIO()
            resized_image.save(buffered, format="PNG")
            resized_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            images.append(resized_image_base64)

        return {"images" : images}

