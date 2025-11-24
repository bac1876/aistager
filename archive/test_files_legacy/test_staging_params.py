import os
import requests
import time
from dotenv import load_dotenv

load_dotenv('.env.local')

REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
headers = {'api-key': REIMAGINEHOME_API_KEY}

# Use the provided masks from previous run
mask_job_id = "68800c296fe37c5542de2b4b"  # From previous run
dropbox_url = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=1"

# Get masks again
print("Getting masks...")
status_response = requests.get(
    f'https://api.reimaginehome.ai/v1/create_mask/{mask_job_id}',
    headers=headers
)

if status_response.status_code != 200:
    print("Failed to get masks")
    exit()

masks = status_response.json()['data']['masks']

# Try different approaches
print("\n=== TEST 1: Using architectural masks (floor/walls) ===")
architectural_masks = [m['url'] for m in masks if 'architectural' in m.get('category', '')]
print(f"Found {len(architectural_masks)} architectural masks")

if architectural_masks:
    # Use the largest architectural mask (likely the floor)
    largest_arch = max([m for m in masks if 'architectural' in m.get('category', '')], 
                      key=lambda x: x.get('area_percent', 0))
    print(f"Using largest architectural mask: {largest_arch.get('area_percent')}% area")
    
    generation_payload = {
        'image_url': dropbox_url,
        'mask_urls': [largest_arch['url']],
        'mask_category': 'floor',  # Try floor category
        'space_type': 'ST-INT-011',
        'design_theme': 'DT-INT-011',  # Modern
        'generation_count': 1,
        'ai_intervention': 'high'  # Try high intervention
    }
    
    print("\nSending generation request with floor mask...")
    gen_response = requests.post(
        'https://api.reimaginehome.ai/v1/generate_image',
        headers=headers,
        json=generation_payload
    )
    
    if gen_response.status_code == 200:
        gen_job_id = gen_response.json()['data']['job_id']
        print(f"Generation job ID: {gen_job_id}")
        
        # Poll for result
        for i in range(20):
            time.sleep(3)
            result_response = requests.get(
                f'https://api.reimaginehome.ai/v1/generate_image/{gen_job_id}',
                headers=headers
            )
            
            if result_response.status_code == 200:
                result_data = result_response.json()
                if result_data['data']['job_status'] == 'done':
                    images = result_data['data'].get('generated_images', [])
                    if images:
                        print(f"\n✅ Generated image URL: {images[0]}")
                        print("Check if this has furniture added!")
                    break
    else:
        print(f"Generation failed: {gen_response.json()}")

print("\n\n=== TEST 2: Using virtual_staging endpoint if available ===")
# Try a different endpoint
virtual_staging_payload = {
    'image_url': dropbox_url,
    'space_type': 'ST-INT-011',
    'design_theme': 'DT-INT-011',
    'mode': 'virtual_staging'  # Explicitly set mode
}

print("Trying virtual staging mode...")
vs_response = requests.post(
    'https://api.reimaginehome.ai/v1/virtual_staging',  # Try this endpoint
    headers=headers,
    json=virtual_staging_payload
)

if vs_response.status_code == 404:
    print("Virtual staging endpoint not found")
    
    # Try the generate endpoint with different params
    print("\n=== TEST 3: Using generate endpoint with virtual staging params ===")
    vs_payload = {
        'image_url': dropbox_url,
        'space_type': 'ST-INT-011',
        'design_theme': 'DT-INT-011',
        'generation_type': 'virtual_staging',
        'room_empty': True,
        'add_furniture': True
    }
    
    vs_response = requests.post(
        'https://api.reimaginehome.ai/v1/generate_image',
        headers=headers,
        json=vs_payload
    )
    
    print(f"Response: {vs_response.status_code}")
    if vs_response.status_code != 200:
        print(f"Error: {vs_response.json()}")