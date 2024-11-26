import os
import requests

# Define the API endpoint
API_URL = "http://127.0.0.1:8000/snet/energy-forecast/"  # Replace with your actual endpoint
API_KEY = "EQq22/s2o9EaXKTJ8EFbKxfoTTuW"
headers = {
    "X-API-KEY": API_KEY
}

# Path to the CSV file (ensure it's in the same directory as this script)
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), "energy_consumption.csv")

# Check if the CSV file exists
if not os.path.exists(CSV_FILE_PATH):
    print(f"Error: File '{CSV_FILE_PATH}' not found.")
    exit()

# Read and send the CSV file
# try:
with open(CSV_FILE_PATH, "rb") as file:
    # Send POST request with the file
    response = requests.post(
        API_URL,
        files={"file": file},  # Attach the file in the request
        headers=headers,
    )

# Print the response from the API
print("Response Status Code:", response.content)
print("Response JSON:", response.json())

# except requests.exceptions.RequestException as e:
#     print(f"An error occurred: {e}")

