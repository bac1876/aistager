import requests
import json
import time

# Test the production API directly
print("=== Testing Production API ===\n")

# Test payload
payload = {
    "image": "https://i.ibb.co/7JpPyMb/test-image.jpg",  # Using URL to skip upload
    "transformation_type": "furnish",
    "space_type": "interior",
    "room_type": "living_room",
    "design_style": "contemporary",
    "update_flooring": False,
    "block_decorative": True
}

# Call production API
print("Calling production API...")
response = requests.post(
    "https://aistager.vercel.app/api/stage",
    json=payload,
    headers={"Content-Type": "application/json"}
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}\n")

if response.status_code == 200:
    result = response.json()
    if result.get('success'):
        request_id = result.get('request_id')
        print(f"Success! Request ID: {request_id}")
        
        # Wait and check for results
        print("\nWaiting 60 seconds for processing...")
        time.sleep(60)
        
        # Check results
        print("\nChecking results...")
        check_response = requests.post(
            "https://aistager.vercel.app/api/check-result",
            json={"request_id": request_id},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Check Status: {check_response.status_code}")
        print(f"Check Response: {check_response.text}")
        
        check_data = check_response.json()
        if check_data.get('status') == 'completed':
            print(f"\nImages received: {check_data.get('images', [])}")
        else:
            print(f"\nStatus: {check_data.get('status')}")
            print("The webhook might not be working correctly")
    else:
        print(f"Error: {result.get('error')}")
else:
    print("API call failed!")