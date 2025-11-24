import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')
api_key = os.getenv('INSTANTDECO_API_KEY')

# Test bedroom with exact same parameters as living_room that worked
payload = {
    "design": "modern",
    "room_type": "bedroom",  # Only difference from working request
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

print("Testing bedroom with same parameters as working living_room...")
print(f"Room type: {payload['room_type']}")

response = requests.post(
    'https://app.instantdeco.ai/api/1.1/wf/request_v2',
    json=payload,
    headers=headers,
    timeout=10
)

result = response.json()
print(f"\nFull response: {result}")

# Let me also check the exact error
if result.get('response', {}).get('status') == 'error':
    print(f"\nError message: '{result['response']['message']}'")
    print("\nThis is very strange - bedroom should be supported according to the docs!")