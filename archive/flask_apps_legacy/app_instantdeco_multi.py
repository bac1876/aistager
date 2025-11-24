from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
import base64
from datetime import datetime
import json
import uuid

load_dotenv('.env.local')

app = Flask(__name__)
CORS(app)

# API Keys
INSTANTDECO_API_KEY = os.getenv('INSTANTDECO_API_KEY')
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')

# API URLs
INSTANTDECO_API_URL = 'https://app.instantdeco.ai/api/1.1/wf/request_v2'
IMGBB_API_URL = 'https://api.imgbb.com/1/upload'

# Staging history storage
staging_history = []

# Auto-detect ngrok URL
def get_webhook_url():
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        tunnels = response.json()
        if tunnels.get('tunnels'):
            public_url = tunnels['tunnels'][0]['public_url']
            return f"{public_url}/api/webhook"
    except:
        pass
    return None

# Display webhook status on startup
webhook_url = get_webhook_url()
print("\n" + "="*60)
print("AI ROOM STAGER - MULTI-DESIGN & MULTI-ROOM")
print("="*60)
if webhook_url:
    print(f"[OK] Ngrok detected: {webhook_url.replace('/api/webhook', '')}")
    print(f"[OK] Webhook URL: {webhook_url}")
else:
    print("[WARNING] Ngrok not detected - webhooks will not work")
print("="*60 + "\n")

print(f"InstantDecoAI API configured: {'Yes' if INSTANTDECO_API_KEY else 'No'}")
print(f"ImgBB API configured: {'Yes' if IMGBB_API_KEY else 'No'}")

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>AI Room Stager - Multi-Design & Multi-Room</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Room Stager</h1>
        <p class="text-center text-gray-600 mb-2">Powered by InstantDecoAI</p>
        <p class="text-center text-sm text-gray-500 mb-8">Multi-Design & Multi-Room Version</p>
        
        <div class="max-w-6xl mx-auto">
            <!-- Webhook Status -->
            <div id="webhookStatus" class="mb-6 p-4 rounded bg-gray-50">
                <p class="text-sm">Checking webhook status...</p>
            </div>
            
            <!-- Upload Section -->
            <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
                <h2 class="text-2xl font-semibold mb-4">Upload Room Photos</h2>
                
                <div class="mb-6">
                    <label class="block text-sm font-medium mb-2">Add Room Photos (Multiple Allowed)</label>
                    <input type="file" id="fileInput" accept="image/*" multiple class="hidden">
                    <label for="fileInput" class="cursor-pointer bg-blue-50 border-2 border-dashed border-blue-300 rounded-lg p-8 block text-center hover:bg-blue-100 transition-colors">
                        <svg class="w-12 h-12 mx-auto mb-3 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                        </svg>
                        <p class="text-gray-700">Click to upload room photos</p>
                        <p class="text-sm text-gray-500 mt-1">You can select multiple images</p>
                    </label>
                </div>
                
                <!-- Uploaded Images Preview -->
                <div id="uploadedImages" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6"></div>
                
                <!-- Design Selection -->
                <div class="mb-6">
                    <label class="block text-sm font-medium mb-2">Select Design Styles (Multiple Allowed)</label>
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                        <label class="flex items-center space-x-2 p-3 border rounded hover:bg-gray-50 cursor-pointer">
                            <input type="checkbox" value="modern" class="design-checkbox">
                            <span>Modern</span>
                        </label>
                        <label class="flex items-center space-x-2 p-3 border rounded hover:bg-gray-50 cursor-pointer">
                            <input type="checkbox" value="scandinavian" class="design-checkbox">
                            <span>Scandinavian</span>
                        </label>
                        <label class="flex items-center space-x-2 p-3 border rounded hover:bg-gray-50 cursor-pointer">
                            <input type="checkbox" value="industrial" class="design-checkbox">
                            <span>Industrial</span>
                        </label>
                        <label class="flex items-center space-x-2 p-3 border rounded hover:bg-gray-50 cursor-pointer">
                            <input type="checkbox" value="bohemian" class="design-checkbox">
                            <span>Bohemian</span>
                        </label>
                        <label class="flex items-center space-x-2 p-3 border rounded hover:bg-gray-50 cursor-pointer">
                            <input type="checkbox" value="minimalist" class="design-checkbox">
                            <span>Minimalist</span>
                        </label>
                        <label class="flex items-center space-x-2 p-3 border rounded hover:bg-gray-50 cursor-pointer">
                            <input type="checkbox" value="coastal" class="design-checkbox">
                            <span>Coastal</span>
                        </label>
                    </div>
                </div>
                
                <!-- Room Type -->
                <div class="mb-6">
                    <label class="block text-sm font-medium mb-2">Room Type</label>
                    <select id="roomType" class="w-full p-3 border rounded">
                        <option value="living_room">Living Room</option>
                        <option value="bedroom">Bedroom</option>
                        <option value="kitchen">Kitchen</option>
                        <option value="bathroom">Bathroom</option>
                        <option value="dining_room">Dining Room</option>
                        <option value="office">Office</option>
                    </select>
                </div>
                
                <!-- Stage Button -->
                <button onclick="stageRooms()" id="stageBtn" class="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors font-medium">
                    Stage All Rooms with Selected Designs
                </button>
            </div>
            
            <!-- Progress Section -->
            <div id="progressSection" class="hidden bg-white rounded-lg shadow-lg p-6 mb-6">
                <h3 class="text-lg font-semibold mb-4">Processing Queue</h3>
                <div id="progressItems"></div>
            </div>
            
            <!-- Results Section -->
            <div id="resultsSection" class="hidden">
                <h2 class="text-2xl font-semibold mb-4">Generated Stagings</h2>
                <div id="resultsGrid"></div>
            </div>
        </div>
    </div>
    
    <script>
        let uploadedImages = [];
        
        // Check webhook status
        fetch('/api/health')
            .then(res => res.json())
            .then(data => {
                const statusEl = document.getElementById('webhookStatus');
                if (data.webhook_ready) {
                    statusEl.innerHTML = `<p class="text-green-700">✓ Webhook ready at: ${data.webhook_url}</p>`;
                    statusEl.classList.add('bg-green-50');
                } else {
                    statusEl.innerHTML = '<p class="text-amber-700">⚠ Webhook not configured - results may be delayed</p>';
                    statusEl.classList.add('bg-amber-50');
                }
            });
        
        // Handle file uploads
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const files = Array.from(e.target.files);
            const preview = document.getElementById('uploadedImages');
            
            files.forEach(file => {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const imageId = Date.now() + Math.random();
                    const imageData = event.target.result;
                    
                    uploadedImages.push({
                        id: imageId,
                        data: imageData,
                        name: file.name
                    });
                    
                    // Add preview
                    const div = document.createElement('div');
                    div.className = 'relative group';
                    div.innerHTML = `
                        <img src="${imageData}" class="w-full h-32 object-cover rounded">
                        <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity rounded flex items-center justify-center">
                            <button onclick="removeImage(${imageId})" class="opacity-0 group-hover:opacity-100 bg-red-500 text-white px-3 py-1 rounded text-sm">
                                Remove
                            </button>
                        </div>
                        <p class="text-xs text-gray-600 mt-1 truncate">${file.name}</p>
                    `;
                    preview.appendChild(div);
                };
                reader.readAsDataURL(file);
            });
        });
        
        function removeImage(imageId) {
            uploadedImages = uploadedImages.filter(img => img.id !== imageId);
            renderUploadedImages();
        }
        
        function renderUploadedImages() {
            const preview = document.getElementById('uploadedImages');
            preview.innerHTML = '';
            
            uploadedImages.forEach(img => {
                const div = document.createElement('div');
                div.className = 'relative group';
                div.innerHTML = `
                    <img src="${img.data}" class="w-full h-32 object-cover rounded">
                    <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity rounded flex items-center justify-center">
                        <button onclick="removeImage(${img.id})" class="opacity-0 group-hover:opacity-100 bg-red-500 text-white px-3 py-1 rounded text-sm">
                            Remove
                        </button>
                    </div>
                    <p class="text-xs text-gray-600 mt-1 truncate">${img.name}</p>
                `;
                preview.appendChild(div);
            });
        }
        
        async function stageRooms() {
            if (uploadedImages.length === 0) {
                alert('Please upload at least one room photo');
                return;
            }
            
            const selectedDesigns = Array.from(document.querySelectorAll('.design-checkbox:checked'))
                .map(cb => cb.value);
                
            if (selectedDesigns.length === 0) {
                alert('Please select at least one design style');
                return;
            }
            
            const roomType = document.getElementById('roomType').value;
            const btn = document.getElementById('stageBtn');
            const progressSection = document.getElementById('progressSection');
            const progressItems = document.getElementById('progressItems');
            
            btn.disabled = true;
            btn.textContent = 'Processing...';
            progressSection.classList.remove('hidden');
            progressItems.innerHTML = '';
            
            // Create progress items for each image/design combination
            const totalJobs = uploadedImages.length * selectedDesigns.length;
            const jobs = [];
            
            uploadedImages.forEach(img => {
                selectedDesigns.forEach(design => {
                    jobs.push({
                        image: img,
                        design: design,
                        id: `${img.id}-${design}`
                    });
                });
            });
            
            // Submit all jobs
            for (const job of jobs) {
                const progressItem = document.createElement('div');
                progressItem.id = `progress-${job.id}`;
                progressItem.className = 'mb-3 p-3 border rounded';
                progressItem.innerHTML = `
                    <div class="flex justify-between items-center">
                        <span class="text-sm">${job.image.name} - ${job.design}</span>
                        <span class="text-sm text-gray-500">Submitting...</span>
                    </div>
                `;
                progressItems.appendChild(progressItem);
                
                try {
                    const response = await fetch('/api/stage', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            image: job.image.data,
                            room_type: roomType,
                            design_style: job.design,
                            num_images: 2,
                            job_id: job.id
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        progressItem.querySelector('span:last-child').textContent = 'Processing...';
                        progressItem.querySelector('span:last-child').classList.add('text-blue-600');
                        
                        // Store request info for tracking
                        job.requestId = data.request_id;
                    } else {
                        progressItem.querySelector('span:last-child').textContent = 'Failed';
                        progressItem.querySelector('span:last-child').classList.add('text-red-600');
                    }
                } catch (error) {
                    progressItem.querySelector('span:last-child').textContent = 'Error';
                    progressItem.querySelector('span:last-child').classList.add('text-red-600');
                }
                
                // Small delay between requests
                await new Promise(resolve => setTimeout(resolve, 500));
            }
            
            btn.textContent = 'Stage All Rooms with Selected Designs';
            btn.disabled = false;
            
            // Start polling for results
            pollForResults(jobs);
        }
        
        async function pollForResults(jobs) {
            const resultsSection = document.getElementById('resultsSection');
            const resultsGrid = document.getElementById('resultsGrid');
            resultsSection.classList.remove('hidden');
            
            let completed = 0;
            const maxAttempts = 120; // 4 minutes
            let attempts = 0;
            
            const pollInterval = setInterval(async () => {
                attempts++;
                
                try {
                    const response = await fetch('/api/recent-stagings');
                    const data = await response.json();
                    
                    jobs.forEach(job => {
                        if (!job.completed && job.requestId) {
                            const staging = data.stagings.find(s => s.request_id === job.requestId);
                            
                            if (staging && staging.webhook_received) {
                                job.completed = true;
                                completed++;
                                
                                // Update progress item
                                const progressItem = document.getElementById(`progress-${job.id}`);
                                if (progressItem) {
                                    progressItem.querySelector('span:last-child').textContent = '✓ Complete';
                                    progressItem.querySelector('span:last-child').className = 'text-sm text-green-600';
                                }
                                
                                // Add to results
                                displayResult(job, staging);
                            }
                        }
                    });
                    
                    if (completed === jobs.length || attempts >= maxAttempts) {
                        clearInterval(pollInterval);
                    }
                } catch (error) {
                    console.error('Polling error:', error);
                }
            }, 2000);
        }
        
        function displayResult(job, staging) {
            const resultsGrid = document.getElementById('resultsGrid');
            
            const resultDiv = document.createElement('div');
            resultDiv.className = 'bg-white rounded-lg shadow-lg p-4 mb-4';
            resultDiv.innerHTML = `
                <h3 class="font-semibold mb-2">${job.image.name} - ${job.design}</h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <p class="text-sm text-gray-600 mb-1">Original</p>
                        <img src="${job.image.data}" class="w-full h-48 object-cover rounded">
                    </div>
                    ${staging.output_images.map((img, idx) => `
                        <div>
                            <p class="text-sm text-gray-600 mb-1">Option ${idx + 1}</p>
                            <img src="${img}" class="w-full h-48 object-cover rounded cursor-pointer hover:opacity-90" onclick="window.open('${img}', '_blank')">
                        </div>
                    `).join('')}
                </div>
            `;
            resultsGrid.appendChild(resultDiv);
        }
    </script>
</body>
</html>
    ''')

@app.route('/api/health')
def health():
    webhook_url = get_webhook_url()
    return jsonify({
        'status': 'healthy',
        'instantdeco_configured': bool(INSTANTDECO_API_KEY),
        'imgbb_configured': bool(IMGBB_API_KEY),
        'webhook_ready': bool(webhook_url),
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
    job_id = data.get('job_id')
    
    if not image_data or not room_type:
        return jsonify({'success': False, 'error': 'Missing required fields'})
    
    if not INSTANTDECO_API_KEY:
        return jsonify({'success': False, 'error': 'InstantDecoAI API key not configured'})
    
    try:
        # Extract base64 data
        base64_data = image_data.split(',')[1] if ',' in image_data else image_data
        
        # Upload to ImgBB first
        if not IMGBB_API_KEY:
            return jsonify({'success': False, 'error': 'ImgBB API key not configured'})
        
        imgbb_response = requests.post(
            IMGBB_API_URL,
            data={
                'key': IMGBB_API_KEY,
                'image': base64_data
            }
        )
        
        if imgbb_response.status_code != 200:
            return jsonify({'success': False, 'error': 'Failed to upload image to ImgBB'})
        
        imgbb_data = imgbb_response.json()
        if not imgbb_data.get('success'):
            return jsonify({'success': False, 'error': 'ImgBB upload failed'})
        
        image_url = imgbb_data['data']['url']
        
        # Get webhook URL
        webhook_url = get_webhook_url()
        
        # Prepare InstantDecoAI payload
        payload = {
            "design": design_style,
            "room_type": room_type,
            "transformation_type": "furnish",
            "block_element": "wall,floor,ceiling,windowpane,door",
            "img_url": image_url,
            "num_images": num_images
        }
        
        if webhook_url:
            payload["webhook_url"] = webhook_url
        
        # Call InstantDecoAI
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {INSTANTDECO_API_KEY}'
        }
        
        response = requests.post(INSTANTDECO_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                request_id = result.get('response', {}).get('request_id')
                
                # Store in history
                staging_history.append({
                    'request_id': request_id,
                    'job_id': job_id,
                    'timestamp': datetime.now().isoformat(),
                    'room_type': room_type,
                    'design_style': design_style,
                    'status': 'processing',
                    'webhook_received': False,
                    'input_image': image_url
                })
                
                return jsonify({
                    'success': True,
                    'request_id': request_id,
                    'webhook_url': webhook_url,
                    'message': 'Staging request submitted successfully!'
                })
        
        return jsonify({'success': False, 'error': 'InstantDecoAI API error'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Handle InstantDecoAI webhook"""
    try:
        data = request.json
        request_id = data.get('request_id')
        
        # Find the staging request
        for staging in staging_history:
            if staging['request_id'] == request_id:
                staging['webhook_received'] = True
                staging['webhook_timestamp'] = datetime.now().isoformat()
                staging['status'] = data.get('status', 'completed')
                
                # Extract output images
                output = data.get('output', '')
                if output and isinstance(output, str):
                    # Split by comma and clean up URLs
                    images = [url.strip() for url in output.split(',') if url.strip()]
                    staging['output_images'] = images
                
                break
        
        return jsonify({'status': 'ok'})
    except Exception as e:
        app.logger.error(f"Webhook error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/recent-stagings')
def recent_stagings():
    """Get recent staging requests"""
    # Return last 50 stagings, newest first
    recent = sorted(staging_history, key=lambda x: x['timestamp'], reverse=True)[:50]
    return jsonify({'stagings': recent})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)