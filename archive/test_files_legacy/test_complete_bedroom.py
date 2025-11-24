import os
import requests
from dotenv import load_dotenv
import time
import json

# Load environment variables
load_dotenv('.env.local')

api_key = os.getenv('INSTANTDECO_API_KEY')

# Use a unique webhook URL - you should create your own at webhook.site
webhook_url = "https://webhook.site/6d5e5c8f-7b3a-4e8f-9f2a-3c4d5e6f7a8b"  # Replace with your webhook.site URL

print("=== Complete Bedroom Test ===")
print("\nIMPORTANT: Go to https://webhook.site and get your unique URL")
print("Replace the webhook_url in this script with your URL\n")

# Test image (empty room)
test_image = "https://i.ibb.co/7JpPyMb/test-image.jpg"

# Test with bedroom prompt
payload = {
    "transformation_type": "furnish",
    "img_url": test_image,
    "room_type": "living_room",  # API only supports this
    "design": "modern",
    "prompt": "modern bedroom with queen size bed, two nightstands with lamps, dresser, bedroom decor",
    "block_element": "wall,ceiling,floor,windowpane,door",
    "num_images": 1,
    "webhook_url": webhook_url
}

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

print("Sending request with bedroom prompt...")
print(f"Prompt: {payload['prompt']}")

try:
    response = requests.post(
        'https://app.instantdeco.ai/api/1.1/wf/request_v2',
        json=payload,
        headers=headers,
        timeout=10
    )
    
    result = response.json()
    print(f"\nResponse: {json.dumps(result, indent=2)}")
    
    if result.get('status') == 'success' and result.get('response', {}).get('status') == 'success':
        request_id = result['response']['request_id']
        print(f"\nSuccess! Request ID: {request_id}")
        print(f"\nNow check your webhook URL for results:")
        print(f"{webhook_url}")
        print("\nResults should appear within 30-60 seconds")
        print("\nThe result will show if the bedroom prompt worked correctly")
    else:
        print(f"\nFailed: {result}")
        
except Exception as e:
    print(f"\nERROR: {e}")

print("\n" + "="*50)
print("To test with your bedroom image:")
print("1. Upload your image to https://imgbb.com")
print("2. Replace test_image URL in this script")
print("3. Get your own webhook URL from https://webhook.site")
print("4. Run the script and check webhook for results")