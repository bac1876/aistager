"""
Simple InstantDecoAI Test with Direct Image URL
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')

if len(sys.argv) < 2:
    print("\nUsage: python test_instantdeco_simple.py YOUR_WEBHOOK_URL")
    print("Get webhook URL from: https://webhook.site\n")
    sys.exit(1)

webhook_url = sys.argv[1]
INSTANTDECO_API_KEY = os.getenv('INSTANTDECO_API_KEY')

# Use a simple, direct image URL (public test image)
# This is a living room image from Unsplash
test_image_url = "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800"

print("Testing InstantDecoAI with simple, direct image URL")
print("="*60)
print(f"Image: {test_image_url}")
print(f"Webhook: {webhook_url}")
print("="*60)

# Minimal payload - only required fields
payload = {
    "design": "modern",
    "room_type": "living_room",
    "transformation_type": "furnish",
    "img_url": test_image_url,
    "webhook_url": webhook_url
}

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {INSTANTDECO_API_KEY}'
}

print("\nSending minimal request (no optional parameters)...")
print("Payload:", payload)

response = requests.post(
    'https://app.instantdeco.ai/api/1.1/wf/request_v2',
    headers=headers,
    json=payload
)

print(f"\nStatus Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    result = response.json()
    if result.get('status') == 'success':
        request_id = result.get('response', {}).get('request_id')
        print(f"\n[SUCCESS] Request ID: {request_id}")
        print(f"\nCheck {webhook_url} for results")
    else:
        print(f"\n[FAILED] Response: {result}")
else:
    print(f"\n[ERROR] HTTP {response.status_code}")

# Also test if the issue is with the Dropbox URL format
print("\n" + "="*60)
print("TROUBLESHOOTING TIPS:")
print("="*60)
print("If this test works but Dropbox URL fails:")
print("- The issue is with Dropbox URL accessibility")
print("- Solution: Always upload to ImgBB first")
print("")
print("If this test also fails:")
print("- Check API key is correct")
print("- Verify webhook URL is valid")
print("- Check InstantDecoAI service status")
print("="*60)