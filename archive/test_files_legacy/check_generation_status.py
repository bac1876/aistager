import os
import requests
import time
from dotenv import load_dotenv

load_dotenv('.env.local')

REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
headers = {'api-key': REIMAGINEHOME_API_KEY}

# Check the status of our previous generation jobs
job_ids = [
    "68800f396fe37c5542de2c3b",  # The architectural mask test
]

for job_id in job_ids:
    print(f"\nChecking job: {job_id}")
    
    for i in range(20):
        result = requests.get(
            f'https://api.reimaginehome.ai/v1/generate_image/{job_id}',
            headers=headers
        )
        
        if result.status_code == 200:
            data = result.json()['data']
            status = data['job_status']
            print(f"Status: {status}")
            
            if status == 'done':
                images = data.get('generated_images', [])
                if images:
                    print(f"[SUCCESS] Result: {images[0]}")
                    print("\nOpen this URL in your browser to see if furniture was added!")
                else:
                    print("[FAILED] No images generated")
                break
        
        time.sleep(2)

# Also test with NO masks approach
print("\n\n=== TESTING WITH NO MASKS (might work better) ===")
dropbox_url = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=1"

generation_payload = {
    'image_url': dropbox_url,
    'mask_urls': [],  # Empty = let AI decide where to add furniture
    'space_type': 'ST-INT-011',
    'design_theme': 'DT-INT-011',
    'generation_count': 1
}

print("Generating without masks...")
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
                    print(f"\n[SUCCESS] No-mask Result: {images[0]}")
                    print("Check if this version has furniture added!")
                else:
                    print("\n[FAILED] No images generated")
                break
            else:
                print(f"Status: {data['job_status']}")
else:
    print(f"Generation failed: {gen_response.json()}")