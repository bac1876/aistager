import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('.env.local')
API_KEY = os.getenv('REIMAGINEHOME_API_KEY')

headers = {'api-key': API_KEY}

print("Testing minimal payloads for generate_image...")
print("=" * 60)

# Different payload combinations
payloads = [
    {
        "name": "Just basics",
        "data": {
            "image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
            "generation_count": 1
        }
    },
    {
        "name": "With prompt only",
        "data": {
            "image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
            "prompt": "Modern living room",
            "generation_count": 1
        }
    },
    {
        "name": "With mask_category only",
        "data": {
            "image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
            "mask_category": "furnishing",
            "generation_count": 1
        }
    },
    {
        "name": "With mode parameter",
        "data": {
            "image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
            "mode": "furnishing",
            "generation_count": 1
        }
    },
    {
        "name": "With style parameter",
        "data": {
            "image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
            "style": "modern",
            "generation_count": 1
        }
    }
]

for test in payloads:
    print(f"\nTest: {test['name']}")
    print(f"Payload: {json.dumps(test['data'], indent=2)}")
    
    response = requests.post(
        "https://api.reimaginehome.ai/v1/generate_image",
        headers=headers,
        json=test['data']
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"[OK] Success! Job ID: {result.get('data', {}).get('job_id')}")
        break
    else:
        error_msg = response.json().get('error_message', 'Unknown error')[:100]
        print(f"[X] Error: {error_msg}")

# Also check what parameters the API actually expects
print("\n\n" + "=" * 60)
print("Checking API expectations...")

# Send empty payload to see what it complains about
response = requests.post(
    "https://api.reimaginehome.ai/v1/generate_image",
    headers=headers,
    json={}
)

if response.status_code != 200:
    print("Empty payload error:")
    print(response.json())