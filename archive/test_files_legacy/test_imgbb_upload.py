import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')

IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')
print(f"ImgBB API Key: {'Found' if IMGBB_API_KEY else 'Not found'}")

# Test with a simple image
test_image_url = "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800"

print("\nTesting ImgBB upload...")

# Download test image
image_response = requests.get(test_image_url)
if image_response.status_code == 200:
    import base64
    image_base64 = base64.b64encode(image_response.content).decode('utf-8')
    
    # Upload to ImgBB
    upload_response = requests.post(
        'https://api.imgbb.com/1/upload',
        data={
            'key': IMGBB_API_KEY,
            'image': image_base64,
            'expiration': 600  # 10 minutes
        }
    )
    
    print(f"Upload status: {upload_response.status_code}")
    print(f"Response: {upload_response.text[:500]}")
    
    if upload_response.status_code == 200:
        data = upload_response.json()
        if data.get('success'):
            print(f"\n✓ Upload successful!")
            print(f"Image URL: {data['data']['url']}")
        else:
            print(f"\n✗ Upload failed: {data}")
    else:
        print(f"\n✗ HTTP Error: {upload_response.status_code}")
else:
    print("Failed to download test image")