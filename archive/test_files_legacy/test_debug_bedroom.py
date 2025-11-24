import os
import requests
from dotenv import load_dotenv
import json
import time

load_dotenv('.env.local')
api_key = os.getenv('INSTANTDECO_API_KEY')

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

print("=== Debugging Bedroom API Issue ===\n")

# Test different variations to find what works
test_cases = [
    {
        "name": "Test 1: Exact copy from API docs example",
        "payload": {
            "design": "scandinavian",
            "room_type": "living_room",
            "transformation_type": "furnish",
            "block_element": "wall,floor,ceiling,windowpane,door",
            "high_details_resolution": True,
            "img_url": "https://i.ibb.co/7JpPyMb/test-image.jpg",
            "webhook_url": "https://webhook.site/test",
            "num_images": 2
        }
    },
    {
        "name": "Test 2: Change only room_type to bedroom",
        "payload": {
            "design": "scandinavian",
            "room_type": "bedroom",
            "transformation_type": "furnish",
            "block_element": "wall,floor,ceiling,windowpane,door",
            "high_details_resolution": True,
            "img_url": "https://i.ibb.co/7JpPyMb/test-image.jpg",
            "webhook_url": "https://webhook.site/test",
            "num_images": 2
        }
    },
    {
        "name": "Test 3: Without high_details_resolution",
        "payload": {
            "design": "modern",
            "room_type": "bedroom",
            "transformation_type": "furnish",
            "block_element": "wall,floor,ceiling,windowpane,door",
            "img_url": "https://i.ibb.co/7JpPyMb/test-image.jpg",
            "webhook_url": "https://webhook.site/test",
            "num_images": 1
        }
    },
    {
        "name": "Test 4: Minimal bedroom request",
        "payload": {
            "design": "modern",
            "room_type": "bedroom",
            "transformation_type": "furnish",
            "img_url": "https://i.ibb.co/7JpPyMb/test-image.jpg",
            "webhook_url": "https://webhook.site/test",
            "num_images": 1
        }
    }
]

for i, test in enumerate(test_cases):
    if i > 0:
        print("\nWaiting 45 seconds...")
        time.sleep(45)
    
    print(f"\n{test['name']}")
    print(f"Payload: {json.dumps(test['payload'], indent=2)}")
    
    response = requests.post(
        'https://app.instantdeco.ai/api/1.1/wf/request_v2',
        json=test['payload'],
        headers=headers,
        timeout=10
    )
    
    result = response.json()
    print(f"Response: {result}")
    
    if result.get('status') == 'success' and result.get('response', {}).get('status') == 'success':
        print(">>> SUCCESS!")
    else:
        print(">>> FAILED")
        if result.get('response', {}).get('message') == 'Wrong request':
            # Try to understand what's wrong
            print(">>> Analyzing failure...")
            if i == 1:
                print(">>> Only difference from working request: room_type changed from 'living_room' to 'bedroom'")