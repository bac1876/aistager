import os
import requests
from dotenv import load_dotenv
import time

load_dotenv('.env.local')

INSTANTDECO_API_KEY = os.getenv('INSTANTDECO_API_KEY')
INSTANTDECO_API_URL = 'https://app.instantdeco.ai/api/1.1/wf/request_v2'

print("="*60)
print("INSTANTDECOAI WEBHOOK TEST")
print("="*60)

# INSTRUCTIONS
print("\nBEFORE RUNNING THIS TEST:")
print("1. Go to https://webhook.site")
print("2. Copy your unique webhook URL")
print("3. Replace the webhook_url variable below")
print("4. Run this script")
print("5. Watch webhook.site for results\n")

# REPLACE THIS WITH YOUR WEBHOOK.SITE URL
webhook_url = "https://webhook.site/YOUR-UNIQUE-ID-HERE"  # <-- CHANGE THIS!

if "YOUR-UNIQUE-ID-HERE" in webhook_url:
    print("[ERROR] Please replace the webhook URL with your actual webhook.site URL!")
    print("Example: https://webhook.site/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6")
    exit(1)

print(f"[OK] Using webhook URL: {webhook_url}")

# Test image
test_image = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=1"

# Test configurations to try
test_configs = [
    {
        "name": "Living Room - Modern",
        "payload": {
            "design": "modern",
            "room_type": "living_room",
            "transformation_type": "furnish",
            "block_element": "wall,floor,ceiling,windowpane,door",
            "img_url": test_image,
            "webhook_url": webhook_url,
            "num_images": 2
        }
    },
    {
        "name": "Living Room - Scandinavian",
        "payload": {
            "design": "scandinavian",
            "room_type": "living_room",
            "transformation_type": "furnish",
            "block_element": "wall,floor,ceiling,windowpane,door",
            "img_url": test_image,
            "webhook_url": webhook_url,
            "num_images": 2
        }
    }
]

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {INSTANTDECO_API_KEY}'
}

print(f"\nWill test {len(test_configs)} configurations\n")

for i, config in enumerate(test_configs, 1):
    print(f"Test {i}: {config['name']}")
    print("Sending request...")
    
    try:
        response = requests.post(
            INSTANTDECO_API_URL,
            headers=headers,
            json=config['payload'],
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                request_id = result.get('response', {}).get('request_id')
                print(f"[SUCCESS] Request ID: {request_id}")
            else:
                print(f"[ERROR] API returned: {result}")
        else:
            print(f"[ERROR] HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] {str(e)}")
    
    print()
    if i < len(test_configs):
        print("Waiting 5 seconds before next test...")
        time.sleep(5)

print("="*60)
print("CHECK YOUR WEBHOOK.SITE PAGE!")
print(f"URL: {webhook_url}")
print("\nYou should see webhook calls with staged images.")
print("The 'output' field will contain the image URL(s).")
print("\nProcessing usually takes 30-60 seconds.")
print("="*60)