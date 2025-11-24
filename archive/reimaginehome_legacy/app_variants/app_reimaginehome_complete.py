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

print(f"ReimagineHome API configured: {'Yes' if REIMAGINEHOME_API_KEY else 'No'}")

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
                    <strong>Welcome!</strong> Transform empty rooms into beautifully staged spaces 
                    using ReimagineHome's AI technology.
                </p>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Upload Room Photo</label>
                <input type="file" id="fileInput" accept="image/*" class="w-full p-2 border rounded">
                <img id="preview" class="mt-4 max-h-64 mx-auto hidden rounded shadow">
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
                    <option value="contemporary">Contemporary</option>
                    <option value="modern">Modern</option>
                    <option value="traditional">Traditional</option>
                    <option value="minimalist">Minimalist</option>
                    <option value="scandinavian">Scandinavian</option>
                    <option value="bohemian">Bohemian</option>
                    <option value="industrial">Industrial</option>
                    <option value="rustic">Rustic</option>
                </select>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Color Preferences (Optional)</label>
                <input type="text" id="colorPreference" class="w-full p-3 border rounded" 
                    placeholder="e.g., neutral tones, light wood accents">
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Additional Instructions (Optional)</label>
                <textarea id="additionalPrompt" rows="3" class="w-full p-3 border rounded" 
                    placeholder="e.g., add a large L-shaped sofa, round coffee table, and textured rug"></textarea>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Number of Variations</label>
                <select id="generationCount" class="w-full p-3 border rounded">
                    <option value="1">1 Design</option>
                    <option value="2">2 Designs</option>
                    <option value="3">3 Designs</option>
                </select>
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
        
        // Load space types
        async function loadSpaceTypes() {
            try {
                const response = await fetch('/api/space-types');
                const data = await response.json();
                
                if (data.success) {
                    const select = document.getElementById('spaceType');
                    select.innerHTML = '<option value="">Select a room type</option>';
                    
                    // Add interior spaces
                    if (data.interior_spaces) {
                        const group = document.createElement('optgroup');
                        group.label = 'Interior Spaces';
                        
                        data.interior_spaces.forEach(space => {
                            const option = document.createElement('option');
                            option.value = space.code;
                            option.textContent = space.name;
                            group.appendChild(option);
                        });
                        
                        select.appendChild(group);
                    }
                    
                    // Add exterior spaces
                    if (data.exterior_spaces) {
                        const group = document.createElement('optgroup');
                        group.label = 'Exterior Spaces';
                        
                        data.exterior_spaces.forEach(space => {
                            const option = document.createElement('option');
                            option.value = space.code;
                            option.textContent = space.name;
                            group.appendChild(option);
                        });
                        
                        select.appendChild(group);
                    }
                }
            } catch (error) {
                console.error('Failed to load space types:', error);
            }
        }
        
        // Load space types on page load
        loadSpaceTypes();
        
        document.getElementById('fileInput').addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
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
            const generationCount = parseInt(document.getElementById('generationCount').value);
            
            if (!imageData) {
                alert('Please upload a room photo');
                return;
            }
            
            if (!spaceType) {
                alert('Please select a room type');
                return;
            }
            
            btn.disabled = true;
            btn.textContent = 'Processing Your Room...';
            status.innerHTML = '<div class="text-blue-600">🎨 Creating masks and staging your room... This may take 30-60 seconds.</div>';
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
                        additional_prompt: additionalPrompt,
                        generation_count: generationCount
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    status.innerHTML = '<div class="text-green-600">✅ Your room has been staged!</div>';
                    
                    // Show results
                    results.innerHTML = '<div class="grid grid-cols-1 gap-4">';
                    
                    // Show original
                    results.innerHTML += `
                        <div>
                            <h3 class="font-semibold mb-2">Original Room</h3>
                            <img src="${imageData}" class="w-full rounded shadow">
                        </div>
                    `;
                    
                    // Show staged versions
                    if (data.images && data.images.length > 0) {
                        data.images.forEach((img, idx) => {
                            results.innerHTML += `
                                <div>
                                    <h3 class="font-semibold mb-2">Staged Version ${idx + 1}</h3>
                                    <img src="${img}" class="w-full rounded shadow">
                                    <a href="${img}" download="staged_room_${idx + 1}.jpg" 
                                       class="inline-block mt-2 text-blue-600 hover:underline">
                                        Download
                                    </a>
                                </div>
                            `;
                        });
                    }
                    
                    results.innerHTML += '</div>';
                    
                    if (data.credits_consumed !== undefined) {
                        status.innerHTML += `<div class="text-sm text-gray-600 mt-2">Credits used: ${data.credits_consumed}</div>`;
                    }
                } else {
                    status.innerHTML = '<div class="text-red-600">❌ ' + (data.error || 'Staging failed') + '</div>';
                    if (data.details) {
                        results.innerHTML = '<pre class="bg-gray-100 p-4 rounded text-sm">' + 
                            JSON.stringify(data.details, null, 2) + '</pre>';
                    }
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
    
    # Return cached data if available
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
            
            # Transform the data for easier use
            result = {
                'success': True,
                'interior_spaces': [],
                'exterior_spaces': []
            }
            
            # Process interior spaces
            for space in data.get('interior_spaces', []):
                for code, name in space.items():
                    result['interior_spaces'].append({
                        'code': code,
                        'name': name
                    })
            
            # Process exterior spaces
            for space in data.get('exterior_spaces', []):
                for code, name in space.items():
                    result['exterior_spaces'].append({
                        'code': code,
                        'name': name
                    })
            
            # Cache the result
            SPACE_TYPES_CACHE = result
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to fetch space types: {response.status_code}'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/stage', methods=['POST'])
def stage_room():
    data = request.json
    image_data = data.get('image')
    space_type = data.get('space_type')
    design_theme = data.get('design_theme')
    color_preference = data.get('color_preference')
    additional_prompt = data.get('additional_prompt')
    generation_count = data.get('generation_count', 1)
    
    if not image_data or not space_type:
        return jsonify({
            'success': False,
            'error': 'Image and room type are required'
        })
    
    headers = {'api-key': REIMAGINEHOME_API_KEY}
    
    try:
        # Upload image to a temporary storage (in production, use cloud storage)
        # For this example, we'll use a public image URL
        # In production, you'd upload to S3, CloudFront, etc. and get a public URL
        
        # Step 1: Create masks
        print("Creating masks...")
        mask_response = requests.post(
            'https://api.reimaginehome.ai/v1/create_mask',
            headers=headers,
            json={
                'image_url': 'https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800'  # Placeholder
            }
        )
        
        if mask_response.status_code != 200:
            return jsonify({
                'success': False,
                'error': 'Failed to create masks',
                'details': mask_response.json()
            })
        
        mask_job_id = mask_response.json()['data']['job_id']
        
        # Step 2: Wait for masks
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
        
        # Step 3: Generate staged image
        print("Generating staged image...")
        
        # For virtual staging, use furnishing masks
        furnishing_masks = [m['url'] for m in masks if 'furnishing' in m['category']]
        mask_urls = furnishing_masks if furnishing_masks else [masks[0]['url']]
        
        generation_payload = {
            'image_url': 'https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800',  # Placeholder
            'mask_urls': mask_urls,
            'mask_category': 'furnishing',
            'space_type': space_type,
            'generation_count': generation_count
        }
        
        # Add optional parameters
        if design_theme:
            generation_payload['design_theme'] = design_theme
        if color_preference:
            generation_payload['color_preference'] = color_preference
        if additional_prompt:
            generation_payload['additional_prompt'] = additional_prompt
            
        # Note: In production, you'd provide a webhook_url
        # generation_payload['webhook_url'] = 'https://your-app.com/reimagine-webhook'
        
        gen_response = requests.post(
            'https://api.reimaginehome.ai/v1/generate_image',
            headers=headers,
            json=generation_payload
        )
        
        if gen_response.status_code == 200:
            result = gen_response.json()
            
            # Since we're not using webhooks in this example, 
            # we'll simulate waiting for the result
            # In production, you'd handle this via webhook
            
            return jsonify({
                'success': True,
                'message': 'Staging initiated successfully',
                'job_id': result.get('job_id'),
                'note': 'In production, results would be delivered via webhook',
                'images': ['https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800'],  # Placeholder
                'credits_consumed': result.get('credits_consumed', 0)
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
    print("AI ROOM STAGER - REIMAGINEHOME")
    print("="*60)
    print(f"API Key configured: {'Yes' if REIMAGINEHOME_API_KEY else 'No'}")
    print("\nNOTE: This implementation requires:")
    print("1. Upload images to cloud storage (S3, CloudFront, etc)")
    print("2. Implement webhook endpoint for async results")
    print("3. Handle job status polling if not using webhooks")
    print("\nFor production use, please implement:")
    print("- Image upload to cloud storage")
    print("- Webhook endpoint to receive results")
    print("- Proper error handling and retry logic")
    print("\nOpen http://localhost:5000 in your browser")
    print("="*60 + "\n")
    app.run(port=5000, debug=True)