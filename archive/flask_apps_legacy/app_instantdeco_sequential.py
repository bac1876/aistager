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
print("AI ROOM STAGER - SEQUENTIAL MULTI-ROOM")
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
    <title>AI Room Stager - Sequential</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Room Stager</h1>
        <p class="text-center text-gray-600 mb-2">Powered by InstantDecoAI</p>
        <p class="text-center text-sm text-gray-500 mb-8">Stage Multiple Rooms One at a Time</p>
        
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
                        
                        <!-- Room Type -->
                        <div class="mb-4">
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
                        
                        <!-- Design Styles (Multiple Selection) -->
                        <div class="mb-6">
                            <label class="block text-sm font-medium mb-2">Select Design Styles</label>
                            <div class="grid grid-cols-2 gap-2">
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="checkbox" value="modern" class="design-checkbox" checked>
                                    <span class="text-sm">Modern</span>
                                </label>
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="checkbox" value="scandinavian" class="design-checkbox">
                                    <span class="text-sm">Scandinavian</span>
                                </label>
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="checkbox" value="industrial" class="design-checkbox">
                                    <span class="text-sm">Industrial</span>
                                </label>
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="checkbox" value="bohemian" class="design-checkbox">
                                    <span class="text-sm">Bohemian</span>
                                </label>
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="checkbox" value="minimalist" class="design-checkbox">
                                    <span class="text-sm">Minimalist</span>
                                </label>
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="checkbox" value="coastal" class="design-checkbox">
                                    <span class="text-sm">Coastal</span>
                                </label>
                            </div>
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
            
            const selectedDesigns = Array.from(document.querySelectorAll('.design-checkbox:checked'))
                .map(cb => cb.value);
                
            if (selectedDesigns.length === 0) {
                alert('Please select at least one design style');
                return;
            }
            
            const roomType = document.getElementById('roomType').value;
            const btn = document.getElementById('stageBtn');
            const status = document.getElementById('status');
            
            btn.disabled = true;
            btn.textContent = 'Processing...';
            
            status.innerHTML = '<div class="bg-blue-50 p-3 rounded mt-2"><p class="text-blue-700">Submitting staging requests...</p></div>';
            
            // Submit requests for each design style
            const jobId = Date.now();
            const jobs = [];
            
            for (const design of selectedDesigns) {
                try {
                    const response = await fetch('/api/stage', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            image: currentImageData,
                            room_type: roomType,
                            design_style: design,
                            num_images: 1,
                            job_id: `${jobId}-${design}`
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        jobs.push({
                            requestId: data.request_id,
                            design: design,
                            roomType: roomType,
                            jobId: `${jobId}-${design}`,
                            status: 'processing',
                            originalImage: currentImageData
                        });
                    }
                } catch (error) {
                    console.error('Error submitting request:', error);
                }
                
                // Small delay between requests
                await new Promise(resolve => setTimeout(resolve, 300));
            }
            
            if (jobs.length > 0) {
                stagingJobs.push(...jobs);
                status.innerHTML = `<div class="bg-green-50 p-3 rounded mt-2"><p class="text-green-700">✓ Submitted ${jobs.length} staging request(s). Results will appear shortly...</p></div>`;
                
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
                status.innerHTML = '<div class="bg-red-50 p-3 rounded mt-2"><p class="text-red-700">Failed to submit staging requests</p></div>';
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
        
        function updateResults() {
            const container = document.getElementById('resultsContainer');
            const allRoomsSection = document.getElementById('allRoomsSection');
            const allRoomsGrid = document.getElementById('allRoomsGrid');
            
            // Group jobs by timestamp
            const groupedJobs = {};
            stagingJobs.forEach(job => {
                const timestamp = job.jobId.split('-')[0];
                if (!groupedJobs[timestamp]) {
                    groupedJobs[timestamp] = [];
                }
                groupedJobs[timestamp].push(job);
            });
            
            // Update recent results
            container.innerHTML = '';
            const recentTimestamp = Object.keys(groupedJobs).sort((a, b) => b - a)[0];
            if (recentTimestamp) {
                const recentJobs = groupedJobs[recentTimestamp];
                const completedJobs = recentJobs.filter(j => j.status === 'completed');
                const processingJobs = recentJobs.filter(j => j.status === 'processing');
                
                if (processingJobs.length > 0) {
                    container.innerHTML += `<p class="text-amber-600 text-sm mb-2">Processing ${processingJobs.length} design(s)...</p>`;
                }
                
                completedJobs.forEach(job => {
                    const jobDiv = document.createElement('div');
                    jobDiv.className = 'border rounded-lg p-3 mb-3';
                    jobDiv.innerHTML = `
                        <h3 class="font-medium mb-2">${job.design.charAt(0).toUpperCase() + job.design.slice(1)} Style</h3>
                        <div class="mt-2">
                            ${job.outputImages.map((img, idx) => `
                                <img src="${img}" class="w-full h-48 object-cover rounded cursor-pointer hover:opacity-90" 
                                     onclick="window.open('${img}', '_blank')" 
                                     title="Click to view full size">
                            `).join('')}
                        </div>
                    `;
                    container.appendChild(jobDiv);
                });
            }
            
            // Update all rooms section
            if (stagingJobs.filter(j => j.status === 'completed').length > 0) {
                allRoomsSection.classList.remove('hidden');
                allRoomsGrid.innerHTML = '';
                
                Object.entries(groupedJobs).reverse().forEach(([timestamp, jobs]) => {
                    const completedJobs = jobs.filter(j => j.status === 'completed');
                    if (completedJobs.length === 0) return;
                    
                    const roomDiv = document.createElement('div');
                    roomDiv.className = 'bg-white rounded-lg shadow-lg p-4';
                    
                    const date = new Date(parseInt(timestamp));
                    const timeStr = date.toLocaleTimeString();
                    
                    roomDiv.innerHTML = `
                        <div class="flex items-start gap-4 mb-3">
                            <img src="${completedJobs[0].originalImage}" class="w-24 h-24 object-cover rounded">
                            <div>
                                <h3 class="font-semibold">${completedJobs[0].roomType.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</h3>
                                <p class="text-sm text-gray-600">Staged at ${timeStr}</p>
                                <p class="text-sm text-gray-600">${completedJobs.length} style(s)</p>
                            </div>
                        </div>
                        <div class="space-y-2">
                            ${completedJobs.map(job => `
                                <details class="border rounded p-2">
                                    <summary class="cursor-pointer font-medium text-sm">${job.design.charAt(0).toUpperCase() + job.design.slice(1)}</summary>
                                    <div class="mt-2">
                                        ${job.outputImages.map((img, idx) => `
                                            <img src="${img}" class="w-full h-32 object-cover rounded cursor-pointer hover:opacity-90" 
                                                 onclick="window.open('${img}', '_blank')">
                                        `).join('')}
                                    </div>
                                </details>
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
    room_type = data.get('room_type')
    design_style = data.get('design_style')
    num_images = data.get('num_images', 1)
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