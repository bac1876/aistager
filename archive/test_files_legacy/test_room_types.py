import os
import requests
from dotenv import load_dotenv
import time

load_dotenv('.env.local')
api_key = os.getenv('INSTANTDECO_API_KEY')

# Test all room types from the documentation
room_types_to_test = [
    "bathroom",
    "bedroom", 
    "dining_room",
    "home_office",
    "kid_bedroom",
    "kitchen",
    "living_room",
    "shower",
    "pool",
    "terrace", 
    "pergola"
]

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

print("=== Testing All Room Types ===")
print("Waiting 45 seconds before starting...")
time.sleep(45)

working_rooms = []
failed_rooms = []

for room_type in room_types_to_test[:3]:  # Test first 3 to avoid too many requests
    print(f"\nTesting: {room_type}")
    
    payload = {
        "design": "modern",
        "room_type": room_type,
        "transformation_type": "furnish",
        "block_element": "wall,floor,ceiling,windowpane,door",
        "img_url": "https://i.ibb.co/7JpPyMb/test-image.jpg",
        "webhook_url": "https://webhook.site/test",
        "num_images": 1
    }
    
    response = requests.post(
        'https://app.instantdeco.ai/api/1.1/wf/request_v2',
        json=payload,
        headers=headers,
        timeout=10
    )
    
    result = response.json()
    if result.get('status') == 'success' and result.get('response', {}).get('status') == 'success':
        print(f"✓ {room_type} - WORKS!")
        working_rooms.append(room_type)
    else:
        print(f"✗ {room_type} - Failed: {result.get('response', {}).get('message')}")
        failed_rooms.append(room_type)
    
    # Wait between requests
    if room_type != room_types_to_test[2]:  # Don't wait after last one
        print("Waiting 45 seconds...")
        time.sleep(45)

print("\n=== Summary ===")
print(f"Working room types: {working_rooms}")
print(f"Failed room types: {failed_rooms}")
print("\nNote: Only tested first 3 room types to avoid rate limits")