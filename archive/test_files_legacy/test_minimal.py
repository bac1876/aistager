import os
import requests
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv('.env.local')

api_key = os.getenv('INSTANTDECO_API_KEY')

print("=== Testing Minimal InstantDeco Request ===")

# Start with the absolute minimum that worked before
payload = {
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

print("\nTesting basic request (no prompt)...")
print(f"Payload: {json.dumps(payload, indent=2)}")

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
        print("\n✓ Basic request works!")
        
        # Now test with prompt
        print("\n" + "="*50)
        print("Now testing with prompt field...")
        
        payload_with_prompt = payload.copy()
        payload_with_prompt['prompt'] = 'bedroom furniture'
        
        response2 = requests.post(
            'https://app.instantdeco.ai/api/1.1/wf/request_v2',
            json=payload_with_prompt,
            headers=headers,
            timeout=10
        )
        
        result2 = response2.json()
        print(f"\nResponse with prompt: {json.dumps(result2, indent=2)}")
        
    else:
        print("\n✗ Even basic request failed!")
        print("The API might be having issues or the key might be rate limited")
        
except Exception as e:
    print(f"\nERROR: {e}")

print("\n" + "="*50)
print("Checking our exact payload structure against their API...")