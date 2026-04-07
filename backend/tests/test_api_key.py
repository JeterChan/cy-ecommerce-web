import os

from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("BREVO_API_KEY")
print(f"Testing API Key: {api_key[:20]}..." if api_key else "No API Key found")

headers = {"accept": "application/json", "api-key": api_key}

response = requests.get("https://api.brevo.com/v3/account", headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
