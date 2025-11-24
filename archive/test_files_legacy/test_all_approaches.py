import os
import requests
import time
from dotenv import load_dotenv

load_dotenv('.env.local')

REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
headers = {'api-key': REIMAGINEHOME_API_KEY}

dropbox_url = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=1"

print("Creating masks...")
mask_response = requests.post(
    'https://api.reimaginehome.ai/v1/create_mask',
    headers=headers,
    json={'image_url': dropbox_url}
)

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

if not masks:
    print("Failed to get masks")
    exit()

print(f"Got {len(masks)} masks")

# Get different mask types
architectural_masks = [m for m in masks if 'architectural' in m.get('category', '')]
furnishing_masks = [m for m in masks if m.get('category', '') == 'furnishing']

# Sort by area
arch_sorted = sorted(architectural_masks, key=lambda x: x.get('area_percent', 0), reverse=True)
furn_sorted = sorted(furnishing_masks, key=lambda x: x.get('area_percent', 0), reverse=True)

print(f"\nArchitectural masks: {len(architectural_masks)}")
for i, m in enumerate(arch_sorted):
    print(f"  {i+1}. {m.get('area_percent', 0):.1f}%")

print(f"\nFurnishing masks: {len(furnishing_masks)}")
for i, m in enumerate(furn_sorted[:3]):
    print(f"  {i+1}. {m.get('area_percent', 0):.1f}%")

# Test different approaches
tests = [
    {
        "name": "Approach 1: Second architectural mask with 'architectural' category",
        "mask_urls": [arch_sorted[1]['url']] if len(arch_sorted) > 1 else [arch_sorted[0]['url']],
        "mask_category": "architectural",
        "masking_element": "floor"
    },
    {
        "name": "Approach 2: Largest architectural mask with 'architectural' category",
        "mask_urls": [arch_sorted[0]['url']],
        "mask_category": "architectural",
        "masking_element": "floor"
    },
    {
        "name": "Approach 3: All furnishing masks",
        "mask_urls": [m['url'] for m in furnishing_masks],
        "mask_category": "furnishing"
    },
    {
        "name": "Approach 4: Single furnishing mask",
        "mask_urls": [furnishing_masks[0]['url']] if furnishing_masks else [masks[0]['url']],
        "mask_category": "furnishing"
    }
]

for test in tests:
    print(f"\n\n=== {test['name']} ===")
    
    payload = {
        'image_url': dropbox_url,
        'mask_urls': test['mask_urls'],
        'mask_category': test['mask_category'],
        'space_type': 'ST-INT-011',
        'design_theme': 'DT-INT-011',
        'generation_count': 1
    }
    
    # Add masking_element if needed
    if 'masking_element' in test:
        payload['masking_element'] = test['masking_element']
    
    print(f"Payload: mask_category={test['mask_category']}, masks={len(test['mask_urls'])}")
    
    gen_response = requests.post(
        'https://api.reimaginehome.ai/v1/generate_image',
        headers=headers,
        json=payload
    )
    
    if gen_response.status_code == 200:
        job_id = gen_response.json()['data']['job_id']
        print(f"Job ID: {job_id}")
        
        # Wait a bit then check
        time.sleep(20)
        
        result = requests.get(
            f'https://api.reimaginehome.ai/v1/generate_image/{job_id}',
            headers=headers
        )
        
        if result.status_code == 200:
            data = result.json()['data']
            if data['job_status'] == 'done':
                images = data.get('generated_images', [])
                if images:
                    print(f"[SUCCESS] Result: {images[0]}")
                else:
                    print("[FAILED] No images")
            else:
                print(f"Status: {data['job_status']} - might need more time")
    else:
        print(f"Failed: {gen_response.json()}")
    
    time.sleep(5)  # Pause between tests