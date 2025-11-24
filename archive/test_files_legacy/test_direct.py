import os
import requests
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
print(f"API Token: {REPLICATE_API_TOKEN[:20]}...{REPLICATE_API_TOKEN[-10:]}")

# Test image (create a small test image)
test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
image_uri = f"data:image/png;base64,{test_image}"

headers = {
    'Authorization': f'Token {REPLICATE_API_TOKEN}',
    'Content-Type': 'application/json',
}

# Simple test with stable diffusion
payload = {
    "version": "ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",  # stable-diffusion
    "input": {
        "prompt": "a modern living room with furniture"
    }
}

print("\nCalling Replicate API...")
response = requests.post(
    'https://api.replicate.com/v1/predictions',
    headers=headers,
    json=payload
)

print(f"Response status: {response.status_code}")
if response.status_code == 201:
    data = response.json()
    print(f"Success! Prediction ID: {data['id']}")
    print(f"Status: {data['status']}")
else:
    print(f"Error: {response.text}")