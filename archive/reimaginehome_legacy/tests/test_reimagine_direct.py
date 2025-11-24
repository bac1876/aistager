import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
print(f"Testing ReimagineHome API Key: {API_KEY[:10]}...")

# Test different possible API endpoints
endpoints = [
    'https://api.reimaginehome.ai/v1/staging',
    'https://api.reimaginehome.ai/v1/generate',
    'https://api.reimaginehome.ai/v1/transform',
    'https://api.reimaginehome.ai/v1/redesign',
    'https://reimaginehome.ai/api/v1/staging',
    'https://www.reimaginehome.ai/api/generate',
]

# Test different auth methods
auth_configs = [
    {'headers': {'Authorization': f'Bearer {API_KEY}'}},
    {'headers': {'Authorization': f'Token {API_KEY}'}},
    {'headers': {'Authorization': API_KEY}},
    {'headers': {'api-key': API_KEY}},
    {'headers': {'x-api-key': API_KEY}},
    {'headers': {'apikey': API_KEY}},
    {'params': {'api_key': API_KEY}},
    {'params': {'apikey': API_KEY}},
    {'params': {'key': API_KEY}},
]

# Simple test payload
test_data = {
    'style': 'modern'
}

print("\nTesting various endpoints and authentication methods...")
print("=" * 60)

success_found = False

for endpoint in endpoints:
    if success_found:
        break
        
    print(f"\nTesting endpoint: {endpoint}")
    
    for i, auth_config in enumerate(auth_configs):
        try:
            if 'headers' in auth_config:
                response = requests.post(
                    endpoint,
                    json=test_data,
                    headers=auth_config['headers'],
                    timeout=5
                )
            else:
                response = requests.post(
                    endpoint,
                    json=test_data,
                    params=auth_config['params'],
                    timeout=5
                )
            
            if response.status_code != 401 and response.status_code != 403:
                print(f"  ✓ Auth method {i+1}: Status {response.status_code}")
                print(f"    Response: {response.text[:200]}")
                if response.status_code == 200:
                    success_found = True
                    print(f"\n🎉 SUCCESS! Working configuration found:")
                    print(f"   Endpoint: {endpoint}")
                    print(f"   Auth: {auth_config}")
                    break
            elif response.status_code == 401:
                print(f"  ✗ Auth method {i+1}: 401 Unauthorized")
            else:
                print(f"  ! Auth method {i+1}: Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"  - Auth method {i+1}: Connection error - {str(e)[:50]}")

if not success_found:
    print("\n❌ No working configuration found.")
    print("\nPossible issues:")
    print("1. The API key might not be activated yet")
    print("2. You might need to complete email verification")
    print("3. The API might require a paid plan")
    print("4. The API endpoints might be different than documented")
    print("\nTry:")
    print("1. Log into reimaginehome.ai dashboard")
    print("2. Check if there are any activation steps needed")
    print("3. Contact their support at info@reimaginehome.ai")