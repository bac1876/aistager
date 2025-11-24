import os
import requests
import time
from dotenv import load_dotenv

load_dotenv('.env.local')

REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
headers = {'api-key': REIMAGINEHOME_API_KEY}

dropbox_url = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=1"

print("Testing CORRECT virtual staging approach...")
print("=" * 60)

# First, let's check if there's a specific virtual staging mode
print("\nTest 1: Using additional_prompt to explicitly request furniture")

# We'll use the image without masks first
generation_payload = {
    'image_url': dropbox_url,
    'mask_urls': [dropbox_url],  # Use the whole image as mask
    'mask_category': 'furnishing',
    'space_type': 'ST-INT-011',  # Living Room
    'design_theme': 'DT-INT-011',  # Modern
    'generation_count': 1,
    'additional_prompt': 'Add modern furniture including sofa, coffee table, TV stand, and decor. This is an empty room that needs to be staged with furniture.'
}

print("Payload includes explicit furniture request in additional_prompt")

gen_response = requests.post(
    'https://api.reimaginehome.ai/v1/generate_image',
    headers=headers,
    json=generation_payload
)

if gen_response.status_code == 200:
    job_id = gen_response.json()['data']['job_id']
    print(f"Job ID: {job_id}")
    
    # Poll for result
    print("Waiting for result...")
    for i in range(30):
        time.sleep(3)
        result = requests.get(
            f'https://api.reimaginehome.ai/v1/generate_image/{job_id}',
            headers=headers
        )
        
        if result.status_code == 200:
            data = result.json()['data']
            if data['job_status'] == 'done':
                images = data.get('generated_images', [])
                if images:
                    print(f"\n[SUCCESS] Result: {images[0]}")
                    print("\nCheck if this has furniture added!")
                break
            else:
                print(f"Status: {data['job_status']}")
else:
    print(f"Failed: {gen_response.json()}")

# Test 2: Try creating a custom mask for the whole room
print("\n\nTest 2: Create mask first, then use it for staging")

# Create masks
mask_response = requests.post(
    'https://api.reimaginehome.ai/v1/create_mask',
    headers=headers,
    json={'image_url': dropbox_url}
)

if mask_response.status_code == 200:
    mask_job_id = mask_response.json()['data']['job_id']
    
    # Wait for masks
    time.sleep(5)
    masks = None
    for i in range(10):
        status_response = requests.get(
            f'https://api.reimaginehome.ai/v1/create_mask/{mask_job_id}',
            headers=headers
        )
        if status_response.json()['data']['job_status'] == 'done':
            masks = status_response.json()['data']['masks']
            break
        time.sleep(2)
    
    if masks:
        # Get ALL masks to cover the whole room
        all_mask_urls = [m['url'] for m in masks]
        
        print(f"Using ALL {len(all_mask_urls)} masks to cover entire room")
        
        generation_payload2 = {
            'image_url': dropbox_url,
            'mask_urls': all_mask_urls,  # All masks
            'mask_category': 'furnishing',
            'space_type': 'ST-INT-011',
            'design_theme': 'DT-INT-011',
            'generation_count': 1,
            'additional_prompt': 'Stage this empty room with furniture'
        }
        
        gen_response2 = requests.post(
            'https://api.reimaginehome.ai/v1/generate_image',
            headers=headers,
            json=generation_payload2
        )
        
        if gen_response2.status_code == 200:
            job_id2 = gen_response2.json()['data']['job_id']
            print(f"Job ID: {job_id2}")
            
            # Poll for result
            print("Waiting for result...")
            for i in range(30):
                time.sleep(3)
                result = requests.get(
                    f'https://api.reimaginehome.ai/v1/generate_image/{job_id2}',
                    headers=headers
                )
                
                if result.status_code == 200:
                    data = result.json()['data']
                    if data['job_status'] == 'done':
                        images = data.get('generated_images', [])
                        if images:
                            print(f"\n[SUCCESS] All-masks Result: {images[0]}")
                        break

print("\n\nIMPORTANT: If these still don't add furniture, the API might require:")
print("1. A different endpoint specifically for virtual staging")
print("2. Pre-furnished training data")
print("3. A specific 'staging mode' parameter we haven't found yet")