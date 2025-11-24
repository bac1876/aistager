import os
import requests
import base64
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv('.env.local')

REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')

print("Testing Direct Image Upload to ReimagineHome")
print("=" * 60)

headers = {'api-key': REIMAGINEHOME_API_KEY}

# Load a test image
test_url = "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800"
image_response = requests.get(test_url)
image_bytes = image_response.content
image_base64 = base64.b64encode(image_bytes).decode('utf-8')

print(f"Test image size: {len(image_bytes) / 1024:.1f} KB")

# Test 1: Try base64 in JSON body
print("\n1. Testing base64 image in JSON body...")
test_payloads = [
    {'image': image_base64},
    {'image_data': image_base64},
    {'image_base64': image_base64},
    {'file': image_base64},
    {'image': f'data:image/jpeg;base64,{image_base64}'},
]

for i, payload in enumerate(test_payloads):
    print(f"\n   Attempt {i+1}: Using key '{list(payload.keys())[0]}'")
    response = requests.post(
        'https://api.reimaginehome.ai/v1/create_mask',
        headers=headers,
        json=payload
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        error_msg = response.json().get('error_message', response.text[:100])
        print(f"   Error: {error_msg}")
    else:
        print("   SUCCESS! Direct base64 upload works!")
        break

# Test 2: Try multipart/form-data
print("\n2. Testing multipart/form-data upload...")
files = {'image': ('room.jpg', image_bytes, 'image/jpeg')}
response = requests.post(
    'https://api.reimaginehome.ai/v1/create_mask',
    headers={'api-key': REIMAGINEHOME_API_KEY},  # Don't include Content-Type
    files=files
)
print(f"   Status: {response.status_code}")
if response.status_code != 200:
    print(f"   Response: {response.text[:200]}")
else:
    print("   SUCCESS! Multipart upload works!")

# Test 3: Check for upload endpoint
print("\n3. Checking for upload endpoints...")
upload_endpoints = [
    '/v1/upload',
    '/v1/upload_image',
    '/v1/images/upload',
    '/api/upload',
    '/upload'
]

for endpoint in upload_endpoints:
    url = f'https://api.reimaginehome.ai{endpoint}'
    print(f"\n   Testing {endpoint}...")
    
    # Try POST with multipart
    files = {'image': ('room.jpg', image_bytes, 'image/jpeg')}
    response = requests.post(
        url,
        headers={'api-key': REIMAGINEHOME_API_KEY},
        files=files
    )
    print(f"   POST Status: {response.status_code}")
    
    if response.status_code == 405:
        # Try GET to see if endpoint exists
        response = requests.get(url, headers=headers)
        print(f"   GET Status: {response.status_code}")

# Test 4: Try the working URL method to confirm API is functioning
print("\n4. Confirming API works with URL (control test)...")
response = requests.post(
    'https://api.reimaginehome.ai/v1/create_mask',
    headers=headers,
    json={'image_url': test_url}
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print("   API is working correctly with URLs")

print("\n" + "=" * 60)
print("Summary:")
print("Check which upload method worked above.")
print("If none worked, the API might only accept URLs.")