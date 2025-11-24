import os
import sys
from dotenv import load_dotenv

# Fix Unicode on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=== Testing Environment Variable Loading ===\n")

# Test 1: Check if .env.local exists
if os.path.exists('.env.local'):
    print("✓ .env.local file exists")
    print(f"  Path: {os.path.abspath('.env.local')}")
    print(f"  Size: {os.path.getsize('.env.local')} bytes")
else:
    print("✗ .env.local file NOT found")

# Test 2: Try different loading methods
print("\n--- Method 1: load_dotenv() ---")
load_dotenv()
key1 = os.getenv('REIMAGINEHOME_API_KEY')
print(f"Result: {key1 if key1 else 'NOT LOADED'}")

print("\n--- Method 2: load_dotenv('.env.local') ---")
load_dotenv('.env.local')
key2 = os.getenv('REIMAGINEHOME_API_KEY')
print(f"Result: {key2 if key2 else 'NOT LOADED'}")

print("\n--- Method 3: load_dotenv(dotenv_path='.env.local') ---")
from pathlib import Path
env_path = Path('.') / '.env.local'
load_dotenv(dotenv_path=env_path)
key3 = os.getenv('REIMAGINEHOME_API_KEY')
print(f"Result: {key3 if key3 else 'NOT LOADED'}")

print("\n--- Method 4: Manual parsing ---")
try:
    with open('.env.local', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if 'REIMAGINEHOME_API_KEY' in line:
                    key, value = line.strip().split('=', 1)
                    print(f"Found: {key} = {value[:10]}...")
except Exception as e:
    print(f"Error reading file: {e}")

print("\n--- All environment variables starting with RE ---")
for key, value in os.environ.items():
    if key.startswith('RE'):
        print(f"{key}: {value[:20]}..." if len(value) > 20 else f"{key}: {value}")