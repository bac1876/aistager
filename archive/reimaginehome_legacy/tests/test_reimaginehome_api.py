import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
print(f"API Key: {API_KEY[:10]}..." if API_KEY else "No API key found")

# Test with a simple image URL
test_image_url = "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800"

# Test Virtual Staging endpoint
print("\nTesting Virtual Staging API...")

headers = {
    'api-key': API_KEY
}

# First, let's try a simple test without image upload
data = {
    'design_type': 'Interior',
    'design_style': 'Modern',
    'room_type': 'Living Room',
    'ai_intervention': 'Mid',
    'no_design': 1,
    'image_url': test_image_url  # Try with URL first
}

response = requests.post(
    'https://homedesigns.ai/api/v2/virtual_staging',
    data=data,
    headers=headers
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:500]}...")

# If 401, try different auth header formats
if response.status_code == 401:
    print("\nTrying alternative authentication methods...")
    
    # Try Bearer token
    headers_bearer = {
        'Authorization': f'Bearer {API_KEY}'
    }
    response2 = requests.post(
        'https://homedesigns.ai/api/v2/virtual_staging',
        data=data,
        headers=headers_bearer
    )
    print(f"\nWith Bearer token - Status: {response2.status_code}")
    
    # Try X-API-Key
    headers_x_api = {
        'X-API-Key': API_KEY
    }
    response3 = requests.post(
        'https://homedesigns.ai/api/v2/virtual_staging',
        data=data,
        headers=headers_x_api
    )
    print(f"With X-API-Key - Status: {response3.status_code}")