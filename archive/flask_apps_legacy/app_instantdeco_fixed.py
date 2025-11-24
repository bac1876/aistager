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
import threading

load_dotenv('.env.local')

app = Flask(__name__)
CORS(app)

# InstantDecoAI API configuration
INSTANTDECO_API_KEY = os.getenv('INSTANTDECO_API_KEY')
INSTANTDECO_API_URL = 'https://app.instantdeco.ai/api/1.1/wf/request_v2'
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')

# Allow manual override of webhook URL via environment variable
WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL')

print(f"InstantDecoAI API configured: {'Yes' if INSTANTDECO_API_KEY else 'No'}")
print(f"ImgBB API configured: {'Yes' if IMGBB_API_KEY else 'No'}")

# Store pending requests
PENDING_REQUESTS = {}

def get_ngrok_url():
    """Try to get ngrok URL from the local API"""
    try:
        # Ngrok exposes a local API on port 4040
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        data = response.json()
        
        # Find the first HTTPS tunnel
        for tunnel in data.get('tunnels', []):
            if tunnel.get('proto') == 'https':
                return tunnel.get('public_url')
    except:
        pass
    return None

def get_webhook_url(request_context):
    """Get the appropriate webhook URL"""
    # Priority 1: Environment variable
    if WEBHOOK_BASE_URL:
        return f"{WEBHOOK_BASE_URL}/api/webhook"
    
    # Priority 2: Try to detect ngrok
    ngrok_url = get_ngrok_url()
    if ngrok_url:
        print(f"Detected ngrok URL: {ngrok_url}")
        return f"{ngrok_url}/api/webhook"
    
    # Priority 3: Use request context (won't work for webhooks!)
    print("WARNING: Using local URL - webhooks won't work! Start ngrok or set WEBHOOK_BASE_URL")
    return f"{request_context.url_root}api/webhook"

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Room Stager - InstantDecoAI (Fixed)</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Room Stager</h1>
        <p class="text-center text-gray-600 mb-2">Powered by InstantDecoAI</p>
        <p class="text-center text-sm text-gray-500 mb-8">Fixed webhook version</p>
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div id="webhookStatus" class="mb-6 p-4 rounded">
                <!-- Webhook status will be shown here -->
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
        let resultImages = [];
        
        // Check webhook status on load
        window.onload = async () => {
            const response = await fetch('/api/webhook-status');
            const data = await response.json();
            
            const statusDiv = document.getElementById('webhookStatus');
            if (data.webhook_url.includes('ngrok') || data.webhook_url.includes('https://')) {
                statusDiv.className = 'mb-6 p-4 rounded bg-green-50 border-l-4 border-green-500';
                statusDiv.innerHTML = `
                    <p class="text-green-700">
                        ✓ Webhook configured: <code class="text-xs">${data.webhook_url}</code>
                    </p>
                `;
            } else {
                statusDiv.className = 'mb-6 p-4 rounded bg-red-50 border-l-4 border-red-500';
                statusDiv.innerHTML = `
                    <p class="text-red-700 font-semibold">⚠️ Webhook not configured!</p>
                    <p class="text-red-600 text-sm mt-1">
                        Please start ngrok with: <code>ngrok http 5000</code>
                    </p>
                    <p class="text-red-600 text-sm">
                        Or set WEBHOOK_BASE_URL environment variable
                    </p>
                `;
            }
        };
        
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
                const response = await fetch('/api/stage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: imageData,
                        room_type: document.getElementById('roomType').value,
                        design_style: document.getElementById('designStyle').value,
                        num_images: parseInt(document.getElementById('numImages').value)
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const requestId = data.request_id;
                    status.innerHTML = '<div class="bg-green-50 p-4 rounded"><p class="text-green-800">Request submitted! Waiting for AI to stage your room...</p></div>';
                    
                    // Update progress
                    progressBar.style.width = '30%';
                    progressText.textContent = 'AI is working on your room...';
                    
                    // Poll for results
                    let attempts = 0;
                    const maxAttempts = 60; // 2 minutes
                    
                    const pollInterval = setInterval(async () => {
                        attempts++;
                        const progress = Math.min(30 + (attempts * 1), 90);
                        progressBar.style.width = progress + '%';
                        progressText.textContent = `Processing... ${attempts * 2}s`;
                        
                        try {
                            const pollResponse = await fetch(`/api/check-result/${requestId}`);
                            const pollData = await pollResponse.json();
                            
                            if (pollData.completed) {
                                clearInterval(pollInterval);
                                progressBar.style.width = '100%';
                                progressText.textContent = 'Complete!';
                                
                                if (pollData.images && pollData.images.length > 0) {
                                    resultImages = pollData.images;
                                    displayResults(pollData.images);
                                    status.innerHTML = '<div class="bg-green-50 p-4 rounded"><p class="text-green-800 font-semibold">✨ Your room has been staged!</p></div>';
                                } else {
                                    status.innerHTML = '<div class="bg-yellow-50 p-4 rounded"><p class="text-yellow-800">Processing completed but no images received. Please try again.</p></div>';
                                }
                                
                                setTimeout(() => progress.classList.add('hidden'), 2000);
                            } else if (attempts >= maxAttempts) {
                                clearInterval(pollInterval);
                                status.innerHTML = '<div class="bg-yellow-50 p-4 rounded"><p class="text-yellow-800">Processing is taking longer than expected. Check if ngrok is running.</p></div>';
                                progress.classList.add('hidden');
                            }
                        } catch (error) {
                            console.error('Poll error:', error);
                        }
                    }, 2000);
                    
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
                resultDiv.className = 'relative';
                resultDiv.innerHTML = `
                    <img src="${url}" class="w-full rounded shadow-lg" alt="Design ${index + 1}">
                    <a href="${url}" download="staged_room_${index + 1}.jpg" 
                       class="absolute bottom-2 right-2 bg-white bg-opacity-90 px-3 py-1 rounded text-sm hover:bg-opacity-100">
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

@app.route('/api/webhook-status')
def webhook_status():
    """Check webhook configuration status"""
    webhook_url = get_webhook_url(request)
    return jsonify({
        'configured': 'ngrok' in webhook_url or 'https://' in webhook_url,
        'webhook_url': webhook_url
    })

@app.route('/api/stage', methods=['POST'])
def stage_room():
    """Submit staging request to InstantDecoAI"""
    data = request.json
    image_data = data.get('image')
    room_type = data.get('room_type')
    design_style = data.get('design_style')
    num_images = data.get('num_images', 2)
    
    if not image_data or not room_type:
        return jsonify({'success': False, 'error': 'Missing required fields'})
    
    if not INSTANTDECO_API_KEY:
        return jsonify({'success': False, 'error': 'InstantDecoAI API key not configured'})
    
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
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Get proper webhook URL
        webhook_url = get_webhook_url(request)
        print(f"Using webhook URL: {webhook_url}")
        
        # Prepare InstantDecoAI request
        api_payload = {
            "design": design_style,
            "room_type": room_type,
            "transformation_type": "furnish",
            "img_url": image_url,
            "webhook_url": webhook_url,
            "num_images": num_images
        }
        
        # Add block elements for furnish transformation
        api_payload["block_element"] = "wall,floor,ceiling,windowpane,door"
        
        # Store request info
        PENDING_REQUESTS[request_id] = {
            'status': 'pending',
            'created_at': time.time(),
            'images': None
        }
        
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
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                # Map their request_id to ours
                their_request_id = result.get('response', {}).get('request_id')
                if their_request_id:
                    PENDING_REQUESTS[their_request_id] = PENDING_REQUESTS[request_id]
                    del PENDING_REQUESTS[request_id]
                    request_id = their_request_id
                
                return jsonify({
                    'success': True,
                    'request_id': request_id,
                    'webhook_url': webhook_url,
                    'message': 'Staging request submitted successfully!'
                })
        
        # Handle error response
        error_msg = response.json().get('message', 'Failed to submit request')
        return jsonify({'success': False, 'error': error_msg})
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/webhook', methods=['POST'])
def webhook_handler():
    """Handle InstantDecoAI webhook callbacks"""
    try:
        data = request.json
        print(f"Webhook received: {data}")
        
        request_id = data.get('request_id')
        status = data.get('status')
        output = data.get('output')
        
        if request_id in PENDING_REQUESTS:
            if status == 'succeeded' and output:
                # Handle both single image and multiple images
                if isinstance(output, str):
                    images = [output]
                elif isinstance(output, list):
                    images = output
                else:
                    images = []
                
                PENDING_REQUESTS[request_id]['status'] = 'completed'
                PENDING_REQUESTS[request_id]['images'] = images
                print(f"Request {request_id} completed with {len(images)} images")
            else:
                PENDING_REQUESTS[request_id]['status'] = 'failed'
                print(f"Request {request_id} failed")
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/check-result/<request_id>')
def check_result(request_id):
    """Check if results are ready"""
    if request_id in PENDING_REQUESTS:
        request_info = PENDING_REQUESTS[request_id]
        
        if request_info['status'] == 'completed':
            return jsonify({
                'completed': True,
                'images': request_info['images']
            })
        elif request_info['status'] == 'failed':
            return jsonify({
                'completed': True,
                'images': [],
                'error': 'Processing failed'
            })
        else:
            # Still pending
            elapsed = time.time() - request_info['created_at']
            return jsonify({
                'completed': False,
                'elapsed': elapsed
            })
    else:
        return jsonify({
            'completed': False,
            'error': 'Request not found'
        })

@app.route('/health')
def health():
    webhook_url = get_webhook_url(request)
    return jsonify({
        'status': 'healthy',
        'instantdeco_configured': bool(INSTANTDECO_API_KEY),
        'imgbb_configured': bool(IMGBB_API_KEY),
        'webhook_url': webhook_url,
        'webhook_ready': 'ngrok' in webhook_url or 'https://' in webhook_url
    })

# Cleanup old requests periodically
def cleanup_old_requests():
    while True:
        time.sleep(300)  # Every 5 minutes
        current_time = time.time()
        to_remove = []
        
        for request_id, info in PENDING_REQUESTS.items():
            if current_time - info['created_at'] > 3600:  # 1 hour old
                to_remove.append(request_id)
        
        for request_id in to_remove:
            del PENDING_REQUESTS[request_id]
            print(f"Cleaned up old request: {request_id}")

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_requests, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI ROOM STAGER - INSTANTDECOAI (FIXED WEBHOOK)")
    print("="*60)
    
    # Check if ngrok is running
    ngrok_url = get_ngrok_url()
    if ngrok_url:
        print(f"[OK] Ngrok detected: {ngrok_url}")
        print(f"[OK] Webhook URL: {ngrok_url}/api/webhook")
    else:
        print("[WARNING] Ngrok not detected!")
        print("\nTo use webhooks, either:")
        print("1. Start ngrok: ngrok http 5000")
        print("2. Set WEBHOOK_BASE_URL environment variable")
        print("   Example: set WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok.io")
    
    print("="*60)
    app.run(host='0.0.0.0', port=5000, debug=True)