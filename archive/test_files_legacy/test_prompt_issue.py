import os
import requests
from dotenv import load_dotenv
import json

load_dotenv('.env.local')
api_key = os.getenv('INSTANTDECO_API_KEY')

# Test if prompt field causes "Wrong request" error
base_payload = {
    "transformation_type": "furnish",
    "img_url": "https://i.ibb.co/7JpPyMb/test-image.jpg",
    "room_type": "living_room",
    "design": "modern",
    "block_element": "wall,ceiling,floor,windowpane,door",
    "num_images": 1,
    "webhook_url": "https://webhook.site/test"
}

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

print("Testing with prompt field...")
payload_with_prompt = base_payload.copy()
payload_with_prompt['prompt'] = 'bedroom furniture'

response = requests.post(
    'https://app.instantdeco.ai/api/1.1/wf/request_v2',
    json=payload_with_prompt,
    headers=headers,
    timeout=10
)

result = response.json()
print(f"Result with prompt: {result}")

if result.get('response', {}).get('message') == 'Wrong request':
    print("\nThe 'prompt' field is causing the 'Wrong request' error!")
    print("InstantDeco API does NOT support custom prompts.")