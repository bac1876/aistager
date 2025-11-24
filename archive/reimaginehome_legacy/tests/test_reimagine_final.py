import os
import requests
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
print(f"Testing ReimagineHome API - Virtual Staging")
print("=" * 60)

headers = {
    'api-key': API_KEY
}

# Test image URL
image_url = "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800"

# Step 1: Create mask
print("\nStep 1: Creating masks for the room...")
mask_response = requests.post(
    "https://api.reimaginehome.ai/v1/create_mask",
    headers=headers,
    json={"image_url": image_url}
)

if mask_response.status_code != 200:
    print(f"Failed to create mask: {mask_response.text}")
    exit(1)

mask_data = mask_response.json()
mask_job_id = mask_data['data']['job_id']
print(f"Mask job ID: {mask_job_id}")

# Step 2: Wait for mask completion
print("\nStep 2: Processing masks...")
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
        
        if status == 'done':
            masks = mask_result.get('data', {}).get('masks', [])
            print(f"\n[OK] Masks created successfully! Found {len(masks)} masks:")
            for mask in masks:
                print(f"  - {mask['name']}: {mask['category']} ({mask['area_percent']:.1f}% of image)")
            break
        elif status in ['error', 'failed']:
            print("[X] Mask creation failed!")
            exit(1)

if not masks:
    print("No masks found!")
    exit(1)

# Step 3: Generate staged image
print("\n\nStep 3: Generating staged room...")
print("-" * 40)

# Select appropriate masks for staging
furnishing_masks = [m['url'] for m in masks if 'furnishing' in m['category']]
architectural_masks = [m['url'] for m in masks if 'architectural' in m['category']]

# If no furnishing masks, use all masks
mask_urls = furnishing_masks if furnishing_masks else [m['url'] for m in masks]

print(f"Using {len(mask_urls)} mask(s) for staging")

# Step 0: Fetch space_type code for Living Room
print("Fetching space_type code for 'Living Room / Family Room / Lounge'...")
space_type_code = None
try:
    space_type_response = requests.get(
        "https://api.reimaginehome.ai/v1/get-space-type-list",
        headers=headers
    )
    space_type_response.raise_for_status()
    space_types_data = space_type_response.json()
    print("Available interior space types:")
    for space_item in space_types_data.get("data", {}).get("interior_spaces", []):
        for code, name in space_item.items():
            print(f"  {code}: {name}")
    # Now search for Living Room
    for space_item in space_types_data.get("data", {}).get("interior_spaces", []):
        if (
            "Living Room/Family Room/Lounge" in space_item.values()
            or "Living Room" in space_item.values()
        ):
            space_type_code = list(space_item.keys())[0]
            break
    if not space_type_code:
        print("[X] Could not find space_type code for Living Room. Check available types.")
        exit(1)
    print(f"[OK] Using space_type code: {space_type_code}")
except Exception as e:
    print(f"[X] Error fetching space_type code: {e}")
    exit(1)

# Create generation payload
# Try without space_type first, add required fields one by one
generation_payload = {
    "image_url": image_url,
    "mask_urls": mask_urls,
    "mask_category": "furnishing",  # Valid values: 'architectural', 'furnishing', 'landscaping'
    "generation_count": 1,
    "prompt": "Modern living room with contemporary furniture, cozy atmosphere, warm lighting",
    # Additional fields that might be required
    "design_style": "modern",
    "room_type": "living room",
    "space_type": space_type_code  # Dynamically fetched code
}

print(f"\nSending generation request...")
response = requests.post(
    "https://api.reimaginehome.ai/v1/generate_image",
    headers=headers,
    json=generation_payload
)

if response.status_code != 200:
    print(f"[X] Generation failed: {response.text}")
    exit(1)

result = response.json()
generation_job_id = result['data']['job_id']
print(f"[OK] Generation job created: {generation_job_id}")

# Step 4: Wait for generation to complete
print("\nStep 4: Generating your staged room (this may take 20-30 seconds)...")
final_result = None

for attempt in range(40):
    time.sleep(3)
    status_response = requests.get(
        f"https://api.reimaginehome.ai/v1/generate_image/{generation_job_id}",
        headers=headers
    )
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        job_status = status_data.get('data', {}).get('job_status', 'Unknown')
        
        if job_status == 'done':
            final_result = status_data.get('data', {})
            print(f"\n[OK] Staging completed successfully!")
            break
        elif job_status in ['error', 'failed']:
            print(f"\n[X] Generation failed: {status_data}")
            exit(1)
        else:
            print(f".", end="", flush=True)

if final_result:
    print("\n\n" + "=" * 60)
    print("STAGING RESULTS")
    print("=" * 60)
    
    if 'output' in final_result:
        output_images = final_result['output']
        if isinstance(output_images, list):
            print(f"\n[OK] Generated {len(output_images)} staged image(s):")
            for i, img_url in enumerate(output_images):
                print(f"\n  Image {i+1}: {img_url}")
        else:
            print(f"\nGenerated image: {output_images}")
    
    print(f"\nOriginal image: {image_url}")
    print(f"Credits consumed: {final_result.get('credits_consumed', 'Unknown')}")
    
    # Save the working configuration
    print("\n\n" + "=" * 60)
    print("WORKING API CONFIGURATION")
    print("=" * 60)
    print("Base URL: https://api.reimaginehome.ai")
    print("Authentication: Headers = {'api-key': 'YOUR_API_KEY'}")
    print("Endpoints:")
    print("  - POST /v1/create_mask - Create masks for image")
    print("  - GET  /v1/create_mask/{job_id} - Check mask status")
    print("  - POST /v1/generate_image - Generate staged image")
    print("  - GET  /v1/generate_image/{job_id} - Check generation status")
else:
    print("\n[X] Generation timed out")