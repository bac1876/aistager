import os
import requests
from dotenv import load_dotenv
import time

load_dotenv('.env.local')
api_key = os.getenv('INSTANTDECO_API_KEY')

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

base_payload = {
    "transformation_type": "furnish",
    "img_url": "https://i.ibb.co/7JpPyMb/test-image.jpg",
    "room_type": "living_room",
    "design": "modern",
    "num_images": 1,
    "webhook_url": "https://webhook.site/test"
}

# Test different block_element combinations
test_cases = [
    {
        "name": "Basic blocks",
        "block_element": "wall,ceiling,floor,windowpane,door"
    },
    {
        "name": "With decorative blocks",
        "block_element": "wall,ceiling,floor,windowpane,door,animal,plant,vase,basket"
    }
]

for i, test in enumerate(test_cases):
    if i > 0:
        print("\nWaiting 35 seconds...")
        time.sleep(35)
        
    print(f"\n=== Test: {test['name']} ===")
    print(f"block_element: {test['block_element']}")
    
    payload = base_payload.copy()
    payload['block_element'] = test['block_element']
    
    response = requests.post(
        'https://app.instantdeco.ai/api/1.1/wf/request_v2',
        json=payload,
        headers=headers,
        timeout=10
    )
    
    result = response.json()
    if result.get('status') == 'success' and result.get('response', {}).get('status') == 'success':
        print("SUCCESS - Request accepted")
    else:
        print(f"FAILED: {result.get('response', {}).get('message', 'Unknown error')}")
        if result.get('response', {}).get('message') == 'Wrong request':
            print("This block_element configuration causes 'Wrong request' error!")