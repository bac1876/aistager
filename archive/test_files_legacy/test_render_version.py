import requests
import json

print("=== Testing Render Version ===\n")

base_url = "https://aistager.onrender.com"

# Test 1: Check HTML content
print("1. Checking HTML content...")
try:
    response = requests.get(base_url)
    html = response.text
    
    if "<!-- Version: 2.0 Fixed -->" in html:
        print("✓ Found version 2.0 comment")
    else:
        print("✗ Version comment not found")
        
    if "Transform Your Rooms with AI" in html:
        print("✓ Correct subtitle found")
    else:
        print("✗ Wrong subtitle")
        
except Exception as e:
    print(f"Error: {e}")

# Test 2: Check available endpoints
print("\n2. Testing endpoints...")
endpoints = [
    ("/health", "GET"),
    ("/api/stage", "POST"),
    ("/api/stage-debug", "POST"),
    ("/upload-image", "POST"),
    ("/temp-image/test.jpg", "GET")
]

for endpoint, method in endpoints:
    try:
        if method == "GET":
            resp = requests.get(f"{base_url}{endpoint}", timeout=5)
        else:
            resp = requests.post(f"{base_url}{endpoint}", json={}, timeout=5)
        print(f"{endpoint}: {resp.status_code}")
    except:
        print(f"{endpoint}: Failed")

# Test 3: Try staging with correct endpoint
print("\n3. Testing staging endpoint...")
try:
    test_data = {
        "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg==",  # minimal valid image
        "space_type": "ST-INT-011",
        "design_theme": ""
    }
    
    resp = requests.post(f"{base_url}/api/stage", json=test_data, timeout=10)
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")