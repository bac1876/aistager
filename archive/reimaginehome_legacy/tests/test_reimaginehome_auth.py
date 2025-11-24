import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
print(f"API Key: {API_KEY[:10]}..." if API_KEY else "No API key found")

# Test different authentication methods
auth_methods = [
    ('Authorization', f'Token {API_KEY}'),
    ('Authorization', API_KEY),
    ('token', API_KEY),
    ('access_token', API_KEY),
    ('api_key', API_KEY),
    ('apikey', API_KEY),
]

test_data = {
    'design_type': 'Interior',
    'design_style': 'Modern',
    'room_type': 'Living Room',
    'ai_intervention': 'Mid',
    'no_design': 1
}

print("\nTrying different authentication methods...\n")

for header_name, header_value in auth_methods:
    headers = {header_name: header_value}
    
    response = requests.post(
        'https://homedesigns.ai/api/v2/virtual_staging',
        data=test_data,
        headers=headers
    )
    
    print(f"{header_name}: {header_value[:20]}... - Status: {response.status_code}")
    if response.status_code != 401:
        print(f"Success! Response: {response.text[:200]}")
        break
    else:
        print(f"Error: {response.text[:100]}\n")

# Also try as a parameter in the request
print("\nTrying as parameter in request body...")
test_data['api_key'] = API_KEY
response = requests.post(
    'https://homedesigns.ai/api/v2/virtual_staging',
    data=test_data
)
print(f"As body parameter - Status: {response.status_code}")
print(f"Response: {response.text[:200]}")