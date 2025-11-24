import os
import requests
from dotenv import load_dotenv
import time
import json
import base64

load_dotenv('.env.local')

print("="*60)
print("INSTANTDECOAI WEBHOOK TEST WITH MONITORING")
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
    print("Sending request to Flask app...")
    response = requests.post(
        'http://localhost:5000/api/stage',
        json=payload,
        timeout=60  # Increased timeout
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n[SUCCESS] Flask app response:")
        print(json.dumps(result, indent=2))
        
        if result.get('success'):
            request_id = result.get('request_id')
            print(f"\n[OK] Request ID: {request_id}")
            print(f"[OK] Webhook URL sent to InstantDeco: {result.get('webhook_url')}")
            print("\nMonitoring for webhook calls...")
            print("This typically takes 30-60 seconds...")
            
            # Monitor for webhook results
            start_time = time.time()
            check_count = 0
            
            while time.time() - start_time < 180:  # 3 minute timeout
                check_count += 1
                time.sleep(10)
                
                elapsed = int(time.time() - start_time)
                print(f"\n[{elapsed}s] Checking for webhook... (check #{check_count})")
                
                try:
                    # Check recent stagings
                    stagings_response = requests.get('http://localhost:5000/api/recent-stagings')
                    if stagings_response.status_code == 200:
                        stagings = stagings_response.json()
                        
                        # Look for our request
                        for staging in stagings.get('stagings', []):
                            if staging.get('request_id') == request_id:
                                print(f"Found staging: Status={staging.get('status')}, Webhook={staging.get('webhook_received')}")
                                
                                if staging.get('webhook_received'):
                                    print(f"\n[SUCCESS] WEBHOOK RECEIVED!")
                                    print(f"Webhook timestamp: {staging.get('webhook_timestamp')}")
                                    print(f"Status: {staging.get('status')}")
                                    
                                    if staging.get('output_images'):
                                        print(f"\nGenerated {len(staging['output_images'])} images:")
                                        for idx, img in enumerate(staging['output_images'], 1):
                                            print(f"  Image {idx}: {img}")
                                    else:
                                        print("No output images found in webhook data")
                                    
                                    print("\n" + "="*60)
                                    print("WEBHOOK TEST SUCCESSFUL!")
                                    print("="*60)
                                    exit(0)
                                elif staging.get('status') == 'error':
                                    print(f"\n[ERROR] Staging failed: {staging.get('error')}")
                                    exit(1)
                                    
                except Exception as e:
                    print(f"Error checking stagings: {e}")
                    
            print(f"\n[TIMEOUT] No webhook received after {int(time.time() - start_time)} seconds")
            print("This could mean:")
            print("1. InstantDeco is still processing (can take up to 2 minutes)")
            print("2. Webhook URL is not reachable from InstantDeco's servers")
            print("3. There was an error in the generation")
            
    else:
        print(f"[ERROR] Flask app returned {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"[ERROR] Request failed: {str(e)}")

print("\n" + "="*60)