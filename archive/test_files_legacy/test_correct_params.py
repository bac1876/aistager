import os
import requests
import time
from dotenv import load_dotenv

load_dotenv('.env.local')

REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
headers = {'api-key': REIMAGINEHOME_API_KEY}

dropbox_url = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=1"

# Create fresh masks
print("Creating masks...")
mask_response = requests.post(
    'https://api.reimaginehome.ai/v1/create_mask',
    headers=headers,
    json={'image_url': dropbox_url}
)

mask_job_id = mask_response.json()['data']['job_id']

# Wait for masks
time.sleep(5)
status_response = requests.get(
    f'https://api.reimaginehome.ai/v1/create_mask/{mask_job_id}',
    headers=headers
)

for i in range(10):
    if status_response.json()['data']['job_status'] == 'done':
        break
    time.sleep(2)
    status_response = requests.get(
        f'https://api.reimaginehome.ai/v1/create_mask/{mask_job_id}',
        headers=headers
    )

masks = status_response.json()['data']['masks']

# TEST 1: Use architectural mask with correct category
print("\n=== Using ARCHITECTURAL mask category ===")
architectural_masks = [m for m in masks if 'architectural' in m.get('category', '')]
largest_arch = max(architectural_masks, key=lambda x: x.get('area_percent', 0))

generation_payload = {
    'image_url': dropbox_url,
    'mask_urls': [largest_arch['url']],
    'mask_category': 'architectural',  # Correct category
    'space_type': 'ST-INT-011',
    'design_theme': 'DT-INT-011',
    'generation_count': 1
}

print("Generating with architectural mask...")
gen_response = requests.post(
    'https://api.reimaginehome.ai/v1/generate_image',
    headers=headers,
    json=generation_payload
)

if gen_response.status_code == 200:
    gen_job_id = gen_response.json()['data']['job_id']
    print(f"Job ID: {gen_job_id}")
    
    # Poll
    for i in range(20):
        time.sleep(3)
        result = requests.get(f'https://api.reimaginehome.ai/v1/generate_image/{gen_job_id}', headers=headers)
        if result.json()['data']['job_status'] == 'done':
            images = result.json()['data'].get('generated_images', [])
            if images:
                print(f"\n✅ ARCHITECTURAL Result: {images[0]}")
            break

# TEST 2: Try ALL masks
print("\n\n=== Using ALL MASKS ===")
all_mask_urls = [m['url'] for m in masks]

generation_payload2 = {
    'image_url': dropbox_url,
    'mask_urls': all_mask_urls,  # All masks
    'space_type': 'ST-INT-011',
    'design_theme': 'DT-INT-011',
    'generation_count': 1
}

print("Generating with all masks...")
gen_response2 = requests.post(
    'https://api.reimaginehome.ai/v1/generate_image',
    headers=headers,
    json=generation_payload2
)

if gen_response2.status_code == 200:
    gen_job_id2 = gen_response2.json()['data']['job_id']
    print(f"Job ID: {gen_job_id2}")
    
    # Poll
    for i in range(20):
        time.sleep(3)
        result = requests.get(f'https://api.reimaginehome.ai/v1/generate_image/{gen_job_id2}', headers=headers)
        if result.json()['data']['job_status'] == 'done':
            images = result.json()['data'].get('generated_images', [])
            if images:
                print(f"\n✅ ALL MASKS Result: {images[0]}")
            break

# TEST 3: NO MASKS
print("\n\n=== Using NO MASKS (whole image) ===")
generation_payload3 = {
    'image_url': dropbox_url,
    'mask_urls': [],  # No masks
    'space_type': 'ST-INT-011',
    'design_theme': 'DT-INT-011',
    'generation_count': 1
}

print("Generating without masks...")
gen_response3 = requests.post(
    'https://api.reimaginehome.ai/v1/generate_image',
    headers=headers,
    json=generation_payload3
)

if gen_response3.status_code == 200:
    gen_job_id3 = gen_response3.json()['data']['job_id']
    print(f"Job ID: {gen_job_id3}")
    
    # Poll
    for i in range(20):
        time.sleep(3)
        result = requests.get(f'https://api.reimaginehome.ai/v1/generate_image/{gen_job_id3}', headers=headers)
        if result.json()['data']['job_status'] == 'done':
            images = result.json()['data'].get('generated_images', [])
            if images:
                print(f"\n✅ NO MASKS Result: {images[0]}")
            break