import requests
import base64
import time
import os

# Test the local app
BASE_URL = "http://localhost:5000"

def test_health():
    """Test if the app is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_staging():
    """Test the staging API with a small test image"""
    # Create a small test image (1x1 white pixel)
    test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    payload = {
        "image": test_image,
        "space_type": "ST-INT-011",  # Living Room
        "design_theme": "DT-INT-011"  # Modern
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/stage", json=payload)
        print(f"\nStaging API response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                job_id = data.get('job_id')
                print(f"Job submitted successfully: {job_id}")
                
                # Check job status
                time.sleep(2)
                status_response = requests.get(f"{BASE_URL}/api/check-job/{job_id}")
                print(f"Job status: {status_response.json()}")
                
        return response.status_code == 200
    except Exception as e:
        print(f"Staging test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing local app at", BASE_URL)
    print("-" * 50)
    
    if test_health():
        print("\n[OK] App is running")
        test_staging()
    else:
        print("\n[ERROR] App is not running. Start it with: python app.py")