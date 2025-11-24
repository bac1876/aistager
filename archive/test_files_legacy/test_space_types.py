import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')
API_KEY = os.getenv('REIMAGINEHOME_API_KEY')

headers = {'api-key': API_KEY}

# Test different space_type values
space_types = [
    "Interior%20(furnishing)",  # URL encoded from documentation
    "Interior%20(architectural)",
    "Exterior%20(landscaping)",
    "Interior (furnishing)",    # With spaces
    "Interior (architectural)",
    "Exterior (landscaping)",
    "interior",                  # Lowercase
    "exterior",
    "garden"
]

print("Testing space_type values for generate_image endpoint...")
print("=" * 60)

base_payload = {
    "image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
    "mask_urls": ["https://example.com/mask.png"],
    "mask_category": "furnishing",
    "generation_count": 1
}

for space_type in space_types:
    payload = base_payload.copy()
    payload["space_type"] = space_type
    
    response = requests.post(
        "https://api.reimaginehome.ai/v1/generate_image",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        print(f"[OK] '{space_type}' - Success!")
        result = response.json()
        print(f"     Job ID: {result.get('data', {}).get('job_id')}")
        break
    else:
        error = response.json().get('error_message', 'Unknown error')
        if "Invalid space type" in error:
            print(f"[X] '{space_type}' - Invalid space type")
        else:
            print(f"[!] '{space_type}' - {error}")