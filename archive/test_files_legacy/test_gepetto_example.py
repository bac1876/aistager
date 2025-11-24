
# Example test script for Gepetto API
import requests

GEPETTO_API_KEY = "your_api_key_here"
TEST_IMAGE = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=1"

headers = {"Authorization": f"Bearer {GEPETTO_API_KEY}"}

# Virtual staging request
response = requests.post(
    "https://api.gepetto.app/v1/furnish",
    headers=headers,
    json={
        "image_url": TEST_IMAGE,
        "room_type": "living_room",
        "style": "modern",
        "quality": "high"
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Staged image: {result['output_url']}")
else:
    print(f"Error: {response.status_code}")
