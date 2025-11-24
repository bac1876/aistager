import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
print(f"Testing ReimagineHome API Key: {API_KEY[:10]}...")

# Base API URL that responded with 405
base_url = "https://api.reimaginehome.ai"

# Test different HTTP methods on the endpoints
endpoints = [
    '/v1/staging',
    '/v1/generate', 
    '/v1/transform',
    '/v1/redesign',
    '/v1/create_mask',  # From the documentation
    '/v1/generate_image',  # Possible endpoint
    '/v1/image',
    '/v1',
    '/'
]

methods = ['GET', 'POST', 'PUT']

# Use the api-key header as shown in documentation
headers = {
    'api-key': API_KEY
}

print("\nTesting different HTTP methods and endpoints...")
print("=" * 60)

for endpoint in endpoints:
    url = base_url + endpoint
    print(f"\nEndpoint: {url}")
    
    for method in methods:
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=5)
            elif method == 'POST':
                # Try with minimal data
                response = requests.post(url, headers=headers, json={}, timeout=5)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json={}, timeout=5)
            
            if response.status_code == 200:
                print(f"  ✓ {method}: SUCCESS! Status {response.status_code}")
                print(f"    Response: {response.text[:200]}")
            elif response.status_code == 401:
                print(f"  ✗ {method}: 401 Unauthorized - {response.text[:100]}")
            elif response.status_code == 404:
                print(f"  - {method}: 404 Not Found")
            elif response.status_code == 405:
                print(f"  ! {method}: 405 Method Not Allowed")
            elif response.status_code == 422:
                print(f"  ? {method}: 422 Validation Error - {response.text[:100]}")
            else:
                print(f"  ? {method}: Status {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"  - {method}: Error - {str(e)[:50]}")

# Test the create_mask endpoint specifically as it's in the docs
print("\n" + "=" * 60)
print("Testing create_mask endpoint with proper payload...")

mask_payload = {
    "image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800"
}

response = requests.post(
    f"{base_url}/v1/create_mask",
    headers=headers,
    json=mask_payload
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

# Also try the homedesigns.ai endpoint with ReimagineHome key
print("\n" + "=" * 60)
print("Testing if ReimagineHome key works with homedesigns.ai...")

response = requests.post(
    "https://homedesigns.ai/api/v2/virtual_staging",
    headers={'api-key': API_KEY},
    data={
        'design_type': 'Interior',
        'design_style': 'Modern',
        'room_type': 'Living Room',
        'no_design': 1
    }
)

print(f"HomeDesigns.ai Status: {response.status_code}")
print(f"Response: {response.text[:200]}")