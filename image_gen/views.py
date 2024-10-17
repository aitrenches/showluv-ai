import base64
import logging
from io import BytesIO

from django.conf import settings
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from openai import OpenAI
from PIL import Image
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from youtube_to_twitter.authentication import APIKeyAuthentication

from .models import GeneratedImage, ImagePrompt, Product, Sale
from .serializers import GeneratedImageSerializer, ImagePromptSerializer, ProductSerializer, AddQuantitySerializer, SellProductSerializer, SaleSerializer

# Get an instance of a logger
logger = logging.getLogger(__name__)


class ImageGenerator(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def __init__(self):
        super().__init__()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    @swagger_auto_schema(
        operation_summary="Generate an image and its variations",
        operation_description="Generates an image based on a prompt and creates three variations of the generated image.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "prompt": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Text prompt to generate the image",
                ),
            },
            required=["prompt"],
        ),
        responses={
            200: openapi.Response(
                description="Successful response with generated and resized images",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "images": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Base64 encoded image",
                            ),
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Bad Request Error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Error message"
                        ),
                    },
                ),
            ),
            500: openapi.Response(
                description="Internal Server Error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Error message"
                        ),
                    },
                ),
            ),
        },
    )
    def post(self, request, size):
        prompt_text = request.data.get("prompt")

        if not prompt_text:
            return Response(
                {"error": "A prompt is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Parse size parameter (e.g., 1024x1024)
        try:
            width, height = map(int, size.lower().split("x"))
        except ValueError:
            return Response(
                {"error": "Invalid size format. Use WIDTHxHEIGHT (e.g., 1024x1024)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Improve the prompt
            improved_prompt = self.improve_prompt(prompt_text)

            # Save prompt to the database
            prompt_instance = ImagePrompt.objects.create(
                prompt=prompt_text, improved_prompt=improved_prompt
            )

            # Generate the initial image
            image_data = self.generate_image_using_openai_dalle(improved_prompt)

            # Generate three variations from the initial image
            variations_data = (
                self.generate_three_variations_from_image_using_openai_dalle(
                    image_data["image"]
                )
            )

            # Resize the images to the requested size
            resized_variations = self.resize_and_save_images(
                prompt_instance, variations_data["images"], width, height
            )

            # Assuming you pass a 'fields' parameter in the request e.g ?fields=uuid,prompt
            requested_fields = request.query_params.get("fields", None)
            if requested_fields:
                requested_fields = requested_fields.split(",")

                serialized_prompt = ImagePromptSerializer(
                    prompt_instance,
                    fields=requested_fields
                    if requested_fields
                    else ["uuid", "prompt", "images"],
                )

            return Response(resized_variations, status=status.HTTP_200_OK)

        except ConnectionError as e:
            logger.error(f"Connection error occurred: {str(e)}")
            return Response(
                {
                    "error": "Unable to connect to the image generation service. Please try again later."
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            return Response(
                {"error": "An internal server error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def improve_prompt(self, prompt):
        user_prompt = f"Generate a better and improved image generation prompt from the following prompt:\n\n{prompt}\n\n"

        system_prompt = """
        You are a helpful assistant that improves image generation prompts to generate better images
                        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = self.client.chat.completions.create(
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
            print("(((((((((((((((((((())))))))))))))))))))")
            print(response)
            return response.choices[0].message.content.strip()
        except Exception as e:
            # print('(((((((((((((((((((( ERROR ))))))))))))))))))))')
            # return prompt
            raise Exception(f"OpenAI API error: {str(e)}")

    def generate_image_using_openai_dalle(self, prompt):
        """Generates a single image using DALL-E 3."""
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            response_format="b64_json",
        )
        print("(((((((((((((((((((())))))))))))))))))))")
        print("image generated")
        return {"image": response.data[0].b64_json}

    def generate_three_variations_from_image_using_openai_dalle(self, base64_image):
        """Generates three variations from a base64 image using DALL-E 3."""
        image_data = base64.b64decode(base64_image)
        response = self.client.images.create_variation(
            image=image_data,
            n=3,
            response_format="b64_json",
        )
        print("(((((((((((((((((((())))))))))))))))))))")
        print("three variations generated")
        return {"images": [img.b64_json for img in response.data]}

    def resize_and_save_images(self, prompt_instance, base64_images, width, height):
        """Resizes the base64 images to the specified dimensions."""
        images = []

        for i in base64_images:
            # Decode the base64 image to bytes
            image_data = base64.b64decode(i)

            # Open the image from bytes using Pillow
            image = Image.open(BytesIO(image_data))

            # Resize the image to the specified dimensions
            resized_image = image.resize((width, height))

            # Convert the resized image back to base64
            buffered = BytesIO()
            resized_image.save(buffered, format="PNG")
            resized_image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # Create and save resized image
            GeneratedImage.objects.create_variation(
                prompt=prompt_instance,
                image_data=i,  # Store as a ContentFile, which will be uploaded to S3
                width=width,
                height=height,
            )
            print("(((((((((((((((((((())))))))))))))))))))")
            print("three images saved")
            images.append(resized_image_base64)
        print("(((((((((((((((((((())))))))))))))))))))")
        print("three images resized")
        return {"images": images}

######################## TEST 2 Start ##############################

class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        request_body=ProductSerializer,
        responses={
            status.HTTP_201_CREATED: ProductSerializer,
            status.HTTP_400_BAD_REQUEST: 'Bad Request',
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: ProductSerializer,
            status.HTTP_404_NOT_FOUND: 'Product not found',
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_object(self):
        lookup_value = self.kwargs.get('pk')

        try:
            # If lookup_value is an integer, assume it's a primary key
            lookup_value = int(lookup_value)
            return Product.objects.get(pk=lookup_value)
        except ValueError:
            # If ValueError occurs, it means lookup_value is not an integer, so we search by productName
            return Product.objects.get(name=lookup_value)
        except Product.DoesNotExist:
            raise Http404("Product not found.")

class AddQuantityView(generics.CreateAPIView):
    serializer_class = AddQuantitySerializer

    @swagger_auto_schema(
        request_body=AddQuantitySerializer,
        responses={
            status.HTTP_200_OK: openapi.Response('Product quantity updated successfully'),
            status.HTTP_400_BAD_REQUEST: 'Bad Request',
        }
    )
    def post(self, request, *args, **kwargs):
        '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
        print("Incoming payload: ", request.data)
        '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
        return super().post(request, *args, **kwargs)

class SellProductView(generics.CreateAPIView):
    serializer_class = SellProductSerializer

    @swagger_auto_schema(
        request_body=SellProductSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response('Product sold successfully'),
            status.HTTP_400_BAD_REQUEST: 'Bad Request',
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class SalesHistoryView(generics.ListAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: SaleSerializer(many=True),
            status.HTTP_404_NOT_FOUND: 'Sales history not found',
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

######################## TEST 2 End ##############################