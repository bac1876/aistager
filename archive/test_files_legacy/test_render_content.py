import requests
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=== Testing Render Homepage Content ===\n")

try:
    response = requests.get("https://aistager.onrender.com", timeout=10)
    print(f"Status: {response.status_code}")
    
    # Look for key phrases in the HTML
    content = response.text
    
    if "Professional Virtual Staging with AI" in content:
        print("✗ OLD VERSION: Found 'Professional Virtual Staging with AI'")
    elif "Transform Your Rooms with AI" in content:
        print("✓ NEW VERSION: Found 'Transform Your Rooms with AI'")
    elif "AI Room Stager" in content:
        print("? Found 'AI Room Stager' but unclear which version")
    else:
        print("? Unknown version")
    
    # Check for specific UI elements
    if "Your Recent Stagings" in content:
        print("✓ Has recent stagings section (new version)")
    
    if "Stage My Room" in content:
        print("✓ Has 'Stage My Room' button")
        
    # Check first 500 characters
    print("\nFirst 500 characters of response:")
    print(content[:500])
    
except Exception as e:
    print(f"Error: {e}")