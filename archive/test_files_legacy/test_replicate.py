import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
print(f"API Key loaded: {'Yes' if REPLICATE_API_TOKEN else 'No'}")
print(f"API Key (first 10 chars): {REPLICATE_API_TOKEN[:10]}..." if REPLICATE_API_TOKEN else "No API key")

# Test the API
headers = {
    'Authorization': f'Token {REPLICATE_API_TOKEN}',
    'Content-Type': 'application/json',
}

# Test with a simple model
response = requests.get(
    'https://api.replicate.com/v1/models/stability-ai/stable-diffusion',
    headers=headers
)

print(f"\nAPI Test Response: {response.status_code}")
if response.status_code == 200:
    print("✓ API key is valid and working!")
else:
    print("✗ API key issue:", response.text[:200])