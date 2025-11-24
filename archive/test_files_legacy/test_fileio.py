import requests
import json

print("=== Testing file.io API ===\n")

# Test with a simple text file
test_data = b"Hello, this is a test file"

try:
    print("Uploading test file to file.io...")
    response = requests.post(
        'https://file.io/?expires=1h',
        files={'file': ('test.txt', test_data, 'text/plain')},
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"\nRaw Response (first 500 chars):")
    print(response.text[:500])
    
    # Try to parse as JSON
    try:
        data = response.json()
        print(f"\nParsed JSON:")
        print(json.dumps(data, indent=2))
    except json.JSONDecodeError as e:
        print(f"\nJSON Parse Error: {e}")
        print("Response is not valid JSON")
        
except Exception as e:
    print(f"Request Error: {e}")