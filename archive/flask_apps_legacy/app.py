import os
import time
import requests
import base64
from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import json
from datetime import datetime
import uuid
import hashlib
import io
import cloudinary
import cloudinary.uploader

load_dotenv('.env.local')  # Explicitly load .env.local

app = Flask(__name__)
CORS(app)

# Get API key from environment
REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')

# ImgBB configuration (primary upload service)
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')

# Cloudinary configuration (backup)
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET
    )
    CLOUDINARY_CONFIGURED = True
else:
    CLOUDINARY_CONFIGURED = False

# Store staging results in memory
STAGING_JOBS = {}
COMPLETED_STAGINGS = {}
TEMP_IMAGES = {}  # Store images temporarily

print("=== UNIQUE DEPLOYMENT TEST: 12345 ===")
print(f"ReimagineHome API configured: {'Yes' if REIMAGINEHOME_API_KEY else 'No'}")
print(f"ImgBB configured: {'Yes' if IMGBB_API_KEY else 'No'}")
print(f"Cloudinary configured: {'Yes' if CLOUDINARY_CONFIGURED else 'No'}")
print(f"App version: Production v2.0 - {datetime.now().isoformat()}")

# HTML template with results display
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Room Stager</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Room Stager</h1>
        <p class="text-center text-gray-600 mb-8">Transform Your Rooms with AI</p>
        <!-- Version: 2.0 Fixed -->
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Upload Your Room Photo</label>
                <input type="file" id="fileInput" accept="image/*" class="w-full p-2 border rounded">
                <img id="preview" class="mt-4 max-h-64 mx-auto hidden rounded shadow">
            </div>
            
            <div class="grid grid-cols-2 gap-4 mb-6">
                <div>
                    <label class="block text-sm font-medium mb-2">Room Type</label>
                    <select id="spaceType" class="w-full p-3 border rounded">
                        <option value="ST-INT-011">Living Room</option>
                        <option value="ST-INT-003">Bedroom</option>
                        <option value="ST-INT-009">Kitchen</option>
                        <option value="ST-INT-002">Bathroom</option>
                        <option value="ST-INT-004">Dining Room</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-2">Design Style</label>
                    <select id="designTheme" class="w-full p-3 border rounded">
                        <option value="">AI Decides</option>
                        <option value="DT-INT-011">Modern</option>
                        <option value="DT-INT-003">Contemporary</option>
                        <option value="DT-INT-013">Scandinavian</option>
                        <option value="DT-INT-010">Minimal</option>
                    </select>
                </div>
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
            
            <!-- Results Section -->
            <div id="results" class="mt-6"></div>
            
            <!-- Previous Stagings -->
            <div class="mt-8 border-t pt-6">
                <h3 class="text-lg font-semibold mb-4">Your Recent Stagings</h3>
                <div id="recentStagings" class="space-y-4"></div>
            </div>
        </div>
    </div>
    
    <script>
        let imageData = null;
        let currentJobId = null;
        
        // Check for recent stagings on load
        window.addEventListener('load', loadRecentStagings);
        
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
            const btn = document.getElementById('stageBtn');
            const status = document.getElementById('status');
            const results = document.getElementById('results');
            
            if (!imageData) {
                alert('Please upload a room photo first');
                return;
            }
            
            const spaceType = document.getElementById('spaceType').value;
            const designTheme = document.getElementById('designTheme').value;
            
            btn.disabled = true;
            btn.textContent = 'Processing...';
            showProgress(10, 'Uploading image...');
            
            try {
                const response = await fetch('/api/stage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: imageData,
                        space_type: spaceType,
                        design_theme: designTheme
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentJobId = data.job_id;
                    
                    status.innerHTML = `
                        <div class="bg-green-50 p-4 rounded">
                            <p class="text-green-800 font-semibold">✓ Staging in progress!</p>
                            <p class="text-sm text-green-600 mt-1">Job ID: ${data.job_id}</p>
                        </div>
                    `;
                    
                    // Start polling for results
                    showProgress(50, 'AI is staging your room...');
                    pollForResults(currentJobId);
                    
                } else {
                    hideProgress();
                    status.innerHTML = `
                        <div class="bg-red-50 p-4 rounded">
                            <p class="text-red-800 font-semibold">✗ Error</p>
                            <p class="text-sm text-red-600 mt-1">${data.error}</p>
                        </div>
                    `;
                }
            } catch (error) {
                hideProgress();
                status.innerHTML = `
                    <div class="bg-red-50 p-4 rounded">
                        <p class="text-red-800">Error: ${error.message}</p>
                    </div>
                `;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Stage My Room';
            }
        });
        
        function showProgress(percent, text) {
            const progress = document.getElementById('progress');
            const progressBar = document.getElementById('progressBar');
            const progressText = document.getElementById('progressText');
            
            progress.classList.remove('hidden');
            progressBar.style.width = percent + '%';
            progressText.textContent = text;
        }
        
        function hideProgress() {
            document.getElementById('progress').classList.add('hidden');
        }
        
        async function pollForResults(jobId) {
            const maxAttempts = 30; // 60 seconds
            let attempts = 0;
            
            const interval = setInterval(async () => {
                attempts++;
                
                const percent = Math.min(50 + (attempts * 1.5), 95);
                showProgress(percent, 'Processing... (' + Math.round(attempts * 2) + 's)');
                
                try {
                    const response = await fetch(`/api/check-job/${jobId}`);
                    const data = await response.json();
                    
                    if (data.completed) {
                        clearInterval(interval);
                        showProgress(100, 'Complete!');
                        displayResults(data.result);
                        loadRecentStagings();
                        setTimeout(hideProgress, 2000);
                    } else if (attempts >= maxAttempts) {
                        clearInterval(interval);
                        hideProgress();
                        document.getElementById('status').innerHTML = `
                            <div class="bg-yellow-50 p-4 rounded">
                                <p class="text-yellow-800">Processing is taking longer than expected.</p>
                                <p class="text-sm text-yellow-600 mt-1">Check back in a minute or refresh the page.</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    console.error('Poll error:', error);
                }
            }, 2000);
        }
        
        function displayResults(result) {
            const results = document.getElementById('results');
            
            if (result.output_urls && result.output_urls.length > 0) {
                results.innerHTML = `
                    <div class="bg-green-50 p-4 rounded mb-4">
                        <p class="text-green-800 font-semibold">🎉 Your room has been staged!</p>
                    </div>
                    <div class="grid grid-cols-1 gap-4">
                        ${result.output_urls.map((url, index) => `
                            <div class="border rounded overflow-hidden">
                                <img src="${url}" class="w-full" alt="Staged room">
                                <div class="p-2 bg-gray-50">
                                    <a href="${url}" target="_blank" class="text-sm text-blue-600 hover:underline">
                                        View full size ↗
                                    </a>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            } else {
                results.innerHTML = `
                    <div class="bg-blue-50 p-4 rounded">
                        <p class="text-blue-800">Staging completed! Results are being processed.</p>
                    </div>
                `;
            }
        }
        
        async function loadRecentStagings() {
            try {
                const response = await fetch('/api/recent-stagings');
                const data = await response.json();
                
                const container = document.getElementById('recentStagings');
                
                if (data.stagings && data.stagings.length > 0) {
                    container.innerHTML = data.stagings.map(staging => `
                        <div class="border rounded p-4 bg-gray-50">
                            <div class="flex justify-between items-start mb-2">
                                <span class="text-sm font-medium">Job: ${staging.job_id}</span>
                                <span class="text-xs text-gray-500">${staging.timestamp}</span>
                            </div>
                            ${staging.output_urls ? `
                                <div class="grid grid-cols-2 gap-2">
                                    ${staging.output_urls.map(url => `
                                        <a href="${url}" target="_blank">
                                            <img src="${url}" class="w-full h-32 object-cover rounded hover:opacity-80">
                                        </a>
                                    `).join('')}
                                </div>
                            ` : '<p class="text-sm text-gray-600">Processing...</p>'}
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = '<p class="text-sm text-gray-500">No stagings yet. Upload a room photo to get started!</p>';
                }
            } catch (error) {
                console.error('Error loading recent stagings:', error);
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stage', methods=['POST'])
def stage():
    """Complete staging endpoint with all fixes"""
    data = request.json
    print(f"\n=== New staging request at {datetime.now().isoformat()} ===")
    
    image_data = data.get('image')
    space_type = data.get('space_type')
    design_theme = data.get('design_theme')
    
    if not image_data or not space_type:
        print("[ERROR] Missing required fields")
        return jsonify({'success': False, 'error': 'Missing required fields'})
    
    headers = {'api-key': REIMAGINEHOME_API_KEY}
    
    try:
        # Extract base64 data
        base64_data = image_data.split(',')[1] if ',' in image_data else image_data
        image_bytes = base64.b64decode(base64_data)
        
        # Try to upload to external service first
        image_url = None
        
        # Try ImgBB first (most reliable)
        if IMGBB_API_KEY:
            try:
                print("Uploading to ImgBB...")
                imgbb_response = requests.post(
                    'https://api.imgbb.com/1/upload',
                    data={
                        'key': IMGBB_API_KEY,
                        'image': base64_data,  # ImgBB accepts base64 directly
                        'name': f'room_{int(time.time())}'
                    },
                    timeout=30
                )
                
                if imgbb_response.status_code == 200:
                    imgbb_data = imgbb_response.json()
                    if imgbb_data.get('success'):
                        image_url = imgbb_data['data']['url']
                        print(f"Image uploaded to ImgBB: {image_url}")
                    else:
                        print(f"ImgBB error: {imgbb_data}")
                else:
                    print(f"ImgBB upload failed with status: {imgbb_response.status_code}")
            except Exception as e:
                print(f"ImgBB upload failed: {e}")
        
        # Try Cloudinary as backup
        if not image_url and CLOUDINARY_CONFIGURED:
            try:
                print("Trying Cloudinary as backup...")
                upload_result = cloudinary.uploader.upload(
                    image_bytes,
                    public_id=f"room_{int(time.time())}",
                    folder="aistager",
                    format="jpg"
                )
                image_url = upload_result.get('secure_url')
                print(f"Image uploaded to Cloudinary: {image_url}")
            except Exception as e:
                print(f"Cloudinary upload failed: {e}")
        
        # If external upload failed, use local serving
        if not image_url:
            # Generate unique ID for image
            image_id = hashlib.md5(f"{time.time()}{len(image_bytes)}".encode()).hexdigest()[:16]
            TEMP_IMAGES[image_id] = image_bytes
            
            # Create URL - this will be public when deployed on Render
            base_url = request.url_root.rstrip('/')
            image_url = f"{base_url}/temp-image/{image_id}.jpg"
            print(f"Image served locally at: {image_url}")
        
        # Create a unique job ID for this staging
        internal_job_id = str(uuid.uuid4())[:12]
        
        # Store job info
        STAGING_JOBS[internal_job_id] = {
            'status': 'processing',
            'created_at': datetime.now().isoformat(),
            'space_type': space_type,
            'design_theme': design_theme
        }
        
        # Get webhook URL
        webhook_url = f"{request.url_root.rstrip('/')}/webhook/reimaginehome/{internal_job_id}"
        
        # Step 1: Create masks
        print(f"Sending image to ReimagineHome API: {image_url}")
        mask_response = requests.post(
            'https://api.reimaginehome.ai/v1/create_mask',
            headers=headers,
            json={'image_url': image_url}
        )
        
        print(f"Mask API response status: {mask_response.status_code}")
        if mask_response.status_code == 200:
            mask_job_id = mask_response.json()['data']['job_id']
            
            # Step 2: Wait for masks
            masks = None
            for i in range(20):
                time.sleep(2)
                status_response = requests.get(
                    f'https://api.reimaginehome.ai/v1/create_mask/{mask_job_id}',
                    headers=headers
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data.get('data', {}).get('job_status') == 'done':
                        masks = status_data['data']['masks']
                        break
            
            if masks:
                # Step 3: Generate staged image
                furnishing_masks = [m['url'] for m in masks if 'furnishing' in m.get('category', '')]
                if not furnishing_masks:
                    masks_sorted = sorted(masks, key=lambda x: x.get('area_percent', 0), reverse=True)
                    mask_urls = [masks_sorted[0]['url']] if masks_sorted else []
                else:
                    mask_urls = furnishing_masks
                
                generation_payload = {
                    'image_url': image_url,
                    'mask_urls': mask_urls,
                    'mask_category': 'furnishing',
                    'space_type': space_type,
                    'generation_count': 1,
                    'webhook_url': webhook_url
                }
                
                if design_theme:
                    generation_payload['design_theme'] = design_theme
                    
                gen_response = requests.post(
                    'https://api.reimaginehome.ai/v1/generate_image',
                    headers=headers,
                    json=generation_payload
                )
                
                if gen_response.status_code == 200:
                    reimagine_job_id = gen_response.json().get('data', {}).get('job_id', 'unknown')
                    STAGING_JOBS[internal_job_id]['reimagine_job_id'] = reimagine_job_id
                    
                    return jsonify({
                        'success': True,
                        'job_id': internal_job_id,
                        'message': 'Staging job submitted successfully!'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to start staging process'
                    })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to process room layout'
                })
        else:
            error_data = mask_response.json()
            error_msg = error_data.get('error_message', 'Image processing failed')
            print(f"[ERROR] ReimagineHome API error: {error_msg}")
            print(f"Full error response: {error_data}")
            return jsonify({
                'success': False,
                'error': error_msg
            })
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/webhook/reimaginehome/<job_id>', methods=['POST'])
def webhook_receiver(job_id):
    """Receive staging results from ReimagineHome"""
    print(f"\\n🎉 Webhook received for job: {job_id}")
    
    try:
        data = request.json
        print(f"Webhook data: {json.dumps(data, indent=2)}")
        
        # Store the completed staging
        if job_id in STAGING_JOBS:
            STAGING_JOBS[job_id]['status'] = 'completed'
            STAGING_JOBS[job_id]['completed_at'] = datetime.now().isoformat()
            STAGING_JOBS[job_id]['result'] = data
            
            # Extract output URLs
            output_urls = []
            if data and 'output_urls' in data:
                output_urls = data['output_urls']
            elif data and 'data' in data and 'output_urls' in data['data']:
                output_urls = data['data']['output_urls']
            
            STAGING_JOBS[job_id]['output_urls'] = output_urls
            
            # Also store in completed stagings
            COMPLETED_STAGINGS[job_id] = {
                'job_id': job_id,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'output_urls': output_urls,
                'space_type': STAGING_JOBS[job_id].get('space_type'),
                'design_theme': STAGING_JOBS[job_id].get('design_theme')
            }
            
            print(f"✅ Staging completed! URLs: {output_urls}")
        
        return jsonify({'status': 'success', 'received': True})
        
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/check-job/<job_id>')
def check_job(job_id):
    """Check if a staging job is completed"""
    if job_id in STAGING_JOBS and STAGING_JOBS[job_id]['status'] == 'completed':
        return jsonify({
            'completed': True,
            'result': {
                'output_urls': STAGING_JOBS[job_id].get('output_urls', [])
            }
        })
    return jsonify({'completed': False})

@app.route('/api/recent-stagings')
def recent_stagings():
    """Get recent completed stagings"""
    # Get last 5 completed stagings
    recent = sorted(
        COMPLETED_STAGINGS.values(),
        key=lambda x: x['timestamp'],
        reverse=True
    )[:5]
    
    return jsonify({'stagings': recent})

@app.route('/api/debug-payload')
def debug_payload():
    try:
        with open('/tmp/stage_debug.json', 'r') as f:
            import json
            data = json.load(f)
        return jsonify({'success': True, 'payload': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-alive')
def test_alive():
    return jsonify({'success': True, 'message': 'Test endpoint is alive and serving latest code.'})

@app.route('/api/deploy-check')
def deploy_check():
    app.logger.error("[DEPLOYMENT CHECK] This is the unique deployment check message: 20240722-XYZ")
    return jsonify({'success': True, 'message': 'Deployment check endpoint hit. If you see the log message, this is the latest code.'})

@app.route('/api/unique-test-abc123')
def unique_test_abc123():
    return jsonify({'success': True, 'message': 'This is the unique test route abc123.'})

# Serve temporary images
@app.route('/temp-image/<image_id>')
def serve_temp_image(image_id):
    """Serve temporarily stored images"""
    # Remove .jpg extension if present
    image_id = image_id.replace('.jpg', '')
    
    if image_id in TEMP_IMAGES:
        return send_file(
            io.BytesIO(TEMP_IMAGES[image_id]),
            mimetype='image/jpeg',
            as_attachment=False,
            download_name=f'{image_id}.jpg'
        )
    else:
        return 'Image not found', 404

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'api_configured': bool(REIMAGINEHOME_API_KEY)})

# For local development
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)