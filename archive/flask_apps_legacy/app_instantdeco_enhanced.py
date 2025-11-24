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

# Staging history storage (in production, use a database)
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
print("AI ROOM STAGER - ENHANCED VERSION")
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
    <title>AI Room Stager - Enhanced</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Room Stager</h1>
        <p class="text-center text-gray-600 mb-2">Powered by InstantDecoAI</p>
        <p class="text-center text-sm text-gray-500 mb-8">Enhanced Version with Multiple Transformation Options</p>
        
        <div class="max-w-6xl mx-auto">
            <!-- Webhook Status -->
            <div id="webhookStatus" class="mb-6 p-4 rounded bg-gray-50">
                <p class="text-sm">Checking webhook status...</p>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Left Column: Upload and Stage -->
                <div>
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <h2 class="text-xl font-semibold mb-4">Stage a Room</h2>
                        
                        <!-- Upload Section -->
                        <div class="mb-6">
                            <label class="block text-sm font-medium mb-2">Upload Room Photo</label>
                            <input type="file" id="fileInput" accept="image/*" class="hidden">
                            <label for="fileInput" class="cursor-pointer bg-blue-50 border-2 border-dashed border-blue-300 rounded-lg p-6 block text-center hover:bg-blue-100 transition-colors">
                                <svg class="w-10 h-10 mx-auto mb-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                                </svg>
                                <p class="text-gray-700">Click to upload a room photo</p>
                            </label>
                        </div>
                        
                        <!-- Current Image Preview -->
                        <div id="currentImagePreview" class="hidden mb-6">
                            <p class="text-sm font-medium mb-2">Selected Image:</p>
                            <img id="previewImage" class="w-full h-48 object-cover rounded">
                        </div>
                        
                        <!-- Transformation Type -->
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Transformation Type</label>
                            <select id="transformationType" class="w-full p-3 border rounded" onchange="handleTransformationChange()">
                                <option value="furnish">Add Furniture (Virtual Staging)</option>
                                <option value="empty">Remove All Furniture</option>
                                <option value="enhance">Enhance Photo Only</option>
                                <option value="redesign">Redesign Existing Furniture</option>
                                <option value="day_to_dusk">Convert to Evening/Dusk</option>
                            </select>
                        </div>
                        
                        <!-- Room Type (hidden for some transformations) -->
                        <div id="roomTypeSection" class="mb-4">
                            <label class="block text-sm font-medium mb-2">Room Type</label>
                            <select id="roomType" class="w-full p-3 border rounded">
                                <option value="living_room">Living Room</option>
                                <option value="bedroom">Bedroom</option>
                                <option value="kitchen">Kitchen</option>
                                <option value="bathroom">Bathroom</option>
                                <option value="dining_room">Dining Room</option>
                                <option value="home_office">Home Office</option>
                                <option value="kid_bedroom">Kid's Bedroom</option>
                            </select>
                        </div>
                        
                        <!-- Design Styles (hidden for some transformations) -->
                        <div id="designStyleSection" class="mb-6">
                            <label class="block text-sm font-medium mb-2">Select Design Style</label>
                            <div class="grid grid-cols-2 gap-2">
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="radio" name="designStyle" value="modern" class="design-radio" checked>
                                    <span class="text-sm">Contemporary</span>
                                </label>
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="radio" name="designStyle" value="traditional" class="design-radio">
                                    <span class="text-sm">Traditional</span>
                                </label>
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="radio" name="designStyle" value="midcentury" class="design-radio">
                                    <span class="text-sm">Mid-Century Modern</span>
                                </label>
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="radio" name="designStyle" value="rustic" class="design-radio">
                                    <span class="text-sm">Farmhouse</span>
                                </label>
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="radio" name="designStyle" value="artdeco" class="design-radio">
                                    <span class="text-sm">Vintage/Art Deco</span>
                                </label>
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="radio" name="designStyle" value="french" class="design-radio">
                                    <span class="text-sm">Colonial/French</span>
                                </label>
                            </div>
                        </div>
                        
                        <!-- Flooring Option (only for furnish/redesign) -->
                        <div id="flooringSection" class="mb-6">
                            <label class="flex items-center space-x-2 p-3 border rounded hover:bg-gray-50 cursor-pointer">
                                <input type="checkbox" id="updateFlooring" class="w-4 h-4">
                                <span class="text-sm font-medium">Update flooring?</span>
                                <span class="text-xs text-gray-500 ml-2">(unchecked = keep existing floor)</span>
                            </label>
                        </div>
                        
                        <!-- Stage Button -->
                        <button onclick="stageCurrentRoom()" id="stageBtn" class="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors font-medium">
                            Stage This Room
                        </button>
                        
                        <!-- Status -->
                        <div id="status" class="mt-4"></div>
                    </div>
                </div>
                
                <!-- Right Column: Results -->
                <div>
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <h2 class="text-xl font-semibold mb-4">Staging Results</h2>
                        <div id="resultsContainer" class="space-y-4">
                            <p class="text-gray-500 text-center py-8">No rooms staged yet. Upload a photo to get started!</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- All Staged Rooms Section -->
            <div id="allRoomsSection" class="mt-8 hidden">
                <h2 class="text-2xl font-semibold mb-4">All Staged Rooms</h2>
                <div id="allRoomsGrid" class="grid grid-cols-1 md:grid-cols-2 gap-6"></div>
            </div>
        </div>
    </div>
    
    <script>
        let currentImageData = null;
        let stagingJobs = [];
        
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
        
        // Handle transformation type change
        function handleTransformationChange() {
            const transformType = document.getElementById('transformationType').value;
            const roomTypeSection = document.getElementById('roomTypeSection');
            const designStyleSection = document.getElementById('designStyleSection');
            const flooringSection = document.getElementById('flooringSection');
            
            // Show/hide sections based on transformation type
            if (transformType === 'empty' || transformType === 'enhance' || transformType === 'day_to_dusk') {
                roomTypeSection.style.display = 'none';
                designStyleSection.style.display = 'none';
                flooringSection.style.display = 'none';
            } else {
                roomTypeSection.style.display = 'block';
                designStyleSection.style.display = 'block';
                flooringSection.style.display = (transformType === 'furnish' || transformType === 'redesign') ? 'block' : 'none';
            }
        }
        
        // Handle file upload
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = function(event) {
                currentImageData = event.target.result;
                document.getElementById('previewImage').src = currentImageData;
                document.getElementById('currentImagePreview').classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        });
        
        async function stageCurrentRoom() {
            if (!currentImageData) {
                alert('Please upload a room photo first');
                return;
            }
            
            const transformationType = document.getElementById('transformationType').value;
            const roomType = document.getElementById('roomType').value;
            const selectedDesign = document.querySelector('input[name="designStyle"]:checked')?.value || 'modern';
            const updateFlooring = document.getElementById('updateFlooring').checked;
            
            const btn = document.getElementById('stageBtn');
            const status = document.getElementById('status');
            
            btn.disabled = true;
            btn.textContent = 'Processing...';
            
            status.innerHTML = '<div class="bg-blue-50 p-3 rounded mt-2"><p class="text-blue-700">Submitting request...</p></div>';
            
            // Prepare request data
            const requestData = {
                image: currentImageData,
                transformation_type: transformationType,
                update_flooring: updateFlooring
            };
            
            // Add room type and design for relevant transformations
            if (transformationType !== 'empty' && transformationType !== 'enhance' && transformationType !== 'day_to_dusk') {
                requestData.room_type = roomType;
                requestData.design_style = selectedDesign;
            }
            
            try {
                const response = await fetch('/api/stage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const job = {
                        requestId: data.request_id,
                        transformationType: transformationType,
                        design: selectedDesign,
                        roomType: roomType,
                        status: 'processing',
                        originalImage: currentImageData,
                        timestamp: Date.now()
                    };
                    
                    stagingJobs.push(job);
                    status.innerHTML = `<div class="bg-green-50 p-3 rounded mt-2"><p class="text-green-700">✓ Request submitted. Processing...</p></div>`;
                    
                    // Start polling for results
                    pollForResults();
                    
                    // Reset form for next room
                    setTimeout(() => {
                        currentImageData = null;
                        document.getElementById('fileInput').value = '';
                        document.getElementById('currentImagePreview').classList.add('hidden');
                        status.innerHTML = '';
                        btn.disabled = false;
                        btn.textContent = 'Stage This Room';
                    }, 3000);
                } else {
                    status.innerHTML = `<div class="bg-red-50 p-3 rounded mt-2"><p class="text-red-700">Error: ${data.error}</p></div>`;
                    btn.disabled = false;
                    btn.textContent = 'Stage This Room';
                }
            } catch (error) {
                status.innerHTML = '<div class="bg-red-50 p-3 rounded mt-2"><p class="text-red-700">Failed to submit request</p></div>';
                btn.disabled = false;
                btn.textContent = 'Stage This Room';
            }
        }
        
        async function pollForResults() {
            const pollInterval = setInterval(async () => {
                try {
                    const response = await fetch('/api/recent-stagings');
                    const data = await response.json();
                    
                    let hasUpdates = false;
                    
                    stagingJobs.forEach(job => {
                        if (job.status === 'processing') {
                            const staging = data.stagings.find(s => s.request_id === job.requestId);
                            
                            if (staging && staging.webhook_received) {
                                job.status = 'completed';
                                job.outputImages = staging.output_images || [];
                                hasUpdates = true;
                            }
                        }
                    });
                    
                    if (hasUpdates) {
                        updateResults();
                    }
                    
                    // Stop polling if all jobs are complete
                    const processingJobs = stagingJobs.filter(j => j.status === 'processing');
                    if (processingJobs.length === 0) {
                        clearInterval(pollInterval);
                    }
                } catch (error) {
                    console.error('Polling error:', error);
                }
            }, 2000);
            
            // Stop polling after 3 minutes
            setTimeout(() => clearInterval(pollInterval), 180000);
        }
        
        function getTransformationLabel(type) {
            const labels = {
                'furnish': 'Virtual Staging',
                'empty': 'Furniture Removed',
                'enhance': 'Enhanced',
                'redesign': 'Redesigned',
                'day_to_dusk': 'Evening View'
            };
            return labels[type] || type;
        }
        
        function updateResults() {
            const container = document.getElementById('resultsContainer');
            const allRoomsSection = document.getElementById('allRoomsSection');
            const allRoomsGrid = document.getElementById('allRoomsGrid');
            
            // Update recent results
            container.innerHTML = '';
            const recentJobs = stagingJobs.slice(-3).reverse(); // Show last 3 jobs
            
            recentJobs.forEach(job => {
                if (job.status === 'completed') {
                    const jobDiv = document.createElement('div');
                    jobDiv.className = 'border rounded-lg p-3 mb-3';
                    const label = getTransformationLabel(job.transformationType);
                    jobDiv.innerHTML = `
                        <h3 class="font-medium mb-2">${label}</h3>
                        <div class="mt-2">
                            ${job.outputImages.map((img, idx) => `
                                <img src="${img}" class="w-full h-48 object-cover rounded cursor-pointer hover:opacity-90" 
                                     onclick="window.open('${img}', '_blank')" 
                                     title="Click to view full size">
                            `).join('')}
                        </div>
                    `;
                    container.appendChild(jobDiv);
                }
            });
            
            // Update all rooms section
            if (stagingJobs.filter(j => j.status === 'completed').length > 0) {
                allRoomsSection.classList.remove('hidden');
                allRoomsGrid.innerHTML = '';
                
                stagingJobs.filter(j => j.status === 'completed').reverse().forEach(job => {
                    const roomDiv = document.createElement('div');
                    roomDiv.className = 'bg-white rounded-lg shadow-lg p-4';
                    
                    const date = new Date(job.timestamp);
                    const timeStr = date.toLocaleTimeString();
                    const label = getTransformationLabel(job.transformationType);
                    
                    roomDiv.innerHTML = `
                        <div class="flex items-start gap-4 mb-3">
                            <img src="${job.originalImage}" class="w-24 h-24 object-cover rounded">
                            <div>
                                <h3 class="font-semibold">${label}</h3>
                                <p class="text-sm text-gray-600">Staged at ${timeStr}</p>
                            </div>
                        </div>
                        <div class="mt-2">
                            ${job.outputImages.map((img, idx) => `
                                <img src="${img}" class="w-full h-32 object-cover rounded cursor-pointer hover:opacity-90 mb-2" 
                                     onclick="window.open('${img}', '_blank')">
                            `).join('')}
                        </div>
                    `;
                    
                    allRoomsGrid.appendChild(roomDiv);
                });
            }
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
    transformation_type = data.get('transformation_type', 'furnish')
    room_type = data.get('room_type', 'living_room')
    design_style = data.get('design_style', 'modern')
    update_flooring = data.get('update_flooring', False)
    
    if not image_data:
        return jsonify({'success': False, 'error': 'Missing image data'})
    
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
            "transformation_type": transformation_type,
            "img_url": image_url,
            "num_images": 1
        }
        
        # Add webhook if available
        if webhook_url:
            payload["webhook_url"] = webhook_url
        
        # Add parameters based on transformation type
        if transformation_type in ['furnish', 'redesign', 'renovate']:
            payload["room_type"] = room_type
            payload["design"] = design_style
            
            # Handle flooring - only add floor to block_element if NOT updating flooring
            if transformation_type in ['furnish', 'redesign']:
                if update_flooring:
                    # Don't block floor - allow it to be transformed
                    payload["block_element"] = "wall,ceiling,windowpane,door"
                else:
                    # Block floor to keep it unchanged
                    payload["block_element"] = "wall,floor,ceiling,windowpane,door"
        
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
                    'timestamp': datetime.now().isoformat(),
                    'transformation_type': transformation_type,
                    'room_type': room_type,
                    'design_style': design_style,
                    'update_flooring': update_flooring,
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
        app.logger.error(f"Stage room error: {str(e)}")
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