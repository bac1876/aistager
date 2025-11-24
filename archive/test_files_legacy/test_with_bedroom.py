import os
import requests
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv('.env.local')

api_key = os.getenv('INSTANTDECO_API_KEY')
imgbb_key = os.getenv('IMGBB_API_KEY')

# Using a test bedroom image URL that's already uploaded
# This is a typical empty bedroom similar to what you showed
test_bedroom_url = "https://i.ibb.co/QXbFtxZ/empty-bedroom.jpg"

print("=== Testing InstantDeco with Bedroom Image ===")

# Test 1: As bedroom with prompt
payload = {
    "transformation_type": "furnish",
    "img_url": test_bedroom_url,
    "room_type": "living_room",  # API only supports this
    "design": "contemporary",
    "prompt": "contemporary bedroom with queen size bed, two nightstands with lamps, dresser, bedroom decor, area rug",
    "block_element": "wall,ceiling,floor,windowpane,door",
    "num_images": 1,
    "webhook_url": "https://webhook.site/test"
}

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

print("\nTest 1: Bedroom with Contemporary design")
print(f"Using prompt: {payload['prompt']}")

try:
    response = requests.post(
        'https://app.instantdeco.ai/api/1.1/wf/request_v2',
        json=payload,
        headers=headers,
        timeout=10
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
    
    # Try to parse as JSON
    try:
        result = response.json()
        print(f"JSON Response: {result}")
        
        if result.get('status') == 'success':
            print("\n✓ SUCCESS - Request submitted!")
            print(f"Request ID: {result.get('response', {}).get('request_id')}")
        else:
            print(f"\n✗ API Error: {result}")
    except:
        # Not JSON - probably HTML error
        print("\n✗ Non-JSON response (likely rate limit or error page)")
        print(f"Response preview: {response.text[:200]}...")
        if "Request Ent" in response.text:
            print("\nThis is the 'Request Entity Too Large' error")
        
except Exception as e:
    print(f"\nERROR: {e}")

# Wait before next test
print("\nWaiting 35 seconds before dining room test...")
time.sleep(35)

# Test 2: Dining room
print("\n" + "="*50)
print("Test 2: Dining Room")

payload2 = {
    "transformation_type": "furnish", 
    "img_url": test_bedroom_url,  # Using same image
    "room_type": "living_room",
    "design": "traditional",
    "prompt": "elegant dining room with large dining table, eight chairs, chandelier, buffet cabinet, dining room decor",
    "block_element": "wall,ceiling,floor,windowpane,door",
    "num_images": 1,
    "webhook_url": "https://webhook.site/test"
}

print(f"Using prompt: {payload2['prompt']}")

try:
    response = requests.post(
        'https://app.instantdeco.ai/api/1.1/wf/request_v2',
        json=payload2,
        headers=headers,
        timeout=10
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    try:
        result = response.json()
        print(f"JSON Response: {result}")
    except:
        print("Non-JSON response - this is the error you're seeing!")
        print(f"Response starts with: {response.text[:100]}...")
        
except Exception as e:
    print(f"\nERROR: {e}")