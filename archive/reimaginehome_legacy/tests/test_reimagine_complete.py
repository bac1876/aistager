import os
import requests
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
print(f"Testing ReimagineHome API Key: {API_KEY[:10]}...")

headers = {
    'api-key': API_KEY
}

# Step 1: Create mask
print("\nStep 1: Creating mask...")
print("=" * 60)

mask_response = requests.post(
    "https://api.reimaginehome.ai/v1/create_mask",
    headers=headers,
    json={"image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800"}
)

if mask_response.status_code != 200:
    print(f"Failed to create mask: {mask_response.text}")
    exit(1)

mask_data = mask_response.json()
mask_job_id = mask_data['data']['job_id']
print(f"Mask job created: {mask_job_id}")

# Step 2: Poll for mask completion
print("\nStep 2: Waiting for mask completion...")
mask_url = None
masks = []

for attempt in range(30):
    time.sleep(2)
    mask_status = requests.get(
        f"https://api.reimaginehome.ai/v1/create_mask/{mask_job_id}",
        headers=headers
    )
    
    if mask_status.status_code == 200:
        mask_result = mask_status.json()
        status = mask_result.get('data', {}).get('job_status', 'Unknown')
        print(f"Attempt {attempt + 1}: Status = {status}")
        
        if status == 'done':
            masks = mask_result.get('data', {}).get('masks', [])
            print(f"\nMask creation completed! Found {len(masks)} masks")
            for mask in masks:
                print(f"  - {mask['name']} ({mask['category']}) - {mask['area_percent']}%")
            break
        elif status in ['error', 'failed']:
            print("Mask creation failed!")
            exit(1)

if not masks:
    print("No masks found!")
    exit(1)

# Step 3: Generate image using mask
print("\n\nStep 3: Testing image generation with mask...")
print("=" * 60)

# Pick the first mask with furnishing category or the largest mask
selected_mask = None
for mask in masks:
    if 'furnishing' in mask['category']:
        selected_mask = mask
        break

if not selected_mask:
    # Pick the largest mask
    selected_mask = max(masks, key=lambda x: x['area_percent'])

print(f"Selected mask: {selected_mask['name']} ({selected_mask['category']})")

# Test different generation payloads
generation_payloads = [
    {
        "image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
        "mask_url": selected_mask['url'],
        "mask_category": selected_mask['category'].split(',')[0],  # Use first category
        "generation_count": 1,
        "prompt": "Modern furniture and decor"
    },
    {
        "image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
        "mask_url": selected_mask['url'],
        "mask_category": "furnishing",
        "generation_count": 1,
        "design_style": "Modern",
        "room_type": "Living Room"
    },
    {
        "image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
        "mask_category": "Interior (furnishing)",
        "generation_count": 1,
        "prompt": "Modern living room with furniture"
    }
]

for i, payload in enumerate(generation_payloads):
    print(f"\nGeneration Test {i+1}:")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        "https://api.reimaginehome.ai/v1/generate_image",
        headers=headers,
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Response: {result}")
        
        # If we get a job_id, poll for results
        if 'data' in result and 'job_id' in result['data']:
            job_id = result['data']['job_id']
            print(f"\nGeneration job created: {job_id}")
            print("Polling for results...")
            
            # Poll for results
            for attempt in range(30):
                time.sleep(3)
                status_response = requests.get(
                    f"https://api.reimaginehome.ai/v1/generate_image/{job_id}",
                    headers=headers
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    job_status = status_data.get('data', {}).get('job_status', 'Unknown')
                    print(f"Attempt {attempt + 1}: {job_status}")
                    
                    if job_status == 'done':
                        print("\nGeneration completed!")
                        output = status_data.get('data', {})
                        if 'output' in output:
                            print(f"Generated images: {output['output']}")
                        else:
                            print(f"Full response: {json.dumps(output, indent=2)}")
                        break
                    elif job_status in ['error', 'failed']:
                        print(f"Generation failed: {status_data}")
                        break
        break
    else:
        print(f"Error: {response.text}")