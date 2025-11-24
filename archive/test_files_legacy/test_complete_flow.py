import requests
import base64
import time

# Test the complete flow through our app
print("Testing complete flow through the polling app...")

# First, let's download the Dropbox image
dropbox_url = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=1"
print(f"Downloading image from: {dropbox_url}")

image_response = requests.get(dropbox_url)
if image_response.status_code != 200:
    print("Failed to download image")
    exit()

# Convert to base64
image_base64 = base64.b64encode(image_response.content).decode('utf-8')
image_data_url = f"data:image/jpeg;base64,{image_base64}"

print("Image downloaded and converted to base64")

# Test our app's staging endpoint
print("\nTesting /api/stage-with-polling endpoint...")
response = requests.post(
    'http://localhost:5000/api/stage-with-polling',
    json={
        'image': image_data_url,
        'space_type': 'ST-INT-011',
        'design_theme': ''
    }
)

print(f"Response status: {response.status_code}")
data = response.json()
print(f"Response data: {data}")

if data.get('success'):
    job_id = data['job_id']
    print(f"\nJob submitted! ID: {job_id}")
    print("Now polling for results...")
    
    # Poll for results
    for i in range(30):
        time.sleep(2)
        print(f"\nPolling attempt {i+1}/30...")
        
        poll_response = requests.get(f'http://localhost:5000/api/poll-result/{job_id}')
        poll_data = poll_response.json()
        print(f"Poll response: {poll_data}")
        
        if poll_data.get('completed'):
            if poll_data.get('output_url'):
                print(f"\n✅ SUCCESS! Staged image URL: {poll_data['output_url']}")
                print("\nYou can view this image in your browser!")
            else:
                print("\n❌ Completed but no image URL returned")
            break
else:
    print(f"\n❌ Error: {data.get('error')}")