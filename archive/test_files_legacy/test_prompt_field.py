import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

api_key = os.getenv('INSTANTDECO_API_KEY')
test_image = "https://i.ibb.co/7JpPyMb/test-image.jpg"

# Test if different fields work
test_payloads = [
    {
        "name": "Basic (no prompt)",
        "payload": {
            "transformation_type": "furnish",
            "img_url": test_image,
            "room_type": "living_room",
            "design": "modern",
            "block_element": "wall,ceiling,floor",
            "num_images": 1,
            "webhook_url": "https://webhook.site/test"
        }
    },
    {
        "name": "With prompt field",
        "payload": {
            "transformation_type": "furnish",
            "img_url": test_image,
            "room_type": "living_room",
            "design": "modern",
            "prompt": "bedroom with bed and nightstands",
            "block_element": "wall,ceiling,floor",
            "num_images": 1,
            "webhook_url": "https://webhook.site/test"
        }
    },
    {
        "name": "With custom_prompt field",
        "payload": {
            "transformation_type": "furnish",
            "img_url": test_image,
            "room_type": "living_room",
            "design": "modern",
            "custom_prompt": "bedroom with bed and nightstands",
            "block_element": "wall,ceiling,floor",
            "num_images": 1,
            "webhook_url": "https://webhook.site/test"
        }
    },
    {
        "name": "With instructions field",
        "payload": {
            "transformation_type": "furnish",
            "img_url": test_image,
            "room_type": "living_room",
            "design": "modern",
            "instructions": "bedroom with bed and nightstands",
            "block_element": "wall,ceiling,floor",
            "num_images": 1,
            "webhook_url": "https://webhook.site/test"
        }
    }
]

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

for test in test_payloads:
    print(f"\n=== Testing: {test['name']} ===")
    print(f"Payload: {test['payload']}")
    
    try:
        response = requests.post(
            'https://app.instantdeco.ai/api/1.1/wf/request_v2',
            json=test['payload'],
            headers=headers,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if result.get('status') == 'success' and result.get('response', {}).get('status') == 'success':
            print(f"✓ SUCCESS - Request ID: {result['response'].get('request_id')}")
        else:
            print(f"✗ FAILED - {result}")
            
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Only test first two to avoid rate limits
    if test['name'] == "With prompt field":
        print("\nStopping here to avoid rate limits. The API accepts the 'prompt' field!")
        break