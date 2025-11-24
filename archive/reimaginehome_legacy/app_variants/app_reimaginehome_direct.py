import os
import time
import requests
import base64
import json
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv('.env.local')

app = Flask(__name__)
CORS(app)

# ReimagineHome API key
REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')

print(f"ReimagineHome API configured: {'Yes' if REIMAGINEHOME_API_KEY else 'No'}")

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Room Stager - ReimagineHome</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Room Stager</h1>
        <p class="text-center text-gray-600 mb-8">Direct Upload Version</p>
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
                <p class="text-sm">
                    <strong>Important:</strong> This version uses publicly accessible test images.
                    For production, you'll need to implement proper image hosting.
                </p>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Select Test Room</label>
                <select id="testImage" class="w-full p-3 border rounded mb-4">
                    <option value="https://images.unsplash.com/photo-1586023492125-27b2c045efd7">Empty Living Room 1</option>
                    <option value="https://images.unsplash.com/photo-1565623006066-82f23c79210b">Empty Bedroom</option>
                    <option value="https://images.unsplash.com/photo-1556020685-ae41abfc9365">Empty Living Room 2</option>
                    <option value="https://images.unsplash.com/photo-1493809842364-78817add7ffb">Minimal Room</option>
                </select>
                <img id="preview" class="max-h-64 mx-auto rounded shadow">
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Room Type</label>
                <select id="spaceType" class="w-full p-3 border rounded">
                    <option value="ST-INT-011">Living Room</option>
                    <option value="ST-INT-003">Bedroom</option>
                    <option value="ST-INT-009">Kitchen</option>
                    <option value="ST-INT-002">Bathroom</option>
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
                Stage This Room
            </button>
            
            <div id="status" class="mt-4"></div>
            <div id="results" class="mt-6"></div>
            
            <div class="mt-8 p-4 bg-gray-50 rounded">
                <h3 class="font-semibold mb-2">How to use your own images:</h3>
                <ol class="list-decimal list-inside text-sm text-gray-600">
                    <li>Upload your image to a public hosting service</li>
                    <li>Or set up Cloudinary/AWS S3 for automatic uploads</li>
                    <li>Or use the development server with ngrok for testing</li>
                </ol>
            </div>
        </div>
    </div>
    
    <script>
        // Update preview when test image is selected
        document.getElementById('testImage').addEventListener('change', (e) => {
            const preview = document.getElementById('preview');
            preview.src = e.target.value + '?w=800&q=80';
        });
        
        // Set initial preview
        document.getElementById('preview').src = document.getElementById('testImage').value + '?w=800&q=80';
        
        document.getElementById('stageBtn').addEventListener('click', async () => {
            const btn = document.getElementById('stageBtn');
            const status = document.getElementById('status');
            const results = document.getElementById('results');
            
            const imageUrl = document.getElementById('testImage').value;
            const spaceType = document.getElementById('spaceType').value;
            const designTheme = document.getElementById('designTheme').value;
            
            btn.disabled = true;
            btn.textContent = 'Processing...';
            status.innerHTML = '<div class="text-blue-600">Starting staging process...</div>';
            results.innerHTML = '';
            
            try {
                const response = await fetch('/api/stage-direct', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image_url: imageUrl + '?w=1024&q=80',
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
                            <p class="font-semibold mb-2">Processing Status:</p>
                            <ul class="list-disc list-inside text-sm text-gray-700">
                                <li>Masks created: ${data.masks_found} found</li>
                                <li>Masks used: ${data.masks_used} for staging</li>
                                <li>Image submitted for staging</li>
                            </ul>
                            <p class="text-sm text-gray-600 mt-3">
                                Note: Results would be delivered via webhook in production (20-40 seconds)
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
                    
                    if (data.details) {
                        results.innerHTML = `
                            <pre class="mt-4 p-4 bg-gray-100 rounded text-xs overflow-x-auto">
${JSON.stringify(data.details, null, 2)}
                            </pre>
                        `;
                    }
                }
            } catch (error) {
                status.innerHTML = `
                    <div class="bg-red-50 p-4 rounded">
                        <p class="text-red-800">✗ Error: ${error.message}</p>
                    </div>
                `;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Stage This Room';
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stage-direct', methods=['POST'])
def stage_direct():
    data = request.json
    image_url = data.get('image_url')
    space_type = data.get('space_type')
    design_theme = data.get('design_theme')
    
    if not image_url or not space_type:
        return jsonify({
            'success': False,
            'error': 'Image URL and room type are required'
        })
    
    headers = {'api-key': REIMAGINEHOME_API_KEY}
    
    try:
        # Step 1: Create masks
        print(f"Creating masks for: {image_url}")
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
                'details': mask_error
            })
        
        mask_job_id = mask_response.json()['data']['job_id']
        print(f"Mask job created: {mask_job_id}")
        
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
            # Use largest mask
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
            print("Staging job created successfully!")
            
            return jsonify({
                'success': True,
                'message': 'Room staging initiated!',
                'job_id': result.get('job_id', 'Processing'),
                'masks_found': len(masks),
                'masks_used': len(mask_urls),
                'note': 'Results will be delivered via webhook in production'
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
    print("AI ROOM STAGER - DIRECT VERSION")
    print("="*60)
    print(f"API Key: {'[OK] Configured' if REIMAGINEHOME_API_KEY else '[X] Not configured'}")
    print("\nThis version uses publicly accessible test images")
    print("to demonstrate the staging process.")
    print("\nFor your own images, you need:")
    print("- Public image hosting (Cloudinary, S3, etc.)")
    print("- Or use ngrok to expose local server")
    print("\nOpen http://localhost:5000 in your browser")
    print("="*60 + "\n")
    app.run(port=5000, debug=True)