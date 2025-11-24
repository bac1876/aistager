"""
Easy InstantDecoAI Test with Webhook.site
"""
import os
import requests
from dotenv import load_dotenv
import time
import webbrowser

load_dotenv('.env.local')

INSTANTDECO_API_KEY = os.getenv('INSTANTDECO_API_KEY')
INSTANTDECO_API_URL = 'https://app.instantdeco.ai/api/1.1/wf/request_v2'

print("="*60)
print("INSTANTDECOAI EASY TEST")
print("="*60)
print("\nThis will help you test InstantDecoAI virtual staging\n")

# Step 1: Open webhook.site
print("Step 1: Opening webhook.site in your browser...")
webbrowser.open('https://webhook.site')
time.sleep(3)

print("\nYou should see webhook.site in your browser now.")
print("Look for your unique URL at the top of the page.")
print("It will look like: https://webhook.site/a1b2c3d4-e5f6-7890")
print("\nCopy that URL and paste it here:")

webhook_url = input("Paste your webhook URL: ").strip()

if not webhook_url or "webhook.site" not in webhook_url:
    print("\n[ERROR] Invalid webhook URL. Please run the script again.")
    exit(1)

print(f"\n[OK] Using webhook URL: {webhook_url}")

# Test configurations
test_image = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=1"

print("\n" + "="*60)
print("TESTING VIRTUAL STAGING")
print("="*60)
print(f"Image: Empty living room")
print(f"Transformation: Furnish (adds furniture)")
print(f"Styles to test: Modern, Scandinavian, Minimalist")
print("="*60)

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {INSTANTDECO_API_KEY}'
}

# Test different styles
styles = ["modern", "scandinavian", "minimalist"]
request_ids = []

for i, style in enumerate(styles, 1):
    print(f"\nTest {i}/3: {style.capitalize()} style")
    
    payload = {
        "design": style,
        "room_type": "living_room",
        "transformation_type": "furnish",
        "block_element": "wall,floor,ceiling,windowpane,door",
        "img_url": test_image,
        "webhook_url": webhook_url,
        "num_images": 2  # Get 2 variations of each style
    }
    
    print("Sending request...")
    
    try:
        response = requests.post(
            INSTANTDECO_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                request_id = result.get('response', {}).get('request_id')
                request_ids.append((style, request_id))
                print(f"[SUCCESS] Request ID: {request_id}")
            else:
                print(f"[ERROR] API returned: {result}")
        else:
            print(f"[ERROR] HTTP {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] {str(e)}")
    
    if i < len(styles):
        print("Waiting 3 seconds before next style...")
        time.sleep(3)

print("\n" + "="*60)
print("ALL REQUESTS SENT!")
print("="*60)
print("\nNow check your webhook.site page!")
print(f"URL: {webhook_url}")
print("\nYou should see incoming webhooks with:")
print("- 'status': 'succeeded'")
print("- 'output': URL of the staged image")
print("\nProcessing usually takes 30-60 seconds per request.")
print("\nRequest IDs for reference:")
for style, req_id in request_ids:
    print(f"- {style}: {req_id}")

print("\n" + "="*60)
print("WHAT TO LOOK FOR:")
print("="*60)
print("1. Each webhook will have an 'output' field with the image URL")
print("2. Click on the image URLs to see the staged rooms")
print("3. Compare how different styles look")
print("4. Each style should produce 2 variations")
print("\nTotal expected images: 6 (3 styles × 2 variations)")
print("="*60)

# Keep the webhook page reference
print("\nPress Enter to open webhook.site again to check results...")
input()
webbrowser.open(webhook_url)