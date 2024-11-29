import os
import requests

# Define the API endpoint
API_URL = "https://djangoapp.vveeq17939eno.us-east-2.cs.amazonlightsail.com/snet/energy-forecast/"
API_KEY = "EQq22/s2o9EaXKTJ8EFbKxfoTTuW"  
api_key = "n3v4$gb7b47g37vrv&@"

headers = {
    "X-API-KEY": API_KEY,
    "Authorization": f"Api-Key {api_key}"
}

def test_energy_forecast_api(csv_file_path: str) -> dict:
    """
    Test the energy forecast API with a given CSV file.

    Args:
        csv_file_path (str): The path to the CSV file to upload.

    Returns:
        dict: The JSON response from the API or an error message.
    """
    # Ensure the file exists
    if not os.path.exists(csv_file_path):
        return {"error": f"File '{csv_file_path}' not found."}

    try:
        with open(csv_file_path, "rb") as file:
            # Send the POST request to the API
            response = requests.post(
                API_URL,
                files={"file": file},
                headers=headers,
            )

        # Check if the response is successful
        if response.status_code == 200:
            return response.json()  # Return the parsed JSON response
        else:
            return {
                "error": f"Error {response.status_code}: {response.json().get('error', 'Unknown error')}",
                "raw_response": response.content.decode("utf-8")  # Include raw content for debugging
            }

    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred: {e}"}


# Test the API
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), "energy_consumption.csv")
result = test_energy_forecast_api(CSV_FILE_PATH)
print(result)  # Replace this with logging if needed
