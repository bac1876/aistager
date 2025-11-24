import requests
import base64
import json

# Step 1: Download the image from Dropbox
image_url = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=1"  # dl=1 for direct download
print("Downloading image from Dropbox...")
img_response = requests.get(image_url)
img_response.raise_for_status()

# Step 2: Convert image to base64
img_b64 = base64.b64encode(img_response.content).decode('utf-8')
data_url = f"data:image/jpeg;base64,{img_b64}"

# Step 3: Prepare payload for /api/stage
payload = {
    "image": data_url,
    "space_type": "ST-INT-011",  # Living Room
    "design_theme": "DT-INT-011"  # Modern
}

print("Payload being sent:")
print(json.dumps(payload)[:500] + ("..." if len(json.dumps(payload)) > 500 else ""))

# Step 4: POST to backend API
api_url = "https://aistager.onrender.com/api/stage"
print(f"Posting to {api_url} ...")
response = requests.post(api_url, json=payload)

print(f"Status: {response.status_code}")
try:
    print(json.dumps(response.json(), indent=2))
except Exception:
    print(response.text)