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
import json
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

# Get API key from environment
REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')

# Store uploaded images and results in memory
UPLOADED_IMAGES = {}
STAGING_RESULTS = {}

print(f"ReimagineHome API configured: {'Yes' if REIMAGINEHOME_API_KEY else 'No'}")

# HTML template with debugging
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Room Stager - Debug Version</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Room Stager - Debug</h1>
        <p class="text-center text-gray-600 mb-8">Testing Image Accessibility</p>
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
                <p class="text-sm font-semibold mb-2">Debug Mode Active</p>
                <p class="text-sm">This version will show detailed error information.</p>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Upload Your Room Photo</label>
                <input type="file" id="fileInput" accept="image/*" class="w-full p-2 border rounded">
                <img id="preview" class="mt-4 max-h-64 mx-auto hidden rounded shadow">
                <div id="uploadStatus" class="mt-2"></div>
            </div>
            
            <div class="mb-6">
                <button id="testBtn" class="w-full bg-green-500 text-white py-2 rounded hover:bg-green-600 font-semibold mb-2">
                    Test Image Accessibility
                </button>
                <button id="stageBtn" class="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600 font-semibold">
                    Stage My Room
                </button>
            </div>
            
            <div id="debugInfo" class="mt-4 p-4 bg-gray-100 rounded text-xs font-mono hidden"></div>
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
                    document.getElementById('preview').src = event.target.result;
                    document.getElementById('preview').classList.remove('hidden');
                    
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
                                <p class="text-xs text-gray-500">Image ID: ${imageId}</p>
                                <p class="text-xs text-gray-500">URL: ${window.location.origin}/image/${imageId}</p>
                            `;
                        }
                    } catch (error) {
                        uploadStatus.innerHTML = '<p class="text-sm text-red-600">Upload error</p>';
                    }
                };
                reader.readAsDataURL(file);
            }
        });
        
        document.getElementById('testBtn').addEventListener('click', async () => {
            if (!imageId) {
                alert('Please upload an image first');
                return;
            }
            
            const debugDiv = document.getElementById('debugInfo');
            debugDiv.classList.remove('hidden');
            debugDiv.innerHTML = 'Testing image accessibility...';
            
            try {
                const response = await fetch('/test-image-access', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image_id: imageId })
                });
                
                const data = await response.json();
                debugDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
            } catch (error) {
                debugDiv.innerHTML = `Error: ${error.message}`;
            }
        });
        
        document.getElementById('stageBtn').addEventListener('click', async () => {
            if (!imageId) {
                alert('Please upload an image first');
                return;
            }
            
            const btn = document.getElementById('stageBtn');
            const status = document.getElementById('status');
            
            btn.disabled = true;
            btn.textContent = 'Processing...';
            
            try {
                const response = await fetch('/api/stage-debug', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image_id: imageId })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    status.innerHTML = `
                        <div class="bg-green-50 p-4 rounded">
                            <p class="text-green-800 font-semibold">✓ Success!</p>
                            <p class="text-sm text-green-600 mt-1">${data.message}</p>
                        </div>
                    `;
                } else {
                    status.innerHTML = `
                        <div class="bg-red-50 p-4 rounded">
                            <p class="text-red-800 font-semibold">✗ Error</p>
                            <p class="text-sm text-red-600 mt-1">${data.error}</p>
                            ${data.debug ? `<pre class="mt-2 text-xs overflow-x-auto">${JSON.stringify(data.debug, null, 2)}</pre>` : ''}
                        </div>
                    `;
                }
            } catch (error) {
                status.innerHTML = `<div class="bg-red-50 p-4 rounded"><p class="text-red-800">Error: ${error.message}</p></div>`;
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
    data = request.json
    image_data = data.get('image')
    
    if not image_data:
        return jsonify({'success': False, 'error': 'No image provided'})
    
    image_id = hashlib.md5(image_data.encode()).hexdigest()[:12]
    UPLOADED_IMAGES[image_id] = image_data
    
    return jsonify({'success': True, 'image_id': image_id})

@app.route('/image/<image_id>')
def serve_image(image_id):
    if image_id not in UPLOADED_IMAGES:
        return 'Image not found', 404
    
    image_data = UPLOADED_IMAGES[image_id]
    base64_data = image_data.split(',')[1] if ',' in image_data else image_data
    image_bytes = base64.b64decode(base64_data)
    
    return send_file(
        io.BytesIO(image_bytes),
        mimetype='image/jpeg',
        as_attachment=False,
        download_name=f'{image_id}.jpg'
    )

@app.route('/test-image-access', methods=['POST'])
def test_image_access():
    """Test if image is accessible"""
    data = request.json
    image_id = data.get('image_id')
    
    base_url = request.url_root.rstrip('/')
    image_url = f"{base_url}/image/{image_id}"
    
    result = {
        'image_url': image_url,
        'tests': {}
    }
    
    # Test 1: Local access
    try:
        response = requests.get(image_url, timeout=5)
        result['tests']['local_access'] = {
            'status': response.status_code,
            'success': response.status_code == 200
        }
    except Exception as e:
        result['tests']['local_access'] = {
            'error': str(e),
            'success': False
        }
    
    # Test 2: Check headers
    try:
        response = requests.head(image_url, timeout=5)
        result['tests']['headers'] = {
            'status': response.status_code,
            'content_type': response.headers.get('content-type'),
            'content_length': response.headers.get('content-length')
        }
    except Exception as e:
        result['tests']['headers'] = {'error': str(e)}
    
    # Test 3: Try with ReimagineHome API
    if REIMAGINEHOME_API_KEY:
        headers = {'api-key': REIMAGINEHOME_API_KEY}
        try:
            # Use a test image first
            test_url = "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800"
            response = requests.post(
                'https://api.reimaginehome.ai/v1/create_mask',
                headers=headers,
                json={'image_url': test_url}
            )
            result['tests']['api_with_test_image'] = {
                'status': response.status_code,
                'success': response.status_code == 200
            }
            
            # Now try with our image
            response = requests.post(
                'https://api.reimaginehome.ai/v1/create_mask',
                headers=headers,
                json={'image_url': image_url}
            )
            result['tests']['api_with_our_image'] = {
                'status': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code != 200 else 'Success'
            }
        except Exception as e:
            result['tests']['api_error'] = str(e)
    
    return jsonify(result)

@app.route('/api/stage-debug', methods=['POST'])
def stage_debug():
    """Debug version of staging endpoint"""
    data = request.json
    image_id = data.get('image_id')
    
    if not image_id:
        return jsonify({'success': False, 'error': 'No image ID provided'})
    
    base_url = request.url_root.rstrip('/')
    image_url = f"{base_url}/image/{image_id}"
    
    # Test with a known working image first
    test_url = "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1024"
    
    headers = {'api-key': REIMAGINEHOME_API_KEY}
    
    debug_info = {
        'image_url': image_url,
        'base_url': base_url,
        'render_detected': 'onrender.com' in base_url
    }
    
    try:
        # Test 1: Try with test image
        response = requests.post(
            'https://api.reimaginehome.ai/v1/create_mask',
            headers=headers,
            json={'image_url': test_url}
        )
        
        if response.status_code == 200:
            debug_info['test_image_works'] = True
            
            # Test 2: Try with our image
            response = requests.post(
                'https://api.reimaginehome.ai/v1/create_mask',
                headers=headers,
                json={'image_url': image_url}
            )
            
            if response.status_code == 200:
                return jsonify({
                    'success': True,
                    'message': 'Image is accessible! Mask creation started.',
                    'debug': debug_info
                })
            else:
                error_data = response.json()
                return jsonify({
                    'success': False,
                    'error': error_data.get('error_message', 'Unknown error'),
                    'debug': {
                        **debug_info,
                        'api_response': error_data,
                        'status_code': response.status_code
                    }
                })
        else:
            return jsonify({
                'success': False,
                'error': 'API test failed with known good image',
                'debug': debug_info
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'debug': debug_info
        })

# For local development
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)