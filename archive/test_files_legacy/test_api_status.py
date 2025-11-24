import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')

# Test ReimagineHome API
REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')

if REIMAGINEHOME_API_KEY:
    print("Testing ReimagineHome API...")
    headers = {'api-key': REIMAGINEHOME_API_KEY}
    
    # Test with a simple API call to check if key is valid
    try:
        # Try to get API status or user info
        response = requests.get(
            'https://api.reimaginehome.ai/v1/user',
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("[OK] ReimagineHome API key is valid!")
            print(f"Response: {response.json()}")
        else:
            print(f"[ERROR] API returned error: {response.text}")
    except Exception as e:
        print(f"[ERROR] API test failed: {str(e)}")
else:
    print("[ERROR] No ReimagineHome API key found")

# Test Cloudinary configuration
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

print("\nCloudinary Configuration:")
print(f"Cloud Name: {'[OK]' if CLOUDINARY_CLOUD_NAME else '[MISSING]'}")
print(f"API Key: {'[OK]' if CLOUDINARY_API_KEY else '[MISSING]'}")
print(f"API Secret: {'[OK]' if CLOUDINARY_API_SECRET else '[MISSING]'}")

# Test ImgBB
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')
print(f"\nImgBB API Key: {'[OK]' if IMGBB_API_KEY else '[MISSING]'}")