import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
print("Testing Replicate API Key...")
print(f"Key loaded: {'Yes' if REPLICATE_API_TOKEN else 'No'}")

# Test the API
headers = {
    'Authorization': f'Token {REPLICATE_API_TOKEN}',
}

response = requests.get('https://api.replicate.com/v1/account', headers=headers)
print(f"\nAPI Response: {response.status_code}")

if response.status_code == 200:
    print("SUCCESS! Your API key is working correctly.")
    data = response.json()
    print(f"Account username: {data.get('username', 'N/A')}")
else:
    print(f"ERROR: {response.status_code}")