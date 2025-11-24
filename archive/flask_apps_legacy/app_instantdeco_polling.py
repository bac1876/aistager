import os
import time
import requests
import base64
import uuid
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv
import json
from datetime import datetime
import hashlib

load_dotenv('.env.local')

app = Flask(__name__)
CORS(app)

# InstantDecoAI API configuration
INSTANTDECO_API_KEY = os.getenv('INSTANTDECO_API_KEY')
INSTANTDECO_API_URL = 'https://app.instantdeco.ai/api/1.1/wf/request_v2'
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')

print(f"InstantDecoAI API configured: {'Yes' if INSTANTDECO_API_KEY else 'No'}")
print(f"ImgBB API configured: {'Yes' if IMGBB_API_KEY else 'No'}")

# Since InstantDecoAI requires webhooks, we'll simulate polling
# by using a public webhook service for testing
WEBHOOK_SITE_URL = "https://webhook.site"  # You'll need to get a unique URL from webhook.site

# HTML template (same as before but with updated title)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Room Stager - InstantDecoAI (Polling Version)</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Room Stager</h1>
        <p class="text-center text-gray-600 mb-2">Powered by InstantDecoAI</p>
        <p class="text-center text-sm text-gray-500 mb-8">Virtual staging for empty rooms (Polling Version)</p>
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="bg-yellow-50 p-4 rounded mb-6">
                <p class="text-yellow-800 text-sm">
                    <strong>Note:</strong> This version simulates polling. For production use, 
                    implement proper webhook handling or use a service like webhook.site for testing.
                </p>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Upload Your Empty Room Photo</label>
                <input type="file" id="fileInput" accept="image/*" class="w-full p-2 border rounded">
                <img id="preview" class="mt-4 max-h-64 mx-auto hidden rounded shadow">
            </div>
            
            <div class="grid grid-cols-2 gap-4 mb-6">
                <div>
                    <label class="block text-sm font-medium mb-2">Room Type</label>
                    <select id="roomType" class="w-full p-3 border rounded">
                        <option value="living_room">Living Room</option>
                        <option value="bedroom">Bedroom</option>
                        <option value="dining_room">Dining Room</option>
                        <option value="home_office">Home Office</option>
                        <option value="kid_bedroom">Kids Bedroom</option>
                        <option value="kitchen">Kitchen</option>
                        <option value="bathroom">Bathroom</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-2">Design Style</label>
                    <select id="designStyle" class="w-full p-3 border rounded">
                        <option value="modern">Modern</option>
                        <option value="scandinavian">Scandinavian</option>
                        <option value="industrial">Industrial</option>
                        <option value="bohemian">Bohemian</option>
                        <option value="french">French</option>
                        <option value="midcentury">Mid-Century</option>
                        <option value="coastal">Coastal</option>
                        <option value="rustic">Rustic</option>
                        <option value="artdeco">Art Deco</option>
                        <option value="minimalist">Minimalist</option>
                    </select>
                </div>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Transformation Type</label>
                <select id="transformationType" class="w-full p-3 border rounded">
                    <option value="furnish">Furnish - Add furniture to empty room</option>
                    <option value="renovate">Renovate - Enhanced transformation</option>
                    <option value="redesign">Redesign - For furnished rooms</option>
                </select>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Number of Designs</label>
                <select id="numImages" class="w-full p-3 border rounded">
                    <option value="1">1 Design</option>
                    <option value="2" selected>2 Designs</option>
                    <option value="3">3 Designs</option>
                    <option value="4">4 Designs</option>
                </select>
            </div>
            
            <button id="stageBtn" class="w-full bg-blue-500 text-white py-3 rounded hover:bg-blue-600 font-semibold">
                Stage My Room
            </button>
            
            <div id="status" class="mt-4"></div>
            <div id="progress" class="mt-4 hidden">
                <div class="bg-gray-200 rounded-full h-2">
                    <div id="progressBar" class="bg-blue-500 h-2 rounded-full transition-all duration-500" style="width: 0%"></div>
                </div>
                <p id="progressText" class="text-sm text-gray-600 mt-2 text-center"></p>
            </div>
            
            <div id="result" class="mt-6 hidden">
                <h3 class="text-lg font-semibold mb-4">Your Staged Room:</h3>
                <div id="resultsGrid" class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <!-- Results will be inserted here -->
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let imageData = null;
        
        document.getElementById('fileInput').addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 10 * 1024 * 1024) {
                    alert('Please select an image smaller than 10MB');
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = (event) => {
                    imageData = event.target.result;
                    document.getElementById('preview').src = imageData;
                    document.getElementById('preview').classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            }
        });
        
        document.getElementById('stageBtn').addEventListener('click', async () => {
            if (!imageData) {
                alert('Please upload a room photo first');
                return;
            }
            
            const btn = document.getElementById('stageBtn');
            const status = document.getElementById('status');
            const progress = document.getElementById('progress');
            const progressBar = document.getElementById('progressBar');
            const progressText = document.getElementById('progressText');
            
            btn.disabled = true;
            btn.textContent = 'Processing...';
            progress.classList.remove('hidden');
            document.getElementById('result').classList.add('hidden');
            
            // Show initial progress
            progressBar.style.width = '10%';
            progressText.textContent = 'Uploading image...';
            
            try {
                const response = await fetch('/api/stage-polling', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: imageData,
                        room_type: document.getElementById('roomType').value,
                        design_style: document.getElementById('designStyle').value,
                        transformation_type: document.getElementById('transformationType').value,
                        num_images: parseInt(document.getElementById('numImages').value)
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    status.innerHTML = '<div class="bg-blue-50 p-4 rounded"><p class="text-blue-800">Request submitted! InstantDecoAI is working on your room...</p></div>';
                    
                    // Update progress
                    progressBar.style.width = '50%';
                    progressText.textContent = 'AI is staging your room...';
                    
                    // Note about webhook requirement
                    setTimeout(() => {
                        progressBar.style.width = '100%';
                        progressText.textContent = 'Note: InstantDecoAI requires webhooks';
                        
                        status.innerHTML = `
                            <div class="bg-yellow-50 p-4 rounded">
                                <p class="text-yellow-800 font-semibold mb-2">⚠️ Webhook Required</p>
                                <p class="text-yellow-700 text-sm mb-2">
                                    InstantDecoAI requires a webhook URL to receive results. 
                                    For local testing, you can:
                                </p>
                                <ol class="text-yellow-700 text-sm list-decimal list-inside space-y-1">
                                    <li>Use ngrok to expose your local webhook endpoint</li>
                                    <li>Use webhook.site to receive the callback</li>
                                    <li>Deploy to a public server</li>
                                </ol>
                                <p class="text-yellow-700 text-sm mt-2">
                                    Request ID: <code class="bg-yellow-100 px-1">${data.request_id || 'N/A'}</code>
                                </p>
                            </div>
                        `;
                        
                        progress.classList.add('hidden');
                    }, 3000);
                    
                } else {
                    progress.classList.add('hidden');
                    status.innerHTML = `<div class="bg-red-50 p-4 rounded"><p class="text-red-800">Error: ${data.error}</p></div>`;
                }
            } catch (error) {
                progress.classList.add('hidden');
                status.innerHTML = `<div class="bg-red-50 p-4 rounded"><p class="text-red-800">Error: ${error.message}</p></div>`;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Stage My Room';
            }
        });
        
        function displayResults(images) {
            document.getElementById('result').classList.remove('hidden');
            const resultsGrid = document.getElementById('resultsGrid');
            resultsGrid.innerHTML = '';
            
            images.forEach((url, index) => {
                const resultDiv = document.createElement('div');
                resultDiv.innerHTML = `
                    <img src="${url}" class="w-full rounded shadow-lg" alt="Design ${index + 1}">
                    <a href="${url}" download="staged_room_${index + 1}.jpg" 
                       class="mt-2 inline-block bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600">
                        Download
                    </a>
                `;
                resultsGrid.appendChild(resultDiv);
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stage-polling', methods=['POST'])
def stage_room_polling():
    """Submit staging request to InstantDecoAI with polling simulation"""
    data = request.json
    image_data = data.get('image')
    room_type = data.get('room_type')
    design_style = data.get('design_style')
    transformation_type = data.get('transformation_type', 'furnish')
    num_images = data.get('num_images', 2)
    
    if not image_data or not room_type:
        return jsonify({'success': False, 'error': 'Missing required fields'})
    
    if not INSTANTDECO_API_KEY:
        return jsonify({'success': False, 'error': 'InstantDecoAI API key not configured. Please add INSTANTDECO_API_KEY to .env.local'})
    
    try:
        # Extract base64 data
        base64_data = image_data.split(',')[1] if ',' in image_data else image_data
        
        # Upload to ImgBB first
        if not IMGBB_API_KEY:
            return jsonify({'success': False, 'error': 'Image hosting not configured'})
            
        print("Uploading to ImgBB...")
        imgbb_response = requests.post(
            'https://api.imgbb.com/1/upload',
            data={
                'key': IMGBB_API_KEY,
                'image': base64_data,
                'name': f'room_{int(time.time())}'
            },
            timeout=30
        )
        
        if imgbb_response.status_code != 200 or not imgbb_response.json().get('success'):
            return jsonify({'success': False, 'error': 'Failed to upload image'})
            
        image_url = imgbb_response.json()['data']['url']
        print(f"Image uploaded: {image_url}")
        
        # For demonstration, we'll need a webhook URL
        # In production, you'd use your actual webhook endpoint
        webhook_url = "https://webhook.site/your-unique-url"  # Replace with actual webhook.site URL
        
        # Prepare InstantDecoAI request
        api_payload = {
            "design": design_style,
            "room_type": room_type,
            "transformation_type": transformation_type,
            "img_url": image_url,
            "webhook_url": webhook_url,
            "num_images": num_images
        }
        
        # Add block elements for furnish transformation
        if transformation_type == 'furnish':
            # Keep structural elements unchanged
            api_payload["block_element"] = "wall,floor,ceiling,windowpane,door"
        
        print(f"Sending request to InstantDecoAI: {api_payload}")
        
        # Send request to InstantDecoAI
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {INSTANTDECO_API_KEY}'
        }
        
        response = requests.post(
            INSTANTDECO_API_URL,
            headers=headers,
            json=api_payload,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                request_id = result.get('response', {}).get('request_id', 'unknown')
                
                return jsonify({
                    'success': True,
                    'request_id': request_id,
                    'message': 'Request submitted! Check webhook.site for results.',
                    'webhook_info': 'InstantDecoAI will send results to the webhook URL'
                })
        
        # Handle error response
        error_msg = response.json().get('message', 'Failed to submit request')
        return jsonify({'success': False, 'error': error_msg})
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'instantdeco_configured': bool(INSTANTDECO_API_KEY),
        'imgbb_configured': bool(IMGBB_API_KEY),
        'note': 'This version demonstrates InstantDecoAI integration but requires webhook setup'
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI ROOM STAGER - INSTANTDECOAI INTEGRATION (Polling Demo)")
    print("="*60)
    print("IMPORTANT: InstantDecoAI requires webhooks!")
    print("")
    print("To test this integration:")
    print("1. Get your InstantDecoAI API key")
    print("2. Add it to .env.local as INSTANTDECO_API_KEY")
    print("3. Set up a webhook receiver:")
    print("   Option A: Use ngrok (recommended)")
    print("   - Install: https://ngrok.com")
    print("   - Run: ngrok http 5000")
    print("   - Use the ngrok URL in app_instantdeco.py")
    print("")
    print("   Option B: Use webhook.site for testing")
    print("   - Go to https://webhook.site")
    print("   - Copy your unique URL")
    print("   - Update webhook_url in the code")
    print("")
    print("This demo version shows how to make the API call")
    print("but cannot receive results without a webhook.")
    print("="*60)
    app.run(host='0.0.0.0', port=5000, debug=True)