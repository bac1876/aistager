import os
import requests
import time
import base64
from dotenv import load_dotenv

load_dotenv('.env.local')
API_KEY = os.getenv('REIMAGINEHOME_API_KEY')

headers = {'api-key': API_KEY}

print("Testing ReimagineHome API - Simple Staging Approach")
print("=" * 60)

# Test different endpoints that might exist
endpoints = [
    '/v1/staging',
    '/v1/stage',
    '/v1/transform',
    '/v1/redesign',
    '/v1/furnish',
    '/v1/virtual-staging',
    '/v1/process'
]

# Simple test payload
test_payload = {
    "image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
    "style": "modern",
    "room_type": "living room"
}

print("\nTesting simple staging endpoints...")
for endpoint in endpoints:
    url = f"https://api.reimaginehome.ai{endpoint}"
    
    # Try POST
    response = requests.post(url, headers=headers, json=test_payload, timeout=5)
    
    if response.status_code == 200:
        print(f"\n[OK] Found working endpoint: POST {endpoint}")
        result = response.json()
        print(f"Response: {result}")
        
        # If it returns a job_id, try to get the result
        if 'data' in result and 'job_id' in result.get('data', {}):
            job_id = result['data']['job_id']
            print(f"\nJob created: {job_id}")
            
            # Wait a bit
            time.sleep(3)
            
            # Try to get result
            status_response = requests.get(f"{url}/{job_id}", headers=headers)
            if status_response.status_code == 200:
                print(f"Status check successful: {status_response.json()}")
        break
    elif response.status_code == 422:
        print(f"\n{endpoint}: Validation error - {response.json().get('error_message', '')[:50]}")
    elif response.status_code == 404:
        print(f"\n{endpoint}: Not found")
    elif response.status_code == 405:
        print(f"\n{endpoint}: Method not allowed")

# Also test if there's a simple transform endpoint that works differently
print("\n\n" + "=" * 60)
print("Testing direct transformation approach...")

# Maybe it works more like a direct API without the mask workflow
simple_payloads = [
    {
        "url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
        "mode": "staging"
    },
    {
        "image": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
        "type": "furnish"
    },
    {
        "input_image": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
        "style": "modern",
        "action": "stage"
    }
]

for i, payload in enumerate(simple_payloads):
    print(f"\nTest {i+1}: {list(payload.keys())}")
    
    for endpoint in ['/v1/transform', '/v1/process', '/v1/stage']:
        response = requests.post(
            f"https://api.reimaginehome.ai{endpoint}",
            headers=headers,
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"[OK] Success with {endpoint}!")
            print(f"Response: {response.json()}")
            break
        elif response.status_code not in [404, 405]:
            print(f"{endpoint}: {response.status_code} - {response.text[:50]}")