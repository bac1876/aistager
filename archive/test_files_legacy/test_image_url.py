import requests
import time
import os
from dotenv import load_dotenv

load_dotenv('.env.local')
api_key = os.getenv('INSTANTDECO_API_KEY')

print("=== Testing InstantDeco Image URL Issue ===\n")

# Submit a request
payload = {
    "design": "modern",
    "room_type": "living_room", 
    "transformation_type": "furnish",
    "block_element": "wall,floor,ceiling,windowpane,door",
    "img_url": "https://i.ibb.co/7JpPyMb/test-image.jpg",
    "webhook_url": "https://webhook.site/test",
    "num_images": 1
}

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

print("1. Submitting request to InstantDeco...")
response = requests.post(
    'https://app.instantdeco.ai/api/1.1/wf/request_v2',
    json=payload,
    headers=headers
)

result = response.json()
print(f"Response: {result}")

if result.get('status') == 'success' and result.get('response', {}).get('status') == 'success':
    request_id = result['response']['request_id']
    print(f"\nRequest ID: {request_id}")
    print("\n2. The webhook would receive something like:")
    print("{\n  'output': 'https://some-url.com/image.png',")
    print("  'status': 'succeeded',")
    print(f"  'request_id': '{request_id}'\n}}")
    
    print("\n3. The issue might be:")
    print("- The image URL from InstantDeco expires quickly")
    print("- The URL format is different than expected")
    print("- We're not storing/handling the URL correctly")
    
    print("\nTo debug this, we need to:")
    print("1. Check what URL format InstantDeco actually returns")
    print("2. Test if the URLs expire after a certain time")
    print("3. Verify our webhook is parsing the response correctly")