"""
Test InstantDecoAI Enhance Mode
This might preserve structure better than furnish mode
"""
import os
import sys
import requests
import time
from dotenv import load_dotenv

load_dotenv('.env.local')

if len(sys.argv) < 2:
    print("\nUsage: python test_enhance_mode.py YOUR_WEBHOOK_URL")
    sys.exit(1)

webhook_url = sys.argv[1]
INSTANTDECO_API_KEY = os.getenv('INSTANTDECO_API_KEY')

# Test image URL (using ImgBB from earlier test)
test_image = "https://i.ibb.co/LDw1Pwj6/room-1753222815.jpg"

print("Testing InstantDecoAI 'enhance' mode for structure preservation")
print("="*60)

# Test 1: Enhance mode
payload1 = {
    "design": "modern",
    "room_type": "living_room",
    "transformation_type": "enhance",  # Just enhance, don't transform
    "img_url": test_image,
    "webhook_url": webhook_url
}

# Test 2: Furnish with maximum block elements
payload2 = {
    "design": "modern", 
    "room_type": "living_room",
    "transformation_type": "furnish",
    "block_element": "wall,floor,ceiling,windowpane,door,window,sky,house,building,tree,car,roof,beam,column,kitchen,counter,countertop",
    "img_url": test_image,
    "webhook_url": webhook_url,
    "num_images": 1
}

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {INSTANTDECO_API_KEY}'
}

# Test enhance mode
print("\nTest 1: Enhance mode")
print("-" * 40)
response1 = requests.post(
    'https://app.instantdeco.ai/api/1.1/wf/request_v2',
    headers=headers,
    json=payload1
)
print(f"Status: {response1.status_code}")
if response1.status_code == 200:
    result = response1.json()
    if result.get('status') == 'success':
        print(f"Request ID: {result['response']['request_id']}")

time.sleep(5)

# Test maximum constraints
print("\nTest 2: Furnish with maximum block elements")
print("-" * 40)
response2 = requests.post(
    'https://app.instantdeco.ai/api/1.1/wf/request_v2',
    headers=headers,
    json=payload2
)
print(f"Status: {response2.status_code}")
if response2.status_code == 200:
    result = response2.json()
    if result.get('status') == 'success':
        print(f"Request ID: {result['response']['request_id']}")

print(f"\nCheck {webhook_url} to compare results")
print("\nLook for which mode better preserves the room structure")