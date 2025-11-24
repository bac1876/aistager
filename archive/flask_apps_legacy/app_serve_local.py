import os
import time
import requests
import base64
from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from PIL import Image
import io
import hashlib

load_dotenv('.env.local')

app = Flask(__name__)
CORS(app)

# ReimagineHome API key
REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')

# Store uploaded images in memory
UPLOADED_IMAGES = {}

print(f"ReimagineHome API configured: {'Yes' if REIMAGINEHOME_API_KEY else 'No'}")

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Room Stager - Local Server</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Room Stager</h1>
        <p class="text-center text-gray-600 mb-8">Serve Your Local Images</p>
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="bg-amber-50 border-l-4 border-amber-400 p-4 mb-6">
                <p class="text-sm font-semibold mb-2">
                    ⚡ Quick Setup Instructions:
                </p>
                <ol class="list-decimal list-inside text-sm space-y-1">
                    <li>Upload your room photo below</li>
                    <li>Open a new terminal and run: <code class="bg-gray-200 px-1">ngrok http 5000</code></li>
                    <li>Copy the ngrok URL (e.g., https://abc123.ngrok.io)</li>
                    <li>Paste it in the field below and click "Stage My Room"</li>
                </ol>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Step 1: Upload Your Room Photo</label>
                <input type="file" id="fileInput" accept="image/*" class="w-full p-2 border rounded">
                <img id="preview" class="mt-4 max-h-64 mx-auto hidden rounded shadow">
                <div id="uploadStatus" class="mt-2"></div>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Step 2: Enter Your ngrok URL</label>
                <input type="text" id="ngrokUrl" placeholder="https://your-id.ngrok.io" 
                       class="w-full p-3 border rounded" value="">
                <p class="text-xs text-gray-500 mt-1">Don't have ngrok? Download from ngrok.com</p>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Room Type</label>
                <select id="spaceType" class="w-full p-3 border rounded">
                    <option value="ST-INT-011">Living Room</option>
                    <option value="ST-INT-003">Bedroom</option>
                    <option value="ST-INT-009">Kitchen</option>
                    <option value="ST-INT-002">Bathroom</option>
                    <option value="ST-INT-004">Dining Room</option>
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
                </select>
            </div>
            
            <button id="stageBtn" class="w-full bg-blue-500 text-white py-3 rounded hover:bg-blue-600 font-semibold">
                Stage My Room
            </button>
            
            <div id="status" class="mt-4"></div>
            <div id="results" class="mt-6"></div>
        </div>
    </div>
    
    <script>
        let imageId = null;
        
        document.getElementById('fileInput').addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = async (event) => {
                    // Show preview
                    document.getElementById('preview').src = event.target.result;
                    document.getElementById('preview').classList.remove('hidden');
                    
                    // Upload to server
                    const uploadStatus = document.getElementById('uploadStatus');
                    uploadStatus.innerHTML = '<p class="text-sm text-blue-600">Uploading image...</p>';
                    
                    try {
                        const response = await fetch('/upload-image', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ image: event.target.result })
                        });
                        
                        const data = await response.json();
                        if (data.success) {
                            imageId = data.image_id;
                            uploadStatus.innerHTML = `
                                <p class="text-sm text-green-600">✓ Image uploaded!</p>
                                <p class="text-xs text-gray-500 mt-1">Image ID: ${imageId}</p>
                                <p class="text-xs text-gray-500">Your image URL will be: [ngrok-url]/image/${imageId}</p>
                            `;
                        } else {
                            uploadStatus.innerHTML = '<p class="text-sm text-red-600">Upload failed</p>';
                        }
                    } catch (error) {
                        uploadStatus.innerHTML = '<p class="text-sm text-red-600">Upload error</p>';
                    }
                };
                reader.readAsDataURL(file);
            }
        });
        
        document.getElementById('stageBtn').addEventListener('click', async () => {
            const btn = document.getElementById('stageBtn');
            const status = document.getElementById('status');
            const results = document.getElementById('results');
            
            if (!imageId) {
                alert('Please upload a room photo first');
                return;
            }
            
            const ngrokUrl = document.getElementById('ngrokUrl').value.trim();
            if (!ngrokUrl) {
                alert('Please enter your ngrok URL');
                return;
            }
            
            const spaceType = document.getElementById('spaceType').value;
            const designTheme = document.getElementById('designTheme').value;
            
            btn.disabled = true;
            btn.textContent = 'Processing...';
            status.innerHTML = '<div class="text-blue-600">Submitting to ReimagineHome...</div>';
            results.innerHTML = '';
            
            try {
                const response = await fetch('/api/stage-with-url', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image_id: imageId,
                        ngrok_url: ngrokUrl,
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
                            <p class="font-semibold mb-2">Success! Your room is being staged.</p>
                            <ul class="list-disc list-inside text-sm text-gray-700">
                                <li>Image URL used: ${data.image_url}</li>
                                <li>Masks found: ${data.masks_found}</li>
                                <li>Processing time: 20-40 seconds</li>
                            </ul>
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

@app.route('/upload-image', methods=['POST'])
def upload_image():
    """Store image and return an ID"""
    data = request.json
    image_data = data.get('image')
    
    if not image_data:
        return jsonify({'success': False, 'error': 'No image provided'})
    
    # Generate unique ID for this image
    image_id = hashlib.md5(image_data.encode()).hexdigest()[:12]
    
    # Store in memory
    UPLOADED_IMAGES[image_id] = image_data
    
    return jsonify({
        'success': True,
        'image_id': image_id
    })

@app.route('/image/<image_id>')
def serve_image(image_id):
    """Serve uploaded image by ID"""
    if image_id not in UPLOADED_IMAGES:
        return 'Image not found', 404
    
    image_data = UPLOADED_IMAGES[image_id]
    
    # Convert base64 to bytes
    base64_data = image_data.split(',')[1] if ',' in image_data else image_data
    image_bytes = base64.b64decode(base64_data)
    
    # Return as image
    return send_file(
        io.BytesIO(image_bytes),
        mimetype='image/jpeg',
        as_attachment=False,
        download_name=f'{image_id}.jpg'
    )

@app.route('/api/stage-with-url', methods=['POST'])
def stage_with_url():
    data = request.json
    image_id = data.get('image_id')
    ngrok_url = data.get('ngrok_url')
    space_type = data.get('space_type')
    design_theme = data.get('design_theme')
    
    if not all([image_id, ngrok_url, space_type]):
        return jsonify({
            'success': False,
            'error': 'Missing required fields'
        })
    
    # Construct the public URL for the image
    image_url = f"{ngrok_url.rstrip('/')}/image/{image_id}"
    
    headers = {'api-key': REIMAGINEHOME_API_KEY}
    
    try:
        print(f"Using image URL: {image_url}")
        
        # Step 1: Create masks
        mask_response = requests.post(
            'https://api.reimaginehome.ai/v1/create_mask',
            headers=headers,
            json={'image_url': image_url}
        )
        
        if mask_response.status_code != 200:
            mask_error = mask_response.json()
            return jsonify({
                'success': False,
                'error': f'Mask creation failed: {mask_error.get("error_message", "Unknown error")}',
                'image_url': image_url
            })
        
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
                job_status = status_data.get('data', {}).get('job_status')
                
                if job_status == 'done':
                    masks = status_data['data']['masks']
                    break
                elif job_status == 'error':
                    return jsonify({
                        'success': False,
                        'error': 'Mask creation failed'
                    })
        
        if not masks:
            return jsonify({
                'success': False,
                'error': 'Mask creation timed out'
            })
        
        # Step 3: Generate staged image
        furnishing_masks = [m['url'] for m in masks if 'furnishing' in m['category']]
        if not furnishing_masks:
            masks_sorted = sorted(masks, key=lambda x: x['area_percent'], reverse=True)
            mask_urls = [masks_sorted[0]['url']]
        else:
            mask_urls = furnishing_masks
        
        generation_payload = {
            'image_url': image_url,
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
            
            return jsonify({
                'success': True,
                'message': 'Room staging initiated!',
                'job_id': result.get('job_id', 'Processing'),
                'masks_found': len(masks),
                'image_url': image_url
            })
        else:
            gen_error = gen_response.json()
            return jsonify({
                'success': False,
                'error': f'Generation failed: {gen_error.get("error_message", "Unknown error")}'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI ROOM STAGER - LOCAL SERVER WITH NGROK")
    print("="*60)
    print(f"API Key: {'[OK] Configured' if REIMAGINEHOME_API_KEY else '[X] Not configured'}")
    print("\nInstructions:")
    print("1. This app is running at: http://localhost:5000")
    print("2. Install ngrok: https://ngrok.com/download")
    print("3. In a NEW terminal, run: ngrok http 5000")
    print("4. Copy the HTTPS URL from ngrok (e.g., https://abc123.ngrok.io)")
    print("5. Use that URL in the app to stage your images")
    print("\nThis allows ReimagineHome to access your local images!")
    print("="*60 + "\n")
    app.run(port=5000, debug=True)