import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')

INSTANTDECO_API_KEY = os.getenv('INSTANTDECO_API_KEY')
INSTANTDECO_API_URL = 'https://app.instantdeco.ai/api/1.1/wf/request_v2'

print("="*60)
print("INSTANTDECOAI API TEST")
print("="*60)

if not INSTANTDECO_API_KEY:
    print("[ERROR] INSTANTDECO_API_KEY not found in .env.local")
    print("\nPlease add your InstantDecoAI API key to .env.local:")
    print("INSTANTDECO_API_KEY=your_api_key_here")
    exit(1)

print(f"[OK] API Key configured: {INSTANTDECO_API_KEY[:10]}...")

# Test image (using the same dropbox URL)
test_image = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=1"

# Test webhook (you'll need to replace this)
test_webhook = "https://webhook.site/YOUR-UNIQUE-URL"  # Get from webhook.site

print("\nTest Configuration:")
print(f"- Image URL: {test_image}")
print(f"- Webhook URL: {test_webhook}")
print(f"- Transformation: furnish (virtual staging)")
print(f"- Room Type: living_room")
print(f"- Design Style: modern")

# Prepare test request
test_payload = {
    "design": "modern",
    "room_type": "living_room",
    "transformation_type": "furnish",
    "block_element": "wall,floor,ceiling,windowpane,door",
    "img_url": test_image,
    "webhook_url": test_webhook,
    "num_images": 2
}

print("\nSending test request...")

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {INSTANTDECO_API_KEY}'
}

try:
    response = requests.post(
        INSTANTDECO_API_URL,
        headers=headers,
        json=test_payload,
        timeout=30
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Body:")
    print(response.text)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            request_id = result.get('response', {}).get('request_id')
            print(f"\n[SUCCESS] Request ID: {request_id}")
            print(f"\n[IMPORTANT] Check {test_webhook} for results")
            print("\nThe staged images will be sent to your webhook URL")
            print("Processing usually takes 30-60 seconds")
        else:
            print(f"\n[ERROR] API returned error: {result}")
    else:
        print(f"\n[ERROR] HTTP Error: {response.status_code}")
        
except Exception as e:
    print(f"\n[ERROR] Error: {str(e)}")

print("\n" + "="*60)
print("NEXT STEPS:")
print("1. If you haven't already, go to https://webhook.site")
print("2. Copy your unique webhook URL")
print("3. Replace test_webhook in this script")
print("4. Run the script again")
print("5. Check webhook.site for the staged images")
print("="*60)