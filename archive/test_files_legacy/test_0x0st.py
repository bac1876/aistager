import requests

print("=== Testing 0x0.st Upload ===\n")

# Test with a simple text file
test_data = b"Hello, this is a test file"

try:
    print("Uploading to 0x0.st...")
    response = requests.post(
        'https://0x0.st',
        files={'file': ('test.txt', test_data, 'text/plain')},
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"\nResponse Text:")
    print(response.text)
    
    if response.status_code == 200:
        url = response.text.strip()
        print(f"\nSuccess! File URL: {url}")
        
        # Test if URL is accessible
        print("\nTesting URL accessibility...")
        test_response = requests.get(url, timeout=5)
        print(f"Access test status: {test_response.status_code}")
        
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

# Test with an image
print("\n\n=== Testing with Image ===")
try:
    from PIL import Image
    import io
    
    # Create a small test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_data = img_bytes.getvalue()
    
    response = requests.post(
        'https://0x0.st',
        files={'file': ('test.jpg', img_data, 'image/jpeg')},
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")