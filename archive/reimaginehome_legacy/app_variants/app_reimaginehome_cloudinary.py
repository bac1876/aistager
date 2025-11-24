import os
import time
import requests
import base64
import json
import cloudinary
import cloudinary.uploader
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv('.env.local')

app = Flask(__name__)
CORS(app)

# ReimagineHome API key
REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')

# Cloudinary configuration (free tier available)
# Sign up at https://cloudinary.com
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

print(f"ReimagineHome API configured: {'Yes' if REIMAGINEHOME_API_KEY else 'No'}")
print(f"Cloudinary configured: {'Yes' if CLOUDINARY_CONFIGURED else 'No'}")

# Cache for space types
SPACE_TYPES_CACHE = None

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
        <p class="text-center text-gray-600 mb-8">Powered by ReimagineHome AI</p>
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
                <p class="text-sm">
                    <strong>Welcome!</strong> Upload a photo of your empty or partially furnished room 
                    and let AI stage it with beautiful furniture and decor.
                </p>
            </div>
            
            ''' + ('''
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
                <p class="text-sm">
                    <strong>Note:</strong> Image upload requires Cloudinary configuration. 
                    Sign up for free at <a href="https://cloudinary.com" target="_blank" class="text-blue-600 underline">cloudinary.com</a>
                    and add credentials to .env.local
                </p>
            </div>
            ''' if not CLOUDINARY_CONFIGURED else '') + '''
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Upload Your Room Photo</label>
                <input type="file" id="fileInput" accept="image/*" class="w-full p-2 border rounded">
                <img id="preview" class="mt-4 max-h-64 mx-auto hidden rounded shadow">
                <p class="text-xs text-gray-500 mt-2">Upload an empty or partially furnished room for best results</p>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Select Room Type</label>
                <select id="spaceType" class="w-full p-3 border rounded">
                    <option value="">Loading room types...</option>
                </select>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Design Style</label>
                <select id="designTheme" class="w-full p-3 border rounded">
                    <option value="">None (AI decides)</option>
                </select>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Color Preferences (Optional)</label>
                <input type="text" id="colorPreference" class="w-full p-3 border rounded" 
                    placeholder="e.g., warm neutral tones, light wood">
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Additional Instructions (Optional)</label>
                <textarea id="additionalPrompt" rows="3" class="w-full p-3 border rounded" 
                    placeholder="e.g., add a large sectional sofa, modern coffee table"></textarea>
            </div>
            
            <button id="generateBtn" class="w-full bg-blue-500 text-white py-3 rounded hover:bg-blue-600 font-semibold">
                Stage My Room
            </button>
            
            <div id="status" class="mt-4 text-center"></div>
            <div id="results" class="mt-6"></div>
        </div>
    </div>
    
    <script>
        let imageData = null;
        let spaceTypes = {};
        let designThemes = {};
        
        // Load space types and design themes
        async function loadOptions() {
            try {
                // Load space types
                const spaceResponse = await fetch('/api/space-types');
                const spaceData = await spaceResponse.json();
                
                if (spaceData.success) {
                    const select = document.getElementById('spaceType');
                    select.innerHTML = '<option value="">Select a room type</option>';
                    
                    // Add interior spaces
                    if (spaceData.interior_spaces) {
                        const group = document.createElement('optgroup');
                        group.label = 'Interior Spaces';
                        
                        spaceData.interior_spaces.forEach(space => {
                            spaceTypes[space.code] = space.name;
                            const option = document.createElement('option');
                            option.value = space.code;
                            option.textContent = space.name;
                            group.appendChild(option);
                        });
                        
                        select.appendChild(group);
                    }
                }
                
                // Load design themes
                const themeResponse = await fetch('/api/design-themes');
                const themeData = await themeResponse.json();
                
                if (themeData.success) {
                    const select = document.getElementById('designTheme');
                    select.innerHTML = '<option value="">None (AI decides)</option>';
                    
                    if (themeData.interior_themes) {
                        themeData.interior_themes.forEach(theme => {
                            designThemes[theme.code] = theme.name;
                            const option = document.createElement('option');
                            option.value = theme.code;
                            option.textContent = theme.name;
                            select.appendChild(option);
                        });
                    }
                }
            } catch (error) {
                console.error('Failed to load options:', error);
            }
        }
        
        // Load options on page load
        loadOptions();
        
        document.getElementById('fileInput').addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                // Check file size (max 10MB for Cloudinary free tier)
                if (file.size > 10 * 1024 * 1024) {
                    alert('File size must be less than 10MB');
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
        
        document.getElementById('generateBtn').addEventListener('click', async () => {
            const btn = document.getElementById('generateBtn');
            const status = document.getElementById('status');
            const results = document.getElementById('results');
            
            const spaceType = document.getElementById('spaceType').value;
            const designTheme = document.getElementById('designTheme').value;
            const colorPreference = document.getElementById('colorPreference').value;
            const additionalPrompt = document.getElementById('additionalPrompt').value;
            
            if (!imageData) {
                alert('Please upload a room photo');
                return;
            }
            
            if (!spaceType) {
                alert('Please select a room type');
                return;
            }
            
            btn.disabled = true;
            btn.textContent = 'Processing...';
            status.innerHTML = '<div class="text-blue-600">Uploading image and creating masks...</div>';
            results.innerHTML = '';
            
            try {
                const response = await fetch('/api/stage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: imageData,
                        space_type: spaceType,
                        design_theme: designTheme,
                        color_preference: colorPreference,
                        additional_prompt: additionalPrompt
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    status.innerHTML = '<div class="text-green-600">✅ Staging complete!</div>';
                    
                    if (data.job_id) {
                        status.innerHTML += '<div class="text-sm text-gray-600 mt-2">Job ID: ' + data.job_id + '</div>';
                    }
                    
                    // Show comparison
                    results.innerHTML = `
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <h3 class="font-semibold mb-2">Original Room</h3>
                                <img src="${imageData}" class="w-full rounded shadow">
                            </div>
                            <div>
                                <h3 class="font-semibold mb-2">Staged Room</h3>
                                <div class="bg-gray-100 rounded p-8 text-center">
                                    <p class="text-gray-600">In production, the staged image would appear here</p>
                                    <p class="text-sm text-gray-500 mt-2">Results are delivered via webhook</p>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    if (data.image_url) {
                        results.innerHTML += `
                            <div class="mt-4 p-4 bg-blue-50 rounded">
                                <p class="text-sm"><strong>Your image URL:</strong> 
                                <a href="${data.image_url}" target="_blank" class="text-blue-600 underline break-all">${data.image_url}</a></p>
                            </div>
                        `;
                    }
                } else {
                    status.innerHTML = '<div class="text-red-600">❌ ' + (data.error || 'Staging failed') + '</div>';
                }
            } catch (error) {
                status.innerHTML = '<div class="text-red-600">❌ Error: ' + error.message + '</div>';
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

@app.route('/api/space-types', methods=['GET'])
def get_space_types():
    global SPACE_TYPES_CACHE
    
    if SPACE_TYPES_CACHE:
        return jsonify(SPACE_TYPES_CACHE)
    
    headers = {'api-key': REIMAGINEHOME_API_KEY}
    
    try:
        response = requests.get(
            'https://api.reimaginehome.ai/v1/get-space-type-list',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            
            result = {
                'success': True,
                'interior_spaces': [],
                'exterior_spaces': []
            }
            
            for space in data.get('interior_spaces', []):
                for code, name in space.items():
                    result['interior_spaces'].append({'code': code, 'name': name})
            
            for space in data.get('exterior_spaces', []):
                for code, name in space.items():
                    result['exterior_spaces'].append({'code': code, 'name': name})
            
            SPACE_TYPES_CACHE = result
            return jsonify(result)
    except Exception as e:
        pass
    
    return jsonify({'success': False, 'error': 'Failed to load space types'})

@app.route('/api/design-themes', methods=['GET'])
def get_design_themes():
    headers = {'api-key': REIMAGINEHOME_API_KEY}
    
    try:
        response = requests.get(
            'https://api.reimaginehome.ai/v1/get-design-theme-list',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            
            result = {
                'success': True,
                'interior_themes': [],
                'exterior_themes': []
            }
            
            for theme in data.get('interior_themes', []):
                for code, name in theme.items():
                    result['interior_themes'].append({'code': code, 'name': name})
            
            return jsonify(result)
    except Exception as e:
        pass
    
    return jsonify({'success': False, 'error': 'Failed to load themes'})

@app.route('/api/stage', methods=['POST'])
def stage_room():
    data = request.json
    image_data = data.get('image')
    space_type = data.get('space_type')
    design_theme = data.get('design_theme')
    color_preference = data.get('color_preference')
    additional_prompt = data.get('additional_prompt')
    
    if not image_data or not space_type:
        return jsonify({
            'success': False,
            'error': 'Image and room type are required'
        })
    
    headers = {'api-key': REIMAGINEHOME_API_KEY}
    
    try:
        # Step 1: Upload image to Cloudinary
        if CLOUDINARY_CONFIGURED:
            print("Uploading image to Cloudinary...")
            
            # Upload the base64 image
            upload_result = cloudinary.uploader.upload(
                image_data,
                folder="reimaginehome_staging",
                resource_type="image"
            )
            
            image_url = upload_result['secure_url']
            print(f"Image uploaded: {image_url}")
        else:
            return jsonify({
                'success': False,
                'error': 'Image hosting not configured. Please set up Cloudinary.'
            })
        
        # Step 2: Create masks
        print("Creating masks...")
        mask_response = requests.post(
            'https://api.reimaginehome.ai/v1/create_mask',
            headers=headers,
            json={'image_url': image_url}
        )
        
        if mask_response.status_code != 200:
            return jsonify({
                'success': False,
                'error': 'Failed to create masks',
                'details': mask_response.json()
            })
        
        mask_job_id = mask_response.json()['data']['job_id']
        
        # Step 3: Wait for masks
        masks = None
        for _ in range(30):
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
        
        if not masks:
            return jsonify({
                'success': False,
                'error': 'Mask creation timed out'
            })
        
        # Step 4: Generate staged image
        print("Generating staged image...")
        
        # Use furnishing masks for staging
        furnishing_masks = [m['url'] for m in masks if 'furnishing' in m['category']]
        
        # If no furnishing masks, use all masks
        if not furnishing_masks:
            # For empty rooms, we might need to use architectural masks
            mask_urls = [m['url'] for m in masks]
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
        if color_preference:
            generation_payload['color_preference'] = color_preference
        if additional_prompt:
            generation_payload['additional_prompt'] = additional_prompt
            
        gen_response = requests.post(
            'https://api.reimaginehome.ai/v1/generate_image',
            headers=headers,
            json=generation_payload
        )
        
        if gen_response.status_code == 200:
            result = gen_response.json()
            
            return jsonify({
                'success': True,
                'message': 'Staging initiated successfully!',
                'job_id': result.get('job_id'),
                'image_url': image_url,
                'note': 'Results will be delivered via webhook in production',
                'masks_found': len(masks),
                'masks_used': len(mask_urls)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate staged image',
                'details': gen_response.json()
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
    print("AI ROOM STAGER - REIMAGINEHOME (WITH IMAGE UPLOAD)")
    print("="*60)
    print(f"ReimagineHome API: {'[OK] Configured' if REIMAGINEHOME_API_KEY else '[X] Not configured'}")
    print(f"Cloudinary: {'[OK] Configured' if CLOUDINARY_CONFIGURED else '[X] Not configured'}")
    
    if not CLOUDINARY_CONFIGURED:
        print("\nTo enable image upload:")
        print("1. Sign up at https://cloudinary.com (free tier available)")
        print("2. Add to .env.local:")
        print("   CLOUDINARY_CLOUD_NAME=your-cloud-name")
        print("   CLOUDINARY_API_KEY=your-api-key")
        print("   CLOUDINARY_API_SECRET=your-api-secret")
    
    print("\nNOTE: This version uploads YOUR actual images for staging")
    print("Results are delivered via webhook (not shown in UI)")
    
    print("\nOpen http://localhost:5000 in your browser")
    print("="*60 + "\n")
    app.run(port=5000, debug=True)