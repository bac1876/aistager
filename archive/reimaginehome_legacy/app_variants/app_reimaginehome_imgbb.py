import os
import time
import requests
import base64
import json
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv('.env.local')

app = Flask(__name__)
CORS(app)

# ReimagineHome API key
REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')

# ImgBB API key (free, get from https://imgbb.com/signup)
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY', 'YOUR_IMGBB_KEY')

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
        <p class="text-center text-gray-600 mb-8">Stage Your Actual Room with AI</p>
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="bg-green-50 border-l-4 border-green-400 p-4 mb-6">
                <p class="text-sm">
                    <strong>Ready to stage YOUR room!</strong> Upload a photo of your empty or 
                    partially furnished room and watch AI transform it.
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
                    <option value="DT-INT-001">Bohemian</option>
                </select>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Special Requests (Optional)</label>
                <textarea id="additionalPrompt" rows="2" class="w-full p-3 border rounded" 
                    placeholder="e.g., add a blue sofa, wooden coffee table"></textarea>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">API Key Options</label>
                <select id="apiKeyOption" class="w-full p-3 border rounded mb-2">
                    <option value="env">Use configured API key</option>
                    <option value="custom">Enter custom API key</option>
                </select>
                <input type="password" id="customApiKey" class="w-full p-3 border rounded hidden" 
                    placeholder="Enter your ReimagineHome API key">
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
        
        document.getElementById('apiKeyOption').addEventListener('change', (e) => {
            const customInput = document.getElementById('customApiKey');
            if (e.target.value === 'custom') {
                customInput.classList.remove('hidden');
            } else {
                customInput.classList.add('hidden');
            }
        });
        
        document.getElementById('fileInput').addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 5 * 1024 * 1024) {
                    alert('Please select an image smaller than 5MB');
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = (event) => {
                    const img = new Image();
                    img.onload = function() {
                        // Check dimensions (ReimagineHome requires 512x512 to 2048x2048)
                        if (img.width < 512 || img.height < 512) {
                            alert('Image must be at least 512x512 pixels');
                            return;
                        }
                        if (img.width > 2048 || img.height > 2048) {
                            alert('Image must be no larger than 2048x2048 pixels');
                            return;
                        }
                        
                        imageData = event.target.result;
                        document.getElementById('preview').src = imageData;
                        document.getElementById('preview').classList.remove('hidden');
                        
                        // Show dimensions
                        const status = document.getElementById('status');
                        status.innerHTML = `<p class="text-sm text-gray-600">Image: ${img.width}x${img.height} pixels</p>`;
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
            
            let apiKey = null;
            if (document.getElementById('apiKeyOption').value === 'custom') {
                apiKey = document.getElementById('customApiKey').value;
                if (!apiKey) {
                    alert('Please enter your API key');
                    return;
                }
            }
            
            btn.disabled = true;
            btn.textContent = 'Processing...';
            status.innerHTML = '';
            results.innerHTML = '';
            updateProgress(0, 'Starting...');
            
            try {
                const response = await fetch('/api/stage-room', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: imageData,
                        space_type: spaceType,
                        design_theme: designTheme,
                        additional_prompt: additionalPrompt,
                        api_key: apiKey
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    updateProgress(100, 'Complete!');
                    
                    status.innerHTML = `
                        <div class="bg-green-50 p-4 rounded">
                            <p class="text-green-800 font-semibold">✅ Staging job submitted successfully!</p>
                            <p class="text-sm text-green-600 mt-1">Job ID: ${data.job_id || 'N/A'}</p>
                        </div>
                    `;
                    
                    results.innerHTML = `
                        <div class="bg-blue-50 p-4 rounded mt-4">
                            <h3 class="font-semibold mb-2">What happens next?</h3>
                            <p class="text-sm text-gray-700">
                                ReimagineHome is now processing your image. In a production app:
                            </p>
                            <ul class="list-disc list-inside text-sm text-gray-600 mt-2">
                                <li>The staged image would be sent to your webhook URL</li>
                                <li>Processing typically takes 20-40 seconds</li>
                                <li>You would receive the staged room image URL</li>
                            </ul>
                        </div>
                        
                        <div class="mt-4">
                            <p class="text-sm text-gray-600">Your uploaded image:</p>
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

@app.route('/api/stage-room', methods=['POST'])
def stage_room():
    data = request.json
    image_data = data.get('image')
    space_type = data.get('space_type')
    design_theme = data.get('design_theme')
    additional_prompt = data.get('additional_prompt')
    custom_api_key = data.get('api_key')
    
    if not image_data or not space_type:
        return jsonify({
            'success': False,
            'error': 'Image and room type are required'
        })
    
    # Use custom API key if provided, otherwise use env variable
    api_key = custom_api_key or REIMAGINEHOME_API_KEY
    
    if not api_key:
        return jsonify({
            'success': False,
            'error': 'No API key available. Please provide one.'
        })
    
    headers = {'api-key': api_key}
    
    try:
        # Step 1: Upload image to temporary hosting
        # For demo, using ImgBB (free tier available)
        print("Uploading image...")
        
        # Extract base64 data
        base64_data = image_data.split(',')[1] if ',' in image_data else image_data
        
        # Upload to ImgBB
        upload_response = requests.post(
            'https://api.imgbb.com/1/upload',
            data={
                'key': IMGBB_API_KEY,
                'image': base64_data,
                'expiration': 600  # 10 minutes
            }
        )
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            if upload_data['success']:
                image_url = upload_data['data']['url']
                print(f"Image uploaded: {image_url}")
            else:
                return jsonify({
                    'success': False,
                    'error': f'ImgBB upload failed: {upload_data.get("error", {}).get("message", "Unknown error")}'
                })
        else:
            return jsonify({
                'success': False,
                'error': f'ImgBB upload failed with status {upload_response.status_code}'
            })
        
        # Step 2: Create masks
        print("Creating masks...")
        mask_response = requests.post(
            'https://api.reimaginehome.ai/v1/create_mask',
            headers=headers,
            json={'image_url': image_url}
        )
        
        if mask_response.status_code != 200:
            mask_error = mask_response.json()
            error_msg = mask_error.get('error_message', mask_error.get('error', 'Unknown error'))
            return jsonify({
                'success': False,
                'error': f'Mask creation failed: {error_msg}',
                'details': {
                    'status_code': mask_response.status_code,
                    'error_details': mask_error,
                    'image_url_used': image_url
                }
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
                    return jsonify({
                        'success': False,
                        'error': 'Mask creation failed'
                    })
        
        if not masks:
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
            'error': f'Internal Server Error: {str(e)}'
        })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI ROOM STAGER - REIMAGINEHOME")
    print("="*60)
    print(f"API Key: {'[OK] Configured' if REIMAGINEHOME_API_KEY else '[!] Not configured (can use custom)'}")
    print("\nThis version uploads YOUR actual room photos!")
    print("The AI will stage your specific room, not a generic image.")
    print("\nFor free image hosting:")
    print("1. Sign up at https://imgbb.com")
    print("2. Get API key from https://api.imgbb.com/")
    print("3. Add to .env.local: IMGBB_API_KEY=your-key")
    print("\nOpen http://localhost:5000 in your browser")
    print("="*60 + "\n")
    app.run(port=5000, debug=True)