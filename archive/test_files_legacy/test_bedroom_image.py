import os
import base64
import requests
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv('.env.local')

# Get API keys
instantdeco_key = os.getenv('INSTANTDECO_API_KEY')
imgbb_key = os.getenv('IMGBB_API_KEY')

print("=== Testing Bedroom Image with InstantDeco ===")
print(f"InstantDeco API Key: {instantdeco_key[:10]}...")
print(f"ImgBB API Key: {imgbb_key[:10]}...")

# First, I'll use a test image URL since I can't access your local file
# You can replace this with your image after uploading to ImgBB
test_image_url = "https://i.ibb.co/7JpPyMb/test-image.jpg"

# Test 1: Living room (should work)
print("\n--- Test 1: Living Room ---")
payload1 = {
    "transformation_type": "furnish",
    "img_url": test_image_url,
    "room_type": "living_room",
    "design": "modern",
    "block_element": "wall,ceiling,floor,windowpane,door",
    "num_images": 1,
    "webhook_url": "https://webhook.site/test"
}

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {instantdeco_key}'
}

try:
    response = requests.post(
        'https://app.instantdeco.ai/api/1.1/wf/request_v2',
        json=payload1,
        headers=headers,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"ERROR: {e}")

# Wait to avoid rate limit
print("\nWaiting 35 seconds to avoid rate limit...")
time.sleep(35)

# Test 2: Bedroom with prompt
print("\n--- Test 2: Bedroom with Prompt ---")
payload2 = {
    "transformation_type": "furnish",
    "img_url": test_image_url,
    "room_type": "living_room",  # API only supports this
    "design": "modern",
    "prompt": "bedroom with bed, nightstands, dresser, bedroom furniture",
    "block_element": "wall,ceiling,floor,windowpane,door",
    "num_images": 1,
    "webhook_url": "https://webhook.site/test"
}

try:
    response = requests.post(
        'https://app.instantdeco.ai/api/1.1/wf/request_v2',
        json=payload2,
        headers=headers,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n=== Instructions for testing your image ===")
print("1. Upload your image to ImgBB:")
print("   - Go to https://imgbb.com/")
print("   - Upload your bedroom image")
print("   - Copy the direct link URL")
print("")
print("2. Replace 'test_image_url' in this script with your ImgBB URL")
print("")
print("3. Run this script again to test with your actual image")
print("")
print("4. Check https://webhook.site for the results (create a unique URL there)")