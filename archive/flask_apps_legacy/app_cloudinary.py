import os
import time
import requests
import base64
import cloudinary
import cloudinary.uploader
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

# Cloudinary configuration (free tier available)
# Sign up at https://cloudinary.com and get your credentials
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', 'YOUR_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', 'YOUR_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', 'YOUR_API_SECRET')

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

print(f"ReimagineHome API configured: {'Yes' if REIMAGINEHOME_API_KEY else 'No'}")
print(f"Cloudinary configured: {'Yes' if CLOUDINARY_API_KEY != 'YOUR_API_KEY' else 'No'}")

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Room Stager - Cloudinary Version</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Room Stager</h1>
        <p class="text-center text-gray-600 mb-8">Professional Virtual Staging</p>
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="bg-green-50 border-l-4 border-green-400 p-4 mb-6">
                <p class="text-sm">
                    <strong>Production Ready!</strong> This version uses Cloudinary for reliable image hosting.
                    Your room photos will be professionally staged by AI.
                </p>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Upload Your Room Photo</label>
                <input type="file" id="fileInput" accept="image/*" class="w-full p-2 border rounded">
                <p class="text-xs text-gray-500 mt-1">Supports JPG, PNG. Max 10MB. Will be resized if needed.</p>
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
                    <option value="">AI Decides (Recommended)</option>
                    <option value="DT-INT-011">Modern</option>
                    <option value="DT-INT-003">Contemporary</option>
                    <option value="DT-INT-013">Scandinavian</option>
                    <option value="DT-INT-010">Minimal</option>
                    <option value="DT-INT-014">Traditional</option>
                    <option value="DT-INT-006">Industrial</option>
                    <option value="DT-INT-001">Bohemian</option>
                </select>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Special Requests (Optional)</label>
                <textarea id="additionalPrompt" rows="2" class="w-full p-3 border rounded" 
                    placeholder="e.g., warm lighting, blue accents, wooden furniture"></textarea>
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
            <div id="results" class="mt-6"></div>
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
                    const img = new Image();
                    img.onload = function() {
                        // Auto-resize large images
                        const canvas = document.createElement('canvas');
                        let width = img.width;
                        let height = img.height;
                        
                        // Resize if larger than 2048
                        if (width > 2048 || height > 2048) {
                            const ratio = Math.min(2048/width, 2048/height);
                            width = Math.round(width * ratio);
                            height = Math.round(height * ratio);
                        }
                        
                        // Ensure minimum size
                        if (width < 512 || height < 512) {
                            alert('Image must be at least 512x512 pixels');
                            return;
                        }
                        
                        canvas.width = width;
                        canvas.height = height;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0, width, height);
                        
                        imageData = canvas.toDataURL('image/jpeg', 0.95);
                        document.getElementById('preview').src = imageData;
                        document.getElementById('preview').classList.remove('hidden');
                        
                        document.getElementById('status').innerHTML = 
                            `<p class="text-sm text-gray-600">Image ready: ${width}x${height} pixels</p>`;
                    };
                    img.src = event.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
        
        function updateProgress(percent, text) {
            document.getElementById('progress').classList.remove('hidden');
            document.getElementById('progressBar').style.width = percent + '%';
            document.getElementById('progressText').textContent = text;
        }
        
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
            const additionalPrompt = document.getElementById('additionalPrompt').value;
            
            btn.disabled = true;
            btn.textContent = 'Processing...';
            status.innerHTML = '';
            results.innerHTML = '';
            updateProgress(10, 'Uploading image...');
            
            try {
                const response = await fetch('/api/stage-cloudinary', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: imageData,
                        space_type: spaceType,
                        design_theme: designTheme,
                        additional_prompt: additionalPrompt
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    updateProgress(100, 'Complete!');
                    
                    status.innerHTML = `
                        <div class="bg-green-50 p-4 rounded">
                            <p class="text-green-800 font-semibold">✅ Room staging submitted!</p>
                            <p class="text-sm text-green-600 mt-1">Job ID: ${data.job_id || 'Processing'}</p>
                        </div>
                    `;
                    
                    results.innerHTML = `
                        <div class="bg-blue-50 p-4 rounded">
                            <h3 class="font-semibold mb-2">Processing Status:</h3>
                            <ul class="list-disc list-inside text-sm text-gray-700">
                                <li>Image uploaded to cloud ✓</li>
                                <li>Room analysis complete (${data.masks_found} areas found) ✓</li>
                                <li>AI staging in progress...</li>
                            </ul>
                            <p class="text-sm text-gray-600 mt-3">
                                The staged room will be ready in 20-40 seconds.
                                In production, results would be sent to your webhook.
                            </p>
                        </div>
                        
                        <div class="mt-4">
                            <p class="text-sm text-gray-600">Your original image (uploaded):</p>
                            <img src="${data.uploaded_url}" class="mt-2 max-w-full rounded shadow" 
                                 style="max-height: 300px">
                        </div>
                    `;
                } else {
                    updateProgress(0, 'Failed');
                    status.innerHTML = `
                        <div class="bg-red-50 p-4 rounded">
                            <p class="text-red-800 font-semibold">❌ Staging failed</p>
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
                updateProgress(0, 'Error');
                status.innerHTML = `
                    <div class="bg-red-50 p-4 rounded">
                        <p class="text-red-800">❌ Error: ${error.message}</p>
                    </div>
                `;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Stage My Room';
                setTimeout(() => {
                    document.getElementById('progress').classList.add('hidden');
                }, 3000);
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stage-cloudinary', methods=['POST'])
def stage_cloudinary():
    data = request.json
    image_data = data.get('image')
    space_type = data.get('space_type')
    design_theme = data.get('design_theme')
    additional_prompt = data.get('additional_prompt')
    
    if not image_data or not space_type:
        return jsonify({
            'success': False,
            'error': 'Image and room type are required'
        })
    
    headers = {'api-key': REIMAGINEHOME_API_KEY}
    
    try:
        # Step 1: Upload to Cloudinary
        print("Uploading to Cloudinary...")
        
        # Upload image to Cloudinary
        upload_result = cloudinary.uploader.upload(
            image_data,
            folder="aistager",
            resource_type="image",
            format="jpg",
            transformation=[
                {'width': 2048, 'height': 2048, 'crop': 'limit'},
                {'quality': 'auto:best'}
            ]
        )
        
        image_url = upload_result['secure_url']
        print(f"Image uploaded: {image_url}")
        
        # Step 2: Create masks
        print("Creating masks...")
        mask_response = requests.post(
            'https://api.reimaginehome.ai/v1/create_mask',
            headers=headers,
            json={'image_url': image_url}
        )
        
        if mask_response.status_code != 200:
            mask_error = mask_response.json()
            
            # Clean up Cloudinary image on error
            cloudinary.uploader.destroy(upload_result['public_id'])
            
            return jsonify({
                'success': False,
                'error': f'Mask creation failed: {mask_error.get("error_message", "Unknown error")}',
                'details': mask_error
            })
        
        mask_job_id = mask_response.json()['data']['job_id']
        print(f"Mask job: {mask_job_id}")
        
        # Step 3: Wait for masks
        masks = None
        for i in range(20):  # 40 seconds max
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
                    # Clean up Cloudinary image on error
                    cloudinary.uploader.destroy(upload_result['public_id'])
                    return jsonify({
                        'success': False,
                        'error': 'Mask creation failed during processing'
                    })
        
        if not masks:
            # Clean up Cloudinary image on timeout
            cloudinary.uploader.destroy(upload_result['public_id'])
            return jsonify({
                'success': False,
                'error': 'Mask creation timed out'
            })
        
        # Step 4: Generate staged image
        print("Generating staged image...")
        
        # For staging, prioritize furnishing masks
        furnishing_masks = [m['url'] for m in masks if 'furnishing' in m['category']]
        
        # If no furnishing masks, use largest mask
        if not furnishing_masks:
            masks_sorted = sorted(masks, key=lambda x: x['area_percent'], reverse=True)
            mask_urls = [masks_sorted[0]['url']]
        else:
            mask_urls = furnishing_masks
        
        print(f"Using {len(mask_urls)} masks for staging")
        
        # Build generation payload
        generation_payload = {
            'image_url': image_url,
            'mask_urls': mask_urls,
            'mask_category': 'furnishing',
            'space_type': space_type,
            'generation_count': 1
        }
        
        # Add optional parameters
        if design_theme:
            generation_payload['design_theme'] = design_theme
        if additional_prompt:
            generation_payload['additional_prompt'] = additional_prompt
            
        gen_response = requests.post(
            'https://api.reimaginehome.ai/v1/generate_image',
            headers=headers,
            json=generation_payload
        )
        
        if gen_response.status_code == 200:
            result = gen_response.json()
            print("Staging job created successfully!")
            
            # Schedule cleanup after 1 hour
            def cleanup():
                time.sleep(3600)  # 1 hour
                try:
                    cloudinary.uploader.destroy(upload_result['public_id'])
                    print(f"Cleaned up image: {upload_result['public_id']}")
                except:
                    pass
            
            import threading
            threading.Thread(target=cleanup).start()
            
            return jsonify({
                'success': True,
                'message': 'Your room is being staged!',
                'job_id': result.get('job_id', 'Processing'),
                'uploaded_url': image_url,
                'masks_found': len(masks),
                'note': 'Staged image will be delivered via webhook'
            })
        else:
            gen_error = gen_response.json()
            # Clean up Cloudinary image on error
            cloudinary.uploader.destroy(upload_result['public_id'])
            return jsonify({
                'success': False,
                'error': gen_error.get('error_message', 'Generation failed'),
                'details': gen_error
            })
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI ROOM STAGER - CLOUDINARY VERSION")
    print("="*60)
    print(f"ReimagineHome API: {'[OK]' if REIMAGINEHOME_API_KEY else '[X] Missing'}")
    print(f"Cloudinary: {'[OK]' if CLOUDINARY_API_KEY != 'YOUR_API_KEY' else '[X] Not configured'}")
    
    if CLOUDINARY_API_KEY == 'YOUR_API_KEY':
        print("\nTo configure Cloudinary:")
        print("1. Sign up at https://cloudinary.com (free tier available)")
        print("2. Get your credentials from the dashboard")
        print("3. Add to .env.local:")
        print("   CLOUDINARY_CLOUD_NAME=your_cloud_name")
        print("   CLOUDINARY_API_KEY=your_api_key")
        print("   CLOUDINARY_API_SECRET=your_api_secret")
    
    print("\nThis version provides reliable image hosting that ReimagineHome can access.")
    print("\nOpen http://localhost:5000 in your browser")
    print("="*60 + "\n")
    app.run(port=5000, debug=True)