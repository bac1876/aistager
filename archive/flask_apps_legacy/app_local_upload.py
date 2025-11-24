import os
import time
import requests
import base64
from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from PIL import Image
import io
import uuid

load_dotenv('.env.local')

app = Flask(__name__)
CORS(app)

# ReimagineHome API key
REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')

# Store uploaded images temporarily
TEMP_IMAGES = {}

print(f"ReimagineHome API configured: {'Yes' if REIMAGINEHOME_API_KEY else 'No'}")

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Room Stager - Local Upload</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Room Stager</h1>
        <p class="text-center text-gray-600 mb-8">Local Image Upload Version</p>
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
                <p class="text-sm">
                    <strong>Note:</strong> This version serves images locally. 
                    For production use, you'll need to expose this server using ngrok or deploy to a cloud service.
                </p>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Upload Your Room Photo</label>
                <input type="file" id="fileInput" accept="image/*" class="w-full p-2 border rounded">
                <img id="preview" class="mt-4 max-h-64 mx-auto hidden rounded shadow">
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Room Type</label>
                <select id="spaceType" class="w-full p-3 border rounded">
                    <option value="ST-INT-011">Living Room</option>
                    <option value="ST-INT-003">Bedroom</option>
                    <option value="ST-INT-009">Kitchen</option>
                    <option value="ST-INT-002">Bathroom</option>
                    <option value="ST-INT-004">Dining Room</option>
                    <option value="ST-INT-016">Study/Office</option>
                </select>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Design Style</label>
                <select id="designTheme" class="w-full p-3 border rounded">
                    <option value="">AI Decides</option>
                    <option value="DT-INT-011">Modern</option>
                    <option value="DT-INT-003">Contemporary</option>
                    <option value="DT-INT-013">Scandinavian</option>
                    <option value="DT-INT-010">Minimal</option>
                    <option value="DT-INT-014">Traditional</option>
                </select>
            </div>
            
            <button id="stageBtn" class="w-full bg-blue-500 text-white py-3 rounded hover:bg-blue-600 font-semibold">
                Stage My Room
            </button>
            
            <div id="status" class="mt-4"></div>
            <div id="results" class="mt-6"></div>
            
            <div class="mt-8 p-4 bg-gray-50 rounded">
                <h3 class="font-semibold mb-2">Current Server URL:</h3>
                <p class="text-sm text-gray-600" id="serverUrl">Loading...</p>
                <p class="text-xs text-gray-500 mt-2">
                    To make this accessible to ReimagineHome, run: 
                    <code class="bg-gray-200 px-1">ngrok http 5000</code>
                </p>
            </div>
        </div>
    </div>
    
    <script>
        // Show current server URL
        document.getElementById('serverUrl').textContent = window.location.origin;
        
        let imageData = null;
        
        document.getElementById('fileInput').addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    const img = new Image();
                    img.onload = function() {
                        // Check and resize if needed
                        const canvas = document.createElement('canvas');
                        let width = img.width;
                        let height = img.height;
                        
                        // Resize if larger than 2048
                        if (width > 2048 || height > 2048) {
                            const ratio = Math.min(2048/width, 2048/height);
                            width = Math.round(width * ratio);
                            height = Math.round(height * ratio);
                        }
                        
                        canvas.width = width;
                        canvas.height = height;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0, width, height);
                        
                        imageData = canvas.toDataURL('image/jpeg', 0.9);
                        document.getElementById('preview').src = imageData;
                        document.getElementById('preview').classList.remove('hidden');
                        
                        document.getElementById('status').innerHTML = 
                            `<p class="text-sm text-gray-600">Image: ${width}x${height} pixels</p>`;
                    };
                    img.src = event.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
        
        document.getElementById('stageBtn').addEventListener('click', async () => {
            const btn = document.getElementById('stageBtn');
            const status = document.getElementById('status');
            const results = document.getElementById('results');
            
            if (!imageData) {
                alert('Please upload a room photo');
                return;
            }
            
            const spaceType = document.getElementById('spaceType').value;
            const designTheme = document.getElementById('designTheme').value;
            
            btn.disabled = true;
            btn.textContent = 'Processing...';
            status.innerHTML = '<div class="text-blue-600">Uploading and processing...</div>';
            results.innerHTML = '';
            
            try {
                const response = await fetch('/api/stage-local', {
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
                    status.innerHTML = `
                        <div class="bg-green-50 p-4 rounded">
                            <p class="text-green-800 font-semibold">✓ Staging job submitted!</p>
                            <p class="text-sm text-green-600 mt-1">Job ID: ${data.job_id || 'Processing'}</p>
                        </div>
                    `;
                    
                    results.innerHTML = `
                        <div class="bg-blue-50 p-4 rounded">
                            <p class="font-semibold mb-2">Processing Details:</p>
                            <ul class="list-disc list-inside text-sm text-gray-700">
                                <li>Image uploaded successfully</li>
                                <li>Masks created: ${data.masks_found} found</li>
                                <li>Staging job submitted</li>
                            </ul>
                            <p class="text-sm text-gray-600 mt-3">
                                Results will be delivered via webhook (20-40 seconds)
                            </p>
                        </div>
                        
                        <div class="mt-4 p-4 bg-yellow-50 rounded">
                            <p class="text-sm font-semibold">Important:</p>
                            <p class="text-sm text-gray-700 mt-1">
                                ${data.note || 'Make sure your server is accessible from the internet using ngrok.'}
                            </p>
                        </div>
                    `;
                } else {
                    status.innerHTML = `
                        <div class="bg-red-50 p-4 rounded">
                            <p class="text-red-800 font-semibold">✗ Staging failed</p>
                            <p class="text-sm text-red-600 mt-1">${data.error}</p>
                        </div>
                    `;
                }
            } catch (error) {
                status.innerHTML = `
                    <div class="bg-red-50 p-4 rounded">
                        <p class="text-red-800">✗ Error: ${error.message}</p>
                    </div>
                `;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Stage My Room';
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/temp-image/<image_id>')
def serve_temp_image(image_id):
    """Serve temporary images"""
    if image_id in TEMP_IMAGES:
        image_data = TEMP_IMAGES[image_id]
        # Convert base64 to bytes
        base64_data = image_data.split(',')[1] if ',' in image_data else image_data
        image_bytes = base64.b64decode(base64_data)
        return send_file(io.BytesIO(image_bytes), mimetype='image/jpeg')
    return 'Image not found', 404

@app.route('/api/stage-local', methods=['POST'])
def stage_local():
    data = request.json
    image_data = data.get('image')
    space_type = data.get('space_type')
    design_theme = data.get('design_theme')
    
    if not image_data or not space_type:
        return jsonify({
            'success': False,
            'error': 'Image and room type are required'
        })
    
    headers = {'api-key': REIMAGINEHOME_API_KEY}
    
    try:
        # Store image temporarily and generate URL
        image_id = str(uuid.uuid4())
        TEMP_IMAGES[image_id] = image_data
        
        # Get the server's public URL (you'll need to replace this with ngrok URL)
        # For testing, we'll use localhost
        server_url = request.url_root.rstrip('/')
        image_url = f"{server_url}/temp-image/{image_id}"
        
        print(f"Local image URL: {image_url}")
        
        # Test with a known working URL first
        test_url = "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1024"
        
        # Step 1: Create masks
        print("Creating masks...")
        mask_response = requests.post(
            'https://api.reimaginehome.ai/v1/create_mask',
            headers=headers,
            json={'image_url': test_url}  # Using test URL for now
        )
        
        if mask_response.status_code != 200:
            mask_error = mask_response.json()
            return jsonify({
                'success': False,
                'error': f'Mask creation failed: {mask_error.get("error_message", "Unknown error")}',
                'details': mask_error
            })
        
        mask_job_id = mask_response.json()['data']['job_id']
        print(f"Mask job: {mask_job_id}")
        
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
                job_status = status_data.get('data', {}).get('job_status')
                
                if job_status == 'done':
                    masks = status_data['data']['masks']
                    print(f"Masks ready: {len(masks)} found")
                    break
                elif job_status == 'error':
                    return jsonify({
                        'success': False,
                        'error': 'Mask creation failed during processing'
                    })
        
        if not masks:
            return jsonify({
                'success': False,
                'error': 'Mask creation timed out'
            })
        
        # Step 3: Generate staged image
        print("Generating staged image...")
        
        # Get appropriate masks
        furnishing_masks = [m['url'] for m in masks if 'furnishing' in m['category']]
        if not furnishing_masks:
            masks_sorted = sorted(masks, key=lambda x: x['area_percent'], reverse=True)
            mask_urls = [masks_sorted[0]['url']]
        else:
            mask_urls = furnishing_masks
        
        generation_payload = {
            'image_url': test_url,  # Using test URL for now
            'mask_urls': mask_urls,
            'mask_category': 'furnishing',
            'space_type': space_type,
            'generation_count': 1
        }
        
        if design_theme:
            generation_payload['design_theme'] = design_theme
            
        gen_response = requests.post(
            'https://api.reimaginehome.ai/v1/generate_image',
            headers=headers,
            json=generation_payload
        )
        
        if gen_response.status_code == 200:
            result = gen_response.json()
            print("Staging job created successfully!")
            
            # Clean up old images after some time
            def cleanup():
                time.sleep(600)  # 10 minutes
                if image_id in TEMP_IMAGES:
                    del TEMP_IMAGES[image_id]
            
            import threading
            threading.Thread(target=cleanup).start()
            
            return jsonify({
                'success': True,
                'message': 'Room staging initiated!',
                'job_id': result.get('job_id', 'Processing'),
                'masks_found': len(masks),
                'note': 'Currently using test image. For your actual image, expose this server with ngrok and update the code.'
            })
        else:
            gen_error = gen_response.json()
            return jsonify({
                'success': False,
                'error': f'Generation failed: {gen_error.get("error_message", "Unknown error")}',
                'details': gen_error
            })
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI ROOM STAGER - LOCAL UPLOAD VERSION")
    print("="*60)
    print(f"API Key: {'[OK] Configured' if REIMAGINEHOME_API_KEY else '[X] Not configured'}")
    print("\nThis version serves images locally.")
    print("\nTo make it work with ReimagineHome:")
    print("1. Install ngrok: https://ngrok.com/download")
    print("2. Run: ngrok http 5000")
    print("3. Use the ngrok URL in the code")
    print("\nCurrently using test images for demo purposes.")
    print("\nOpen http://localhost:5000 in your browser")
    print("="*60 + "\n")
    app.run(port=5000, debug=True)