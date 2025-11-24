import requests
import json

# Test the API endpoint directly
url = "http://localhost:5000/api/stage"

# Test payload
payload = {
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
    "space_type": "ST-INT-011",
    "design_theme": ""
}

print("Testing API endpoint directly...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"\nError: {e}")