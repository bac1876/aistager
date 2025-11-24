import os
import requests
from dotenv import load_dotenv
import sys

load_dotenv('.env.local')

INSTANTDECO_API_KEY = os.getenv('INSTANTDECO_API_KEY')

# Get request ID from command line or use the one from your recent test
request_id = sys.argv[1] if len(sys.argv) > 1 else "cc17msch3hrj00cr7hzs27y8qc"

print(f"Checking status for request: {request_id}")

# Check status endpoint
status_url = f"https://app.instantdeco.ai/api/1.1/wf/status/{request_id}"

headers = {
    'Authorization': f'Bearer {INSTANTDECO_API_KEY}'
}

try:
    response = requests.get(status_url, headers=headers)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Also try the result endpoint
result_url = f"https://app.instantdeco.ai/api/1.1/wf/result/{request_id}"

try:
    response = requests.get(result_url, headers=headers)
    print(f"\nResult endpoint status: {response.status_code}")
    print(f"Result: {response.text}")
except Exception as e:
    print(f"Error: {e}")