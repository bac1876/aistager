import os
import requests
from dotenv import load_dotenv
import time
import json

load_dotenv('.env.local')

print("="*60)
print("INSTANTDECOAI WEBHOOK TEST - LOCAL FLASK APP")
print("="*60)

# Check ngrok URL
try:
    ngrok_response = requests.get('http://localhost:4040/api/tunnels')
    tunnels = ngrok_response.json()
    ngrok_url = tunnels['tunnels'][0]['public_url']
    webhook_url = f"{ngrok_url}/api/webhook"
    print(f"[OK] Detected ngrok URL: {ngrok_url}")
    print(f"[OK] Using webhook URL: {webhook_url}")
except Exception as e:
    print(f"[ERROR] Could not detect ngrok URL: {e}")
    exit(1)

# Test image URL
test_image_url = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=1"

print("\nDownloading test image...")
try:
    img_response = requests.get(test_image_url)
    if img_response.status_code == 200:
        import base64
        image_base64 = base64.b64encode(img_response.content).decode('utf-8')
        image_data = f"data:image/jpeg;base64,{image_base64}"
        print("[OK] Image downloaded and encoded")
    else:
        print(f"[ERROR] Failed to download image: {img_response.status_code}")
        exit(1)
except Exception as e:
    print(f"[ERROR] Failed to download image: {e}")
    exit(1)

print("\nMaking staging request via local Flask app...")

# Make request through our Flask app
payload = {
    "image": image_data,
    "room_type": "living_room", 
    "design_style": "modern",
    "num_images": 2
}

try:
    response = requests.post(
        'http://localhost:5000/api/stage',
        json=payload,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n[SUCCESS] Flask app response:")
        print(json.dumps(result, indent=2))
        
        if result.get('status') == 'success':
            request_id = result.get('request_id')
            print(f"\n[OK] Request ID: {request_id}")
            print("\nNow monitoring for webhook calls...")
            print("This may take 30-60 seconds...")
            
            # Monitor recent stagings to see webhook results
            for i in range(12):  # Check for 2 minutes
                time.sleep(10)
                print(f"\nChecking for results... ({i+1}/12)")
                
                try:
                    stagings_response = requests.get('http://localhost:5000/api/recent-stagings')
                    if stagings_response.status_code == 200:
                        stagings = stagings_response.json()
                        
                        # Look for our request
                        for staging in stagings.get('stagings', []):
                            if staging.get('request_id') == request_id:
                                if staging.get('webhook_received'):
                                    print(f"\n[SUCCESS] Webhook received!")
                                    print(f"Status: {staging.get('status')}")
                                    if staging.get('output_images'):
                                        print(f"Generated images: {len(staging['output_images'])}")
                                        for idx, img in enumerate(staging['output_images'], 1):
                                            print(f"  Image {idx}: {img}")
                                    exit(0)
                                else:
                                    print(f"Status: {staging.get('status')} (no webhook yet)")
                except Exception as e:
                    print(f"Error checking stagings: {e}")
                    
            print("\n[TIMEOUT] No webhook received after 2 minutes")
            
    else:
        print(f"[ERROR] Flask app returned {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"[ERROR] Request failed: {str(e)}")

print("\n" + "="*60)