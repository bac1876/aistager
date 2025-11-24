import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('.env.local')

REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
headers = {'api-key': REIMAGINEHOME_API_KEY}

print("Testing Presigned URL Parameters")
print("=" * 60)

# Test with various parameters
params_list = [
    {},
    {'filename': 'room.jpg'},
    {'file_name': 'room.jpg'},
    {'name': 'room.jpg'},
    {'type': 'image/jpeg'},
    {'content_type': 'image/jpeg'},
    {'filename': 'room.jpg', 'content_type': 'image/jpeg'}
]

endpoints = ['/v1/get_upload_url', '/v1/presigned_url', '/v1/upload']

for endpoint in endpoints:
    print(f"\nTesting {endpoint}...")
    url = f'https://api.reimaginehome.ai{endpoint}'
    
    for params in params_list:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and data['data'] != {}:
                print(f"  Params: {params}")
                print(f"  Response: {json.dumps(data, indent=2)}")
                break

# Also test POST with JSON body
print("\n\nTesting POST with JSON body...")
for endpoint in endpoints:
    url = f'https://api.reimaginehome.ai{endpoint}'
    
    for body in params_list:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and data['data'] != {}:
                print(f"\n{endpoint} with body {body}:")
                print(f"Response: {json.dumps(data, indent=2)}")

# Check if the web interface uses a different domain or path
print("\n\nChecking other possible API paths...")
other_domains = [
    'https://www.reimaginehome.ai/api',
    'https://app.reimaginehome.ai/api',
    'https://reimaginehome.ai/api'
]

for domain in other_domains:
    print(f"\nTesting {domain}/upload...")
    try:
        response = requests.post(
            f'{domain}/upload',
            headers={'api-key': REIMAGINEHOME_API_KEY},
            timeout=3
        )
        print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"Error: {type(e).__name__}")