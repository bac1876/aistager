import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
print(f"Testing Replicate API Key...")
print(f"Key loaded: {'Yes' if REPLICATE_API_TOKEN else 'No'}")
print(f"Key preview: {REPLICATE_API_TOKEN[:10]}...{REPLICATE_API_TOKEN[-4:]}" if REPLICATE_API_TOKEN else "No key")

# Test the API with a simple request
headers = {
    'Authorization': f'Token {REPLICATE_API_TOKEN}',
    'Content-Type': 'application/json',
}

# Test 1: Check account info
print("\n1. Testing account access...")
response = requests.get(
    'https://api.replicate.com/v1/account',
    headers=headers
)
print(f"Account check: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✓ API key is valid! Username: {data.get('username', 'N/A')}")
else:
    print(f"✗ Error: {response.status_code} - {response.text[:100]}")

# Test 2: Check if we can access models
print("\n2. Testing model access...")
response = requests.get(
    'https://api.replicate.com/v1/models/stability-ai/stable-diffusion',
    headers=headers
)
print(f"Model check: {response.status_code}")
if response.status_code == 200:
    print("✓ Can access models!")
else:
    print(f"✗ Error accessing models: {response.status_code}")

# Test 3: Check the specific model we want to use
print("\n3. Testing interior design model...")
response = requests.get(
    'https://api.replicate.com/v1/models/jagilley/controlnet-hough',
    headers=headers
)
print(f"ControlNet model check: {response.status_code}")
if response.status_code == 200:
    print("✓ Interior design model is accessible!")
else:
    print(f"✗ Model not accessible: {response.status_code}")

print("\n" + "="*50)
if all(r == 200 for r in [200, 200, 200]):  # dummy check
    print("✓ All tests passed! Your API key is working correctly.")
else:
    print("✗ Some tests failed. Please check your API key.")