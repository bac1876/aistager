"""
Automated InstantDecoAI Test
"""
import os
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv('.env.local')

INSTANTDECO_API_KEY = os.getenv('INSTANTDECO_API_KEY')
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')

print("="*60)
print("AUTOMATED INSTANTDECOAI TEST")
print("="*60)

# Create a webhook using webhook.site API
print("\nStep 1: Creating temporary webhook...")
webhook_response = requests.post('https://webhook.site/token')
if webhook_response.status_code == 201:
    webhook_data = webhook_response.json()
    webhook_token = webhook_data['uuid']
    webhook_url = f"https://webhook.site/{webhook_token}"
    print(f"[OK] Webhook created: {webhook_url}")
else:
    print("[ERROR] Failed to create webhook")
    exit(1)

# Test 1: Simple Unsplash image
print("\n" + "="*60)
print("TEST 1: Direct image URL (Unsplash)")
print("="*60)

test_image_1 = "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800"

payload_1 = {
    "design": "modern",
    "room_type": "living_room",
    "transformation_type": "furnish",
    "img_url": test_image_1,
    "webhook_url": webhook_url,
    "num_images": 1
}

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {INSTANTDECO_API_KEY}'
}

print("Sending request...")
response_1 = requests.post(
    'https://app.instantdeco.ai/api/1.1/wf/request_v2',
    headers=headers,
    json=payload_1
)

print(f"Status: {response_1.status_code}")
print(f"Response: {response_1.text[:200]}...")

request_id_1 = None
if response_1.status_code == 200:
    result = response_1.json()
    if result.get('status') == 'success':
        request_id_1 = result.get('response', {}).get('request_id')
        print(f"[SUCCESS] Request ID: {request_id_1}")

# Test 2: Upload Dropbox image to ImgBB first
print("\n" + "="*60)
print("TEST 2: Dropbox image via ImgBB")
print("="*60)

dropbox_url = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=1"

print("Downloading from Dropbox...")
img_response = requests.get(dropbox_url, timeout=30)
if img_response.status_code == 200:
    print("[OK] Downloaded")
    
    import base64
    image_base64 = base64.b64encode(img_response.content).decode('utf-8')
    
    print("Uploading to ImgBB...")
    imgbb_response = requests.post(
        'https://api.imgbb.com/1/upload',
        data={
            'key': IMGBB_API_KEY,
            'image': image_base64,
            'name': f'test_{int(time.time())}'
        }
    )
    
    if imgbb_response.status_code == 200 and imgbb_response.json().get('success'):
        imgbb_url = imgbb_response.json()['data']['url']
        print(f"[OK] Uploaded to: {imgbb_url}")
        
        payload_2 = {
            "design": "scandinavian",
            "room_type": "living_room",
            "transformation_type": "furnish",
            "block_element": "wall,floor,ceiling,windowpane,door",
            "img_url": imgbb_url,
            "webhook_url": webhook_url,
            "num_images": 1
        }
        
        print("Sending request...")
        response_2 = requests.post(
            'https://app.instantdeco.ai/api/1.1/wf/request_v2',
            headers=headers,
            json=payload_2
        )
        
        print(f"Status: {response_2.status_code}")
        print(f"Response: {response_2.text[:200]}...")
        
        if response_2.status_code == 200:
            result = response_2.json()
            if result.get('status') == 'success':
                request_id_2 = result.get('response', {}).get('request_id')
                print(f"[SUCCESS] Request ID: {request_id_2}")

# Wait and check webhook results
print("\n" + "="*60)
print("CHECKING WEBHOOK RESULTS")
print("="*60)
print("Waiting 10 seconds for initial results...")
time.sleep(10)

# Check webhook for results
webhook_check = requests.get(f'https://webhook.site/token/{webhook_token}/requests')
if webhook_check.status_code == 200:
    webhook_results = webhook_check.json()
    
    print(f"\nReceived {webhook_results.get('total', 0)} webhooks")
    
    if 'data' in webhook_results and webhook_results['data']:
        for i, webhook in enumerate(webhook_results['data'][:5]):  # Show first 5
            print(f"\nWebhook {i+1}:")
            try:
                content = json.loads(webhook.get('content', '{}'))
                print(f"  Status: {content.get('status')}")
                print(f"  Request ID: {content.get('request_id')}")
                print(f"  Output: {content.get('output')}")
            except:
                print(f"  Raw content: {webhook.get('content', '')[:100]}...")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
print(f"\nView all results at: {webhook_url}")
print("\nWaiting 30 more seconds for any remaining callbacks...")
time.sleep(30)

# Final check
webhook_final = requests.get(f'https://webhook.site/token/{webhook_token}/requests')
if webhook_final.status_code == 200:
    final_results = webhook_final.json()
    total = final_results.get('total', 0)
    print(f"\nFinal webhook count: {total}")
    
    if total > 0:
        print("\nSummary of results:")
        success_count = 0
        failed_count = 0
        
        for webhook in final_results.get('data', []):
            try:
                content = json.loads(webhook.get('content', '{}'))
                if content.get('status') == 'succeeded':
                    success_count += 1
                    print(f"✓ Success: {content.get('request_id')} -> {content.get('output', '')[:50]}...")
                else:
                    failed_count += 1
                    print(f"✗ Failed: {content.get('request_id')} -> {content.get('output', 'unknown error')}")
            except:
                pass
        
        print(f"\nTotal: {success_count} succeeded, {failed_count} failed")

print("\n" + "="*60)