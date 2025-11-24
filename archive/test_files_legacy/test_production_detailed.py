import requests
import json

print("=== Testing Production with Valid Parameters ===\n")

# Test with exact same parameters that work with direct API
payload = {
    "image": "https://i.ibb.co/7JpPyMb/test-image.jpg",
    "transformation_type": "furnish",
    "space_type": "interior", 
    "room_type": "living_room",
    "design_style": "modern",  # Valid design
    "update_flooring": False,
    "block_decorative": True
}

print(f"Payload: {json.dumps(payload, indent=2)}\n")

response = requests.post(
    "https://aistager.vercel.app/api/stage",
    json=payload,
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code != 200:
    print("\nProduction is still failing even with valid parameters!")
    print("Let me check if it's a rate limit issue...")
    
    # Try the health check
    health = requests.get("https://aistager.vercel.app/api/health")
    print(f"\nHealth check status: {health.status_code}")