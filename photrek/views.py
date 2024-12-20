from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import pandas as pd
from snet import sdk
import base64
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from youtube_to_twitter.authentication import APIKeyAuthentication

import environ
env = environ.Env()
environ.Env.read_env()

PRIVATE_KEY = env("PRIVATE_KEY")
INFURA_KEY = env("INFURA_KEY")


config = sdk.config.Config(private_key=PRIVATE_KEY,
                eth_rpc_endpoint=f"https://mainnet.infura.io/v3/{INFURA_KEY}", # RPC endpoint of "mainnet" network
                concurrency=False,
                force_update=False)

def ingest_csv(file):
    """
    Ingests a CSV file and formats it into the input string required by the service.

    Args:
        file (UploadedFile or File-like object): The CSV file to process.

    Returns:
        str: The formatted input string.
    """
    # Read the CSV into a pandas DataFrame
    data = pd.read_csv(file, header=None)

    # Step 1: Retrieve row and column counts
    row_count, col_count = data.shape

    # Step 2: Convert the CSV to a string
    csv_str = data.to_csv(index=False, header=False).strip()

    # Step 3: Encode the string with Base64 encryption
    csv_str_base64 = base64.b64encode(csv_str.encode("utf-8")).decode("utf-8")

    # Step 4: Combine the information
    input_string = f"{row_count},{col_count},{csv_str_base64}"

    return input_string


class EnergyForecastAPI(APIView):
    parser_classes = [MultiPartParser]  # To handle file uploads
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def validate_api_key(self, request):
        # Extract the API key from the Authorization header
        auth_header = get_authorization_header(request).decode("utf-8")
        if not auth_header.startswith("Api-Key "):
            raise AuthenticationFailed("Invalid API key format.")
        
        api_key = auth_header.split(" ")[1]
        
        # Validate the API key (TODO: implement database or hardcoded validation)
        valid_api_keys = ["n3v4$gb7b47g37vrv&@"]  # Replace with your API key logic
        if api_key not in valid_api_keys:
            raise AuthenticationFailed("Invalid API key.")
        
        return True

    def post(self, request, *args, **kwargs):

        try:
            # Validate the API key
            self.validate_api_key(request)

            snet_sdk = sdk.SnetSDK(config)

            org_id = "Photrek" # Organization ID
            service_id = "risk-aware-assessment" # Service ID
            group_name = "default_group"
            service_client = snet_sdk.create_service_client(org_id=org_id, service_id=service_id, group_name=group_name)

            # Check if a file is uploaded
            uploaded_file = request.FILES.get("file", None)
            print(uploaded_file)
            if not uploaded_file:
                return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                uploaded_file.seek(0)
                input_string = ingest_csv(uploaded_file)

                # Call the `adr` method
                photrek_response = service_client.call_rpc(
                    rpc_name="adr",
                    message_class="InputString",
                    s=input_string  # Pass the CSV data as a string
                )

                # Serialize the Protobuf response into a dictionary
                photrek_response_dict = {
                    "a": photrek_response.a,
                    "d": photrek_response.d,
                    "r": photrek_response.r,
                    "img": photrek_response.img,  # Base64-encoded string
                    "numr": photrek_response.numr,
                    "numc": photrek_response.numc,
                }

                # Return serialized response
                return Response(photrek_response_dict, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
