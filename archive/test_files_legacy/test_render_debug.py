import requests
import json
import base64
from PIL import Image
import io
import sys

# Fix Unicode output on Windows
sys.stdout.reconfigure(encoding='utf-8')

# Your Render app URL
RENDER_URL = "https://aistager.onrender.com"

print("=== Testing Render Deployment ===\n")

# Test 1: Check if system-test endpoint exists (debug version indicator)
print("1. Testing system-test endpoint...")
try:
    response = requests.get(f"{RENDER_URL}/api/system-test", timeout=10)
    if response.status_code == 200:
        print("✓ Debug version is deployed!")
        print("System test results:")
        print(json.dumps(response.json(), indent=2))
    else:
        print("✗ Debug version NOT deployed - system-test endpoint not found")
        print(f"Status: {response.status_code}")
except Exception as e:
    print(f"✗ Error testing system-test: {e}")

print("\n" + "="*50 + "\n")

# Test 2: Check health endpoint
print("2. Testing health endpoint...")
try:
    response = requests.get(f"{RENDER_URL}/health", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Health check passed")
        print(f"API configured: {data.get('api_configured')}")
        print(f"Debug mode: {data.get('debug_mode', 'Not specified')}")
    else:
        print(f"✗ Health check failed: {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*50 + "\n")

# Test 3: Try staging with a small test image
print("3. Testing stage-debug endpoint with test image...")

# Create a small test image
img = Image.new('RGB', (100, 100), color='red')
buffered = io.BytesIO()
img.save(buffered, format="JPEG")
img_base64 = base64.b64encode(buffered.getvalue()).decode()
test_image_data = f"data:image/jpeg;base64,{img_base64}"

# Try the debug endpoint
try:
    response = requests.post(
        f"{RENDER_URL}/api/stage-debug",
        json={
            "image": test_image_data,
            "space_type": "ST-INT-011",
            "design_theme": ""
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print("Response received!")
        print(f"Success: {data.get('success')}")
        
        if not data.get('success'):
            print(f"Failed at step: {data.get('failed_step')}")
            print(f"Error: {data.get('error')}")
            
            if 'debug_info' in data:
                print("\nDebug Information:")
                print(json.dumps(data['debug_info'], indent=2))
            
            if 'error_details' in data:
                print("\nError Details:")
                print(json.dumps(data['error_details'], indent=2))
    else:
        print(f"✗ Request failed with status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except requests.exceptions.RequestException as e:
    print(f"✗ Request error: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")

print("\n" + "="*50 + "\n")

# Test 4: Check what endpoints are available
print("4. Checking available endpoints...")
test_endpoints = [
    "/api/stage-debug",
    "/api/stage-complete", 
    "/api/stage",
    "/api/debug-logs"
]

for endpoint in test_endpoints:
    try:
        response = requests.options(f"{RENDER_URL}{endpoint}", timeout=5)
        print(f"{endpoint}: {response.status_code}")
    except:
        print(f"{endpoint}: Not responding")

print("\n=== End of diagnostics ===")