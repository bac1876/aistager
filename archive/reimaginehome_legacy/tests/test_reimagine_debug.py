import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv('.env.local')

REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')

print("Debug Test for ReimagineHome + ImgBB")
print("=" * 60)

# Step 1: Test with a known working image URL first
print("\n1. Testing with known image URL...")
test_url = "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800"

headers = {'api-key': REIMAGINEHOME_API_KEY}

mask_response = requests.post(
    'https://api.reimaginehome.ai/v1/create_mask',
    headers=headers,
    json={'image_url': test_url}
)

print(f"Mask creation status: {mask_response.status_code}")
if mask_response.status_code == 200:
    print("[OK] Known image works!")
else:
    print(f"[X] Error: {mask_response.text}")

# Step 2: Test ImgBB upload and then ReimagineHome
print("\n2. Testing ImgBB upload + ReimagineHome...")

# Download test image
image_response = requests.get(test_url)
image_base64 = base64.b64encode(image_response.content).decode('utf-8')

# Upload to ImgBB
upload_response = requests.post(
    'https://api.imgbb.com/1/upload',
    data={
        'key': IMGBB_API_KEY,
        'image': image_base64,
        'expiration': 600
    }
)

if upload_response.status_code == 200:
    upload_data = upload_response.json()
    if upload_data['success']:
        imgbb_url = upload_data['data']['url']
        print(f"ImgBB URL: {imgbb_url}")
        
        # Test if URL is accessible
        test_access = requests.head(imgbb_url)
        print(f"URL accessible: {test_access.status_code == 200}")
        
        # Try mask creation with ImgBB URL
        mask_response2 = requests.post(
            'https://api.reimaginehome.ai/v1/create_mask',
            headers=headers,
            json={'image_url': imgbb_url}
        )
        
        print(f"Mask creation with ImgBB URL: {mask_response2.status_code}")
        if mask_response2.status_code != 200:
            print(f"Error response: {mask_response2.text}")
            
            # Try with display_url instead
            display_url = upload_data['data']['display_url']
            print(f"\nTrying display_url: {display_url}")
            
            mask_response3 = requests.post(
                'https://api.reimaginehome.ai/v1/create_mask',
                headers=headers,
                json={'image_url': display_url}
            )
            
            print(f"Mask creation with display_url: {mask_response3.status_code}")
            if mask_response3.status_code != 200:
                print(f"Error: {mask_response3.text}")
        else:
            print("[OK] ImgBB URL works with ReimagineHome!")

print("\n" + "=" * 60)
print("Diagnosis:")
print("- If known URL works but ImgBB doesn't: URL access issue")
print("- If both fail: API key or service issue")
print("- Check which URL format works: 'url' or 'display_url'")