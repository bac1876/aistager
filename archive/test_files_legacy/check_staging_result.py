import os
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv('.env.local')

REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
headers = {'api-key': REIMAGINEHOME_API_KEY}

print("Checking for staging results...")
print("=" * 60)

# Unfortunately, we don't have the actual job_id from the response
# Let's try to find the status endpoint pattern

# Based on the mask creation pattern, let's try similar endpoints
job_id = "Processing"  # This is what was shown in your screenshot

endpoints_to_try = [
    f'/v1/generate_image/{job_id}',
    f'/v1/image_status/{job_id}',
    f'/v1/status/{job_id}',
    f'/v1/jobs/{job_id}',
    '/v1/generate_image',  # Maybe GET returns recent jobs?
    '/v1/recent_jobs',
    '/v1/my_jobs'
]

for endpoint in endpoints_to_try:
    url = f'https://api.reimaginehome.ai{endpoint}'
    print(f"\nTrying: {endpoint}")
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check if this contains image URLs
            if 'data' in data:
                if 'output_urls' in data.get('data', {}):
                    print("\n🎉 FOUND YOUR STAGED IMAGE!")
                    print(f"URL: {data['data']['output_urls'][0]}")
                    break
                elif 'images' in data.get('data', {}):
                    print("\n🎉 FOUND YOUR STAGED IMAGE!")
                    print(f"URL: {data['data']['images'][0]}")
                    break
        except:
            print(f"Response: {response.text[:200]}")

# Also check if there's a list endpoint that shows recent jobs
print("\n\nChecking for list endpoints...")
list_endpoints = [
    '/v1/jobs',
    '/v1/images',
    '/v1/history',
    '/v1/recent'
]

for endpoint in list_endpoints:
    url = f'https://api.reimaginehome.ai{endpoint}'
    print(f"\nTrying: {endpoint}")
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            # Only print if there's actual data
            if data.get('data') and isinstance(data['data'], list) and len(data['data']) > 0:
                print("Found data! Recent jobs:")
                print(json.dumps(data, indent=2)[:500] + "...")
        except:
            pass