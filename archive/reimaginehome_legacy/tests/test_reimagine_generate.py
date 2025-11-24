import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
print(f"Testing ReimagineHome API Key: {API_KEY[:10]}...")

headers = {
    'api-key': API_KEY
}

# Test the generate_image endpoint with different payloads
print("\nTesting generate_image endpoint...")
print("=" * 60)

# Test different payload structures
test_payloads = [
    {
        "image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
        "prompt": "Modern living room with furniture",
        "num_images": 1
    },
    {
        "image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
        "prompt": "Modern living room with furniture",
        "generation_count": 1
    },
    {
        "image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
        "design_style": "Modern",
        "room_type": "Living Room",
        "generation_count": 1
    },
    {
        "image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800",
        "style": "Modern",
        "mode": "Interior (furnishing)",
        "generation_count": 1
    }
]

for i, payload in enumerate(test_payloads):
    print(f"\nTest {i+1}: {list(payload.keys())}")
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
            print(f"\nJob created: {job_id}")
            print("Polling for results...")
            
            # Poll for results
            for attempt in range(20):
                time.sleep(2)
                status_response = requests.get(
                    f"https://api.reimaginehome.ai/v1/generate_image/{job_id}",
                    headers=headers
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"Attempt {attempt + 1}: {status_data.get('data', {}).get('job_status', 'Unknown')}")
                    
                    if status_data.get('data', {}).get('job_status') == 'done':
                        print("\nJob completed!")
                        print(f"Results: {status_data}")
                        break
        break
    else:
        print(f"Error: {response.text[:200]}")

# Also test mask creation + image generation workflow
print("\n" + "=" * 60)
print("Testing mask creation + generation workflow...")

# Step 1: Create mask
mask_response = requests.post(
    "https://api.reimaginehome.ai/v1/create_mask",
    headers=headers,
    json={"image_url": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800"}
)

if mask_response.status_code == 200:
    mask_data = mask_response.json()
    mask_job_id = mask_data['data']['job_id']
    print(f"Mask job created: {mask_job_id}")
    
    # Wait for mask to complete
    print("Waiting for mask creation...")
    time.sleep(5)
    
    # Check mask status
    mask_status = requests.get(
        f"https://api.reimaginehome.ai/v1/create_mask/{mask_job_id}",
        headers=headers
    )
    
    if mask_status.status_code == 200:
        mask_result = mask_status.json()
        print(f"Mask status: {mask_result.get('data', {}).get('job_status', 'Unknown')}")
        
        # If mask is ready, try to use it for generation
        if mask_result.get('data', {}).get('masks'):
            print("\nMasks available. Testing generation with mask...")
            # This is where we'd test generation with masks if we knew the correct format