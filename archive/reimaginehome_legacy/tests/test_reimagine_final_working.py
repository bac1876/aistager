import os
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv('.env.local')
API_KEY = os.getenv('REIMAGINEHOME_API_KEY')

print("ReimagineHome API - Complete Virtual Staging Demo")
print("=" * 60)

headers = {'api-key': API_KEY}

# Step 1: Create masks for a new image
print("\n1. Creating masks...")
image_url = "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800"

mask_response = requests.post(
    'https://api.reimaginehome.ai/v1/create_mask',
    headers=headers,
    json={'image_url': image_url}
)

if mask_response.status_code != 200:
    print(f"[X] Failed to create masks")
    exit(1)

mask_job_id = mask_response.json()['data']['job_id']
print(f"[OK] Mask job created: {mask_job_id}")

# Wait for masks
print("\n2. Processing masks...")
masks = None

for i in range(30):
    time.sleep(2)
    status_response = requests.get(
        f'https://api.reimaginehome.ai/v1/create_mask/{mask_job_id}',
        headers=headers
    )
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        if status_data['data']['job_status'] == 'done':
            masks = status_data['data']['masks']
            print(f"[OK] Masks ready!")
            break

if not masks:
    print("[X] Mask creation failed")
    exit(1)

# Step 3: Generate staged image
print("\n3. Staging the room...")

# Get furnishing masks
furnishing_masks = [m['url'] for m in masks if 'furnishing' in m['category']]
mask_urls = furnishing_masks if furnishing_masks else [masks[0]['url']]

generation_payload = {
    'image_url': image_url,
    'mask_urls': mask_urls,
    'mask_category': 'furnishing',
    'space_type': 'ST-INT-011',  # Living Room
    'design_theme': 'DT-INT-011',  # Modern
    'color_preference': 'warm neutral tones',
    'additional_prompt': 'add comfortable modern furniture',
    'generation_count': 1
}

gen_response = requests.post(
    'https://api.reimaginehome.ai/v1/generate_image',
    headers=headers,
    json=generation_payload
)

if gen_response.status_code == 200:
    result = gen_response.json()
    print(f"[OK] Staging job created successfully!")
    print(f"\nJob ID: {result.get('job_id', 'N/A')}")
    print(f"Status: {result.get('status', 'Processing')}")
    
    print("\n" + "="*60)
    print("SUCCESS! Virtual staging initiated.")
    print("="*60)
    print("\nIn a production environment:")
    print("1. Results would be sent to your webhook URL")
    print("2. The webhook would receive the staged image URLs")
    print("3. Processing typically takes 20-40 seconds")
    
    print("\n[Summary]")
    print(f"- Original image: {image_url}")
    print(f"- Room type: Living Room")
    print(f"- Style: Modern")
    print(f"- Status: Job submitted successfully")
else:
    print(f"[X] Generation failed: {gen_response.text}")

print("\nAPI integration complete!")