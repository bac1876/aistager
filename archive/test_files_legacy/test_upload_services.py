import os
import base64
import requests
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv('.env.local')

# Test image - small 1x1 white pixel PNG
TEST_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
TEST_IMAGE_BYTES = base64.b64decode(TEST_IMAGE_BASE64)

def test_cloudinary():
    """Test Cloudinary upload"""
    print("\n=== Testing Cloudinary ===")
    
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
    
    if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
        print("[ERROR] Cloudinary credentials not found")
        return None
        
    try:
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET
        )
        
        # Upload test image
        result = cloudinary.uploader.upload(
            TEST_IMAGE_BYTES,
            public_id="test_image",
            folder="aistager_test",
            format="png"
        )
        
        image_url = result.get('secure_url')
        print(f"[OK] Upload successful!")
        print(f"URL: {image_url}")
        
        # Test if URL is accessible
        response = requests.get(image_url, timeout=5)
        if response.status_code == 200:
            print("[OK] Image URL is accessible")
        else:
            print(f"[ERROR] Image URL returned status: {response.status_code}")
            
        return image_url
        
    except Exception as e:
        print(f"[ERROR] Cloudinary upload failed: {str(e)}")
        return None

def test_imgbb():
    """Test ImgBB upload"""
    print("\n=== Testing ImgBB ===")
    
    IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')
    
    if not IMGBB_API_KEY:
        print("[ERROR] ImgBB API key not found")
        return None
        
    try:
        # Convert to base64 string
        image_base64 = base64.b64encode(TEST_IMAGE_BYTES).decode('utf-8')
        
        response = requests.post(
            'https://api.imgbb.com/1/upload',
            data={
                'key': IMGBB_API_KEY,
                'image': image_base64,
                'name': 'test_image'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                image_url = data['data']['url']
                print(f"[OK] Upload successful!")
                print(f"URL: {image_url}")
                
                # Test if URL is accessible
                test_response = requests.get(image_url, timeout=5)
                if test_response.status_code == 200:
                    print("[OK] Image URL is accessible")
                else:
                    print(f"[ERROR] Image URL returned status: {test_response.status_code}")
                    
                return image_url
            else:
                print(f"[ERROR] ImgBB returned error: {data}")
        else:
            print(f"[ERROR] ImgBB returned status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] ImgBB upload failed: {str(e)}")
        return None

def test_0x0st():
    """Test 0x0.st upload"""
    print("\n=== Testing 0x0.st ===")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.post(
            'https://0x0.st',
            files={'file': ('test.png', TEST_IMAGE_BYTES, 'image/png')},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            image_url = response.text.strip()
            print(f"[OK] Upload successful!")
            print(f"URL: {image_url}")
            
            # Test if URL is accessible
            test_response = requests.get(image_url, timeout=5)
            if test_response.status_code == 200:
                print("[OK] Image URL is accessible")
            else:
                print(f"[ERROR] Image URL returned status: {test_response.status_code}")
                
            return image_url
        else:
            print(f"[ERROR] 0x0.st returned status: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] 0x0.st upload failed: {str(e)}")
        return None

def test_reimaginehome_api(image_url):
    """Test if ReimagineHome API can access the image"""
    print(f"\n=== Testing ReimagineHome API Access ===")
    print(f"Testing URL: {image_url}")
    
    REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
    
    if not REIMAGINEHOME_API_KEY:
        print("[ERROR] ReimagineHome API key not found")
        return
        
    try:
        headers = {'api-key': REIMAGINEHOME_API_KEY}
        response = requests.post(
            'https://api.reimaginehome.ai/v1/create_mask',
            headers=headers,
            json={'image_url': image_url},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("[OK] ReimagineHome can access the image!")
        else:
            print(f"[ERROR] ReimagineHome API error: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] API test failed: {str(e)}")

if __name__ == "__main__":
    print("Testing Image Upload Services")
    print("=" * 50)
    
    # Test each service
    cloudinary_url = test_cloudinary()
    imgbb_url = test_imgbb()
    x0st_url = test_0x0st()
    
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"Cloudinary: {'[OK]' if cloudinary_url else '[FAILED]'}")
    print(f"ImgBB: {'[OK]' if imgbb_url else '[FAILED]'}")
    print(f"0x0.st: {'[OK]' if x0st_url else '[FAILED]'}")
    
    # Test ReimagineHome API access with successful uploads
    if cloudinary_url:
        test_reimaginehome_api(cloudinary_url)
    elif imgbb_url:
        test_reimaginehome_api(imgbb_url)
    elif x0st_url:
        test_reimaginehome_api(x0st_url)