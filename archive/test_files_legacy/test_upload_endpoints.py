import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('.env.local')

REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
headers = {'api-key': REIMAGINEHOME_API_KEY}

print("Investigating ReimagineHome Upload Endpoints")
print("=" * 60)

# Test the upload endpoints with GET to see what they return
endpoints = ['/v1/upload', '/v1/upload_image']

for endpoint in endpoints:
    url = f'https://api.reimaginehome.ai{endpoint}'
    print(f"\nTesting GET {endpoint}...")
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text[:500]}")

# Test if these endpoints accept different methods
print("\n\nTesting different HTTP methods...")
methods = ['PUT', 'PATCH', 'OPTIONS']

for method in methods:
    print(f"\n{method} /v1/upload...")
    response = requests.request(
        method,
        'https://api.reimaginehome.ai/v1/upload',
        headers=headers
    )
    print(f"Status: {response.status_code}")

# Check if there's a presigned URL workflow
print("\n\nChecking for presigned URL endpoint...")
presigned_endpoints = [
    '/v1/get_upload_url',
    '/v1/presigned_url',
    '/v1/generate_upload_url'
]

for endpoint in presigned_endpoints:
    url = f'https://api.reimaginehome.ai{endpoint}'
    print(f"\nTesting {endpoint}...")
    
    # Try GET
    response = requests.get(url, headers=headers)
    print(f"GET Status: {response.status_code}")
    
    # Try POST
    response = requests.post(url, headers=headers, json={})
    print(f"POST Status: {response.status_code}")
    if response.status_code < 500:
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text[:200]}")