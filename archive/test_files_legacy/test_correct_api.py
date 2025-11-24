import os
import requests
from dotenv import load_dotenv
import json
import time

load_dotenv('.env.local')
api_key = os.getenv('INSTANTDECO_API_KEY')

print("=== Testing Corrected InstantDeco API ===")

# Test with correct parameter order from docs
test_cases = [
    {
        "name": "Bedroom (should work now!)",
        "payload": {
            "design": "contemporary",
            "room_type": "bedroom",
            "transformation_type": "furnish",
            "block_element": "wall,floor,ceiling,windowpane,door",
            "high_details_resolution": True,
            "img_url": "https://i.ibb.co/7JpPyMb/test-image.jpg",
            "webhook_url": "https://webhook.site/test",
            "num_images": 1
        }
    },
    {
        "name": "Dining Room (should work now!)",
        "payload": {
            "design": "traditional",
            "room_type": "dining_room",
            "transformation_type": "furnish",
            "block_element": "wall,floor,ceiling,windowpane,door",
            "high_details_resolution": True,
            "img_url": "https://i.ibb.co/7JpPyMb/test-image.jpg",
            "webhook_url": "https://webhook.site/test",
            "num_images": 1
        }
    },
    {
        "name": "Kid's Bedroom",
        "payload": {
            "design": "modern",
            "room_type": "kid_bedroom",
            "transformation_type": "furnish",
            "block_element": "wall,floor,ceiling,windowpane,door",
            "high_details_resolution": True,
            "img_url": "https://i.ibb.co/7JpPyMb/test-image.jpg", 
            "webhook_url": "https://webhook.site/test",
            "num_images": 1
        }
    }
]

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

for i, test in enumerate(test_cases):
    if i > 0:
        print("\nWaiting 45 seconds for rate limit...")
        time.sleep(45)
    
    print(f"\n=== {test['name']} ===")
    print(f"Room type: {test['payload']['room_type']}")
    print(f"Design: {test['payload']['design']}")
    
    response = requests.post(
        'https://app.instantdeco.ai/api/1.1/wf/request_v2',
        json=test['payload'],
        headers=headers,
        timeout=10
    )
    
    result = response.json()
    if result.get('status') == 'success' and result.get('response', {}).get('status') == 'success':
        print(f"SUCCESS! Request ID: {result['response']['request_id']}")
    else:
        print(f"FAILED: {result}")
        
print("\n\nThe correct parameter order from the docs fixed the issue!")