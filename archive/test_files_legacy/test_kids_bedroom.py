import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

# Get API key
api_key = os.getenv('INSTANTDECO_API_KEY')
print(f"API Key: {api_key}")

# Test with Kid's Bedroom + Traditional
url = 'https://app.instantdeco.ai/api/1.1/wf/request_v2'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

# First test - same as what worked
payload1 = {
    "transformation_type": "furnish",
    "img_url": "https://i.ibb.co/7JpPyMb/test-image.jpg",
    "room_type": "living_room",
    "design": "modern",
    "block_element": "wall,ceiling,floor,windowpane,door,animal,plant,vase,basket",
    "num_images": 1,
    "webhook_url": "https://aistager.vercel.app/api/webhook-receiver"
}

print("\n=== Test 1: Living Room + Modern (should work) ===")
try:
    response = requests.post(url, json=payload1, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"ERROR: {e}")

# Second test - Kid's Bedroom + Traditional
payload2 = {
    "transformation_type": "furnish",
    "img_url": "https://i.ibb.co/7JpPyMb/test-image.jpg",
    "room_type": "kids_bedroom",  # Note: might need to be "kid_bedroom" or "children_bedroom"
    "design": "traditional",
    "block_element": "wall,ceiling,floor,windowpane,door,animal,plant,vase,basket",
    "num_images": 1,
    "webhook_url": "https://aistager.vercel.app/api/webhook-receiver"
}

print("\n=== Test 2: Kid's Bedroom + Traditional ===")
try:
    response = requests.post(url, json=payload2, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"ERROR: {e}")

# Try alternative room type names
for room_type in ["kid_bedroom", "children_bedroom", "child_bedroom"]:
    payload3 = payload2.copy()
    payload3["room_type"] = room_type
    
    print(f"\n=== Test 3: Trying room_type = '{room_type}' ===")
    try:
        response = requests.post(url, json=payload3, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"ERROR: {e}")