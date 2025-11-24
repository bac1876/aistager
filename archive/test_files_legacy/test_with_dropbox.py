import os
import requests
import time
from dotenv import load_dotenv

load_dotenv('.env.local')

REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')

# Convert Dropbox share link to direct download link
dropbox_url = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=0"
# Change dl=0 to dl=1 for direct download
direct_url = dropbox_url.replace("dl=0", "dl=1")

print(f"Testing with image URL: {direct_url}")

headers = {'api-key': REIMAGINEHOME_API_KEY}

# Step 1: Create masks
print("\n1. Creating masks...")
mask_response = requests.post(
    'https://api.reimaginehome.ai/v1/create_mask',
    headers=headers,
    json={'image_url': direct_url}
)

print(f"Mask API response: {mask_response.status_code}")
if mask_response.status_code != 200:
    print(f"Error: {mask_response.json()}")
    exit()

mask_job_id = mask_response.json()['data']['job_id']
print(f"Mask job ID: {mask_job_id}")

# Step 2: Wait for masks
print("\n2. Waiting for masks to be created...")
masks = None
for i in range(20):
    time.sleep(2)
    print(f"Checking... ({i+1}/20)")
    status_response = requests.get(
        f'https://api.reimaginehome.ai/v1/create_mask/{mask_job_id}',
        headers=headers
    )
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        job_status = status_data.get('data', {}).get('job_status')
        print(f"Job status: {job_status}")
        
        if job_status == 'done':
            masks = status_data['data']['masks']
            print(f"Masks created! Found {len(masks)} masks")
            break

if not masks:
    print("Failed to get masks")
    exit()

# Step 3: Generate staged image
print("\n3. Generating staged image...")
furnishing_masks = [m['url'] for m in masks if 'furnishing' in m.get('category', '')]
if not furnishing_masks:
    masks_sorted = sorted(masks, key=lambda x: x.get('area_percent', 0), reverse=True)
    mask_urls = [masks_sorted[0]['url']] if masks_sorted else []
else:
    mask_urls = furnishing_masks

generation_payload = {
    'image_url': direct_url,
    'mask_urls': mask_urls,
    'mask_category': 'furnishing',
    'space_type': 'ST-INT-011',  # Living Room
    'generation_count': 1
}

gen_response = requests.post(
    'https://api.reimaginehome.ai/v1/generate_image',
    headers=headers,
    json=generation_payload
)

print(f"Generation API response: {gen_response.status_code}")
if gen_response.status_code != 200:
    print(f"Error: {gen_response.json()}")
    exit()

generation_job_id = gen_response.json()['data']['job_id']
print(f"Generation job ID: {generation_job_id}")

# Step 4: Poll for results
print("\n4. Waiting for staged image...")
for i in range(30):
    time.sleep(2)
    print(f"Checking... ({i+1}/30)")
    
    result_response = requests.get(
        f'https://api.reimaginehome.ai/v1/generate_image/{generation_job_id}',
        headers=headers
    )
    
    if result_response.status_code == 200:
        result_data = result_response.json()
        job_status = result_data.get('data', {}).get('job_status')
        print(f"Job status: {job_status}")
        
        if job_status == 'done':
            print(f"\nFull response data: {result_data}")
            output_urls = result_data['data'].get('output_urls', [])
            if output_urls:
                print(f"\n✅ SUCCESS! Staged image URL: {output_urls[0]}")
                print("\nOpen this URL in your browser to see the staged room!")
            else:
                print("No output URLs found in response")
                print(f"Available keys in data: {list(result_data.get('data', {}).keys())}")
            break

print("\nTest complete!")