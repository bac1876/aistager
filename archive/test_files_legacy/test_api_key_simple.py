import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

# Get API key
api_key = os.getenv('INSTANTDECO_API_KEY')
print(f"API Key: {api_key}")

if not api_key:
    print("ERROR: No API key found in .env.local")
    exit(1)

# Test the API with minimal payload
url = 'https://app.instantdeco.ai/api/1.1/wf/request_v2'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

payload = {
    "transformation_type": "furnish",
    "img_url": "https://i.ibb.co/7JpPyMb/test-image.jpg",
    "room_type": "living_room",
    "design": "modern",
    "block_element": "wall,ceiling,floor",
    "num_images": 1,
    "webhook_url": "https://webhook.site/test"
}

print("\nTesting InstantDeco API...")
print(f"URL: {url}")
print(f"Headers: {headers}")
print(f"Payload: {payload}")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"\nERROR: {e}")