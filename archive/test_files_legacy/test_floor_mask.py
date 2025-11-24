import os
import requests
import time
from dotenv import load_dotenv

load_dotenv('.env.local')

REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
headers = {'api-key': REIMAGINEHOME_API_KEY}

# Use the Dropbox image
dropbox_url = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=1"

print("Creating masks to analyze...")
mask_response = requests.post(
    'https://api.reimaginehome.ai/v1/create_mask',
    headers=headers,
    json={'image_url': dropbox_url}
)

if mask_response.status_code != 200:
    print(f"Error: {mask_response.json()}")
    exit()

mask_job_id = mask_response.json()['data']['job_id']
print(f"Mask job ID: {mask_job_id}")

# Wait for masks
masks = None
for i in range(20):
    time.sleep(2)
    status_response = requests.get(
        f'https://api.reimaginehome.ai/v1/create_mask/{mask_job_id}',
        headers=headers
    )
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        if status_data.get('data', {}).get('job_status') == 'done':
            masks = status_data['data']['masks']
            break

if masks:
    print(f"\nFound {len(masks)} masks:")
    
    # Analyze all masks
    for i, mask in enumerate(masks):
        print(f"\nMask {i+1}:")
        print(f"  Category: {mask.get('category', 'N/A')}")
        print(f"  Area %: {mask.get('area_percent', 'N/A')}")
    
    # Sort by area
    masks_sorted = sorted(masks, key=lambda x: x.get('area_percent', 0), reverse=True)
    
    print("\n=== TESTING DIFFERENT MASK STRATEGIES ===")
    
    # Strategy 1: Use the second largest mask (often the floor)
    print("\nStrategy 1: Second largest mask")
    if len(masks_sorted) > 1:
        second_largest = masks_sorted[1]
        print(f"Second largest: {second_largest.get('category')} - {second_largest.get('area_percent')}%")
    
    # Strategy 2: Find architectural mask with medium area (likely floor)
    print("\nStrategy 2: Architectural mask with 20-40% area")
    floor_candidates = [m for m in masks if 'architectural' in m.get('category', '') 
                       and 20 < m.get('area_percent', 0) < 40]
    if floor_candidates:
        print(f"Found {len(floor_candidates)} floor candidates")
        for fc in floor_candidates:
            print(f"  - {fc.get('category')} - {fc.get('area_percent')}%")
    
    # Strategy 3: Use NO masks (let AI decide)
    print("\nStrategy 3: No masks (full image)")
    
    # Test with the most promising approach
    print("\n=== TESTING WITH ARCHITECTURAL MASK ===")
    
    # Find the architectural mask that's likely the floor (not the largest which might be walls)
    arch_masks = [m for m in masks if 'architectural' in m.get('category', '')]
    arch_masks_sorted = sorted(arch_masks, key=lambda x: x.get('area_percent', 0), reverse=True)
    
    if len(arch_masks_sorted) > 1:
        # Use second largest architectural mask (often the floor)
        floor_mask = arch_masks_sorted[1]
        print(f"Using mask: {floor_mask.get('category')} - {floor_mask.get('area_percent')}%")
        
        generation_payload = {
            'image_url': dropbox_url,
            'mask_urls': [floor_mask['url']],
            'mask_category': 'furnishing',  # Per API docs
            'space_type': 'ST-INT-011',  # Living Room
            'design_theme': 'DT-INT-011',  # Modern
            'generation_count': 1
        }
        
        print("\nGenerating with selected mask...")
        gen_response = requests.post(
            'https://api.reimaginehome.ai/v1/generate_image',
            headers=headers,
            json=generation_payload
        )
        
        if gen_response.status_code == 200:
            gen_job_id = gen_response.json()['data']['job_id']
            print(f"Generation job: {gen_job_id}")
            
            # Poll for result
            for i in range(30):
                time.sleep(3)
                result = requests.get(
                    f'https://api.reimaginehome.ai/v1/generate_image/{gen_job_id}',
                    headers=headers
                )
                
                if result.status_code == 200:
                    data = result.json()['data']
                    if data['job_status'] == 'done':
                        images = data.get('generated_images', [])
                        if images:
                            print(f"\n[SUCCESS] Result: {images[0]}")
                        else:
                            print("\n[FAILED] No images generated")
                        break
        else:
            print(f"Generation failed: {gen_response.json()}")
    
    # Also test with NO masks
    print("\n\n=== TESTING WITH NO MASKS ===")
    generation_payload2 = {
        'image_url': dropbox_url,
        'mask_urls': [],  # Empty array
        'mask_category': 'furnishing',
        'space_type': 'ST-INT-011',
        'design_theme': 'DT-INT-011',
        'generation_count': 1
    }
    
    print("Generating without masks...")
    gen_response2 = requests.post(
        'https://api.reimaginehome.ai/v1/generate_image',
        headers=headers,
        json=generation_payload2
    )
    
    if gen_response2.status_code == 200:
        gen_job_id2 = gen_response2.json()['data']['job_id']
        print(f"Generation job: {gen_job_id2}")
        
        # Poll for result
        for i in range(30):
            time.sleep(3)
            result = requests.get(
                f'https://api.reimaginehome.ai/v1/generate_image/{gen_job_id2}',
                headers=headers
            )
            
            if result.status_code == 200:
                data = result.json()['data']
                if data['job_status'] == 'done':
                    images = data.get('generated_images', [])
                    if images:
                        print(f"\n[SUCCESS] No-mask Result: {images[0]}")
                    else:
                        print("\n❌ No images generated")
                    break
    else:
        print(f"No-mask generation failed: {gen_response2.json()}")