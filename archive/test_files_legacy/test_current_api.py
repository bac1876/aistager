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

print("=== Testing Current /api/stage Endpoint ===\n")

# Create a small test image
img = Image.new('RGB', (100, 100), color='blue')
buffered = io.BytesIO()
img.save(buffered, format="JPEG")
img_base64 = base64.b64encode(buffered.getvalue()).decode()
test_image_data = f"data:image/jpeg;base64,{img_base64}"

# Test the current stage endpoint
try:
    response = requests.post(
        f"{RENDER_URL}/api/stage",
        json={
            "image": test_image_data,
            "space_type": "ST-INT-011",  # Living Room
            "design_theme": ""
        },
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print("\nResponse:")
    
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text[:1000])
        
except requests.exceptions.Timeout:
    print("✗ Request timed out (30s)")
except requests.exceptions.ConnectionError as e:
    print(f"✗ Connection error: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {type(e).__name__}: {e}")

print("\n=== Testing with real image URL ===\n")

# Try with a known working image URL
try:
    response = requests.post(
        f"{RENDER_URL}/api/stage",
        json={
            "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800",
            "space_type": "ST-INT-011",
            "design_theme": ""
        },
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text[:1000])
        
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")