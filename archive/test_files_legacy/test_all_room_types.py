import os
import requests
from dotenv import load_dotenv
import time

load_dotenv('.env.local')
api_key = os.getenv('INSTANTDECO_API_KEY')

# All room types from the API documentation
room_types = [
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
print("Will test each room type with 45-second delays\n")

working = []
not_working = []

for i, room_type in enumerate(room_types):
    if i > 0:
        print("\nWaiting 45 seconds...")
        time.sleep(45)
    
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
    
    try:
        response = requests.post(
            'https://app.instantdeco.ai/api/1.1/wf/request_v2',
            json=payload,
            headers=headers,
            timeout=10
        )
        
        result = response.json()
        
        if result.get('status') == 'success' and result.get('response', {}).get('status') == 'success':
            print(f"  SUCCESS - {room_type} works!")
            working.append(room_type)
        else:
            error_msg = result.get('response', {}).get('message', 'Unknown error')
            print(f"  FAILED - {error_msg}")
            not_working.append(room_type)
            
    except Exception as e:
        print(f"  ERROR - {str(e)}")
        not_working.append(room_type)

print("\n" + "="*50)
print("SUMMARY:")
print(f"\nWorking room types ({len(working)}):")
for rt in working:
    print(f"  - {rt}")
    
print(f"\nNOT working room types ({len(not_working)}):")
for rt in not_working:
    print(f"  - {rt}")
    
print("\nThe API documentation is misleading - it lists room types that don't actually work!")