import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')
API_KEY = os.getenv('REIMAGINEHOME_API_KEY')

headers = {'api-key': API_KEY}

print("Checking valid design themes...")
print("=" * 60)

# According to the docs, there should be a Get Design Theme List API
# Let's try to find it
endpoints = [
    '/v1/get-design-theme-list',
    '/v1/design-themes',
    '/v1/themes',
    '/v1/styles'
]

for endpoint in endpoints:
    url = f'https://api.reimaginehome.ai{endpoint}'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print(f"\n[OK] Found endpoint: {endpoint}")
        print(f"Response: {response.json()}")
        break
    else:
        print(f"{endpoint}: {response.status_code}")

# Also test without design_theme
print("\n\nTesting generation without design_theme...")

# Use the successful mask from previous test
generation_payload = {
    'image_url': "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
    'mask_urls': ["https://cdn.reimaginehome.ai/prod/mask/b552d509-df57-48d8-a734-9276b5a75629_segment.png"],
    'mask_category': 'furnishing',
    'space_type': 'ST-INT-011',
    'generation_count': 1
}

response = requests.post(
    'https://api.reimaginehome.ai/v1/generate_image',
    headers=headers,
    json=generation_payload
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"[OK] Success! Job ID: {result.get('job_id')}")
else:
    print(f"Error: {response.text}")