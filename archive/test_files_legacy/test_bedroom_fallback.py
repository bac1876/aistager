import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

# Get API key
api_key = os.getenv('INSTANTDECO_API_KEY')

url = 'https://app.instantdeco.ai/api/1.1/wf/request_v2'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

# Test with regular bedroom
payload = {
    "transformation_type": "furnish",
    "img_url": "https://i.ibb.co/7JpPyMb/test-image.jpg",
    "room_type": "bedroom",  # Using generic bedroom
    "design": "traditional",
    "block_element": "wall,ceiling,floor,windowpane,door,animal,plant,vase,basket",
    "num_images": 1,
    "webhook_url": "https://aistager.vercel.app/api/webhook-receiver"
}

print("Testing with room_type = 'bedroom' + design = 'traditional'")
try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"ERROR: {e}")