import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')
api_key = os.getenv('INSTANTDECO_API_KEY')

# Just test living_room which should definitely work
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

print("Testing living_room (should definitely work)...")

response = requests.post(
    'https://app.instantdeco.ai/api/1.1/wf/request_v2',
    json=payload,
    headers=headers,
    timeout=10
)

result = response.json()
print(f"Response: {result}")

if result.get('status') == 'success' and result.get('response', {}).get('status') == 'success':
    print("SUCCESS - living_room works!")
    print(f"Request ID: {result['response']['request_id']}")
else:
    print("FAILED - Even living_room doesn't work")
    print("There might be an issue with the API or our parameters")