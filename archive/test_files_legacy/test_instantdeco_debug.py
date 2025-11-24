"""
InstantDecoAI Debug Test - Handles image upload properly
"""
import os
import sys
import requests
import base64
import time
from dotenv import load_dotenv

load_dotenv('.env.local')

INSTANTDECO_API_KEY = os.getenv('INSTANTDECO_API_KEY')
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')

if len(sys.argv) < 2:
    print("="*60)
    print("INSTANTDECO DEBUG TEST")
    print("="*60)
    print("\nUsage: python test_instantdeco_debug.py YOUR_WEBHOOK_URL")
    print("\nThis script will:")
    print("1. Download the test image")
    print("2. Upload it to ImgBB") 
    print("3. Use the ImgBB URL for InstantDecoAI")
    print("="*60)
    sys.exit(1)

webhook_url = sys.argv[1]
print(f"Using webhook: {webhook_url}\n")

# Step 1: Download the Dropbox image
print("Step 1: Downloading test image from Dropbox...")
dropbox_url = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=1"

try:
    img_response = requests.get(dropbox_url, timeout=30)
    if img_response.status_code == 200:
        print("[OK] Image downloaded successfully")
        image_data = img_response.content
    else:
        print(f"[ERROR] Failed to download image: {img_response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Download failed: {e}")
    sys.exit(1)

# Step 2: Upload to ImgBB
print("\nStep 2: Uploading to ImgBB...")
try:
    # Convert to base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    imgbb_response = requests.post(
        'https://api.imgbb.com/1/upload',
        data={
            'key': IMGBB_API_KEY,
            'image': image_base64,
            'name': f'test_room_{int(time.time())}'
        },
        timeout=30
    )
    
    if imgbb_response.status_code == 200:
        imgbb_data = imgbb_response.json()
        if imgbb_data.get('success'):
            image_url = imgbb_data['data']['url']
            print(f"[OK] Image uploaded to: {image_url}")
        else:
            print(f"[ERROR] ImgBB upload failed: {imgbb_data}")
            sys.exit(1)
    else:
        print(f"[ERROR] ImgBB HTTP {imgbb_response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"[ERROR] Upload failed: {e}")
    sys.exit(1)

# Step 3: Test InstantDecoAI with the ImgBB URL
print("\nStep 3: Testing InstantDecoAI with ImgBB URL...")
print("="*60)
print("Request Details:")
print(f"- Image URL: {image_url}")
print(f"- Webhook URL: {webhook_url}")
print(f"- Room Type: living_room")
print(f"- Design: modern")
print(f"- Transformation: furnish")
print("="*60)

# Test different parameter combinations
test_configs = [
    {
        "name": "Test 1: Basic furnish request",
        "payload": {
            "design": "modern",
            "room_type": "living_room",
            "transformation_type": "furnish",
            "img_url": image_url,
            "webhook_url": webhook_url,
            "num_images": 1
        }
    },
    {
        "name": "Test 2: With block elements",
        "payload": {
            "design": "modern",
            "room_type": "living_room",
            "transformation_type": "furnish",
            "block_element": "wall,floor,ceiling,windowpane,door",
            "img_url": image_url,
            "webhook_url": webhook_url,
            "num_images": 1
        }
    },
    {
        "name": "Test 3: Different design (scandinavian)",
        "payload": {
            "design": "scandinavian",
            "room_type": "living_room",
            "transformation_type": "furnish",
            "img_url": image_url,
            "webhook_url": webhook_url,
            "num_images": 1
        }
    }
]

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {INSTANTDECO_API_KEY}'
}

for i, config in enumerate(test_configs):
    print(f"\n{config['name']}")
    print("-" * 40)
    
    # Show exact payload
    print("Payload:")
    for key, value in config['payload'].items():
        if key != 'img_url':  # Don't print long URL
            print(f"  {key}: {value}")
    
    print("\nSending request...")
    
    try:
        response = requests.post(
            'https://app.instantdeco.ai/api/1.1/wf/request_v2',
            headers=headers,
            json=config['payload'],
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text[:200]}...")  # First 200 chars
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                request_id = result.get('response', {}).get('request_id')
                print(f"[SUCCESS] Request ID: {request_id}")
            else:
                print(f"[ERROR] API returned: {result}")
        else:
            print(f"[ERROR] HTTP {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
    
    if i < len(test_configs) - 1:
        print("\nWaiting 5 seconds before next test...")
        time.sleep(5)

print("\n" + "="*60)
print("DEBUGGING COMPLETE")
print("="*60)
print(f"\nCheck your webhook at: {webhook_url}")
print("\nLook for:")
print("1. Which requests succeeded vs failed")
print("2. Any error messages in the webhook data")
print("3. Whether using ImgBB URL fixed the issue")
print("\nIf all requests failed, the issue might be:")
print("- API key problem")
print("- Parameter mismatch") 
print("- Service temporarily down")
print("="*60)