import requests

# Get the ngrok URL from user
ngrok_url = input("Enter your ngrok URL (e.g., https://abc123.ngrok-free.app): ").strip()

print(f"\nTesting ngrok accessibility...")
print("=" * 60)

# Test 1: Basic connection
print("\n1. Testing basic ngrok connection...")
try:
    response = requests.get(ngrok_url, timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   ngrok is accessible!")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Test a sample image endpoint
test_image_id = "test123"
image_url = f"{ngrok_url}/image/{test_image_id}"
print(f"\n2. Testing image endpoint: {image_url}")
try:
    response = requests.get(image_url, timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 404:
        print("   Expected 404 (image doesn't exist) - endpoint is working!")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Check ngrok headers
print(f"\n3. Checking if ngrok requires browser verification...")
try:
    response = requests.get(ngrok_url, timeout=5)
    headers = dict(response.headers)
    
    # Check for ngrok warning page
    if 'ngrok-warning' in response.text.lower() or 'visit site' in response.text.lower():
        print("   ⚠️  ISSUE FOUND: ngrok is showing a warning page!")
        print("   This prevents APIs from accessing your images.")
        print("\n   SOLUTION: Add a header to bypass the warning:")
        print("   You need to use ngrok's --request-header-add flag")
    else:
        print("   No ngrok warning page detected")
        
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("If ngrok shows a warning page, external APIs can't access your images.")
print("This is likely why ReimagineHome gets 'mask creation failed'.")