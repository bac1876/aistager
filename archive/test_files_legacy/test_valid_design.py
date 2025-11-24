import requests
import os
from dotenv import load_dotenv

load_dotenv('.env.local')
api_key = os.getenv('INSTANTDECO_API_KEY')

# Test with a definitely valid design from the docs
payload = {
    "design": "modern",  # Valid per docs
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

print("Testing with valid 'modern' design style...")
response = requests.post(
    'https://app.instantdeco.ai/api/1.1/wf/request_v2',
    json=payload,
    headers=headers
)

result = response.json()
print(f"Response: {result}")

if result.get('status') == 'success' and result.get('response', {}).get('status') == 'success':
    print("\nSUCCESS - 'modern' design style works!")
    print("The issue was using 'contemporary' which is not in the API's valid list")
else:
    print("\nFAILED - Something else is wrong")