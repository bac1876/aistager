import os
import time
import requests
import base64
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv
import json
from datetime import datetime
import random

load_dotenv('.env.local')

app = Flask(__name__)
CORS(app)

# ReimagineHome API key
REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')

print(f"ReimagineHome API configured: {'Yes' if REIMAGINEHOME_API_KEY else 'No'}")
print(f"ImgBB API configured: {'Yes' if IMGBB_API_KEY else 'No'}")

# Store job IDs for polling
ACTIVE_JOBS = {}

# Enhanced prompts for better quality
ENHANCED_PROMPTS = {
    'living_room': [
        'Transform this empty living room into a warm, inviting space with a plush sofa set, elegant coffee table, entertainment center, side tables with lamps, area rug, wall art, plants, and decorative accessories. Create a realistic, magazine-quality staged home.',
        'Stage this vacant living room with designer furniture including sectional sofa, modern coffee table, TV console, accent chairs, floor lamps, contemporary artwork, throw pillows, and stylish decor. Make it look move-in ready.',
        'Add high-end virtual staging to this living room: leather sofa, glass coffee table, media unit, reading chair, table lamps, abstract paintings, Persian rug, and curated accessories. Professional real estate staging quality.'
    ],
    'bedroom': [
        'Stage this empty bedroom with a luxurious king bed with upholstered headboard, matching nightstands with lamps, dresser, comfortable armchair, area rug, window treatments, wall art, and bedroom accessories.',
        'Transform this vacant bedroom into a serene retreat with queen bed, bedside tables, wardrobe, vanity mirror, ottoman, soft lighting, artwork, plants, and cozy textiles. Hotel-quality staging.',
        'Virtual stage this bedroom with modern platform bed, floating nightstands, chest of drawers, accent chair, pendant lights, minimalist art, textured rug, and sophisticated decor.'
    ],
    'kitchen': [
        'Enhance this empty kitchen with bar stools at the counter, decorative bowls with fruit, potted herbs, cookbook stand, coffee maker, and modern accessories. Make it feel lived-in and welcoming.',
        'Stage this kitchen with dining set, pendant lighting, kitchen island accessories, small appliances, wine rack, and decorative elements. Professional staging quality.',
        'Add virtual staging elements: breakfast nook furniture, counter accessories, hanging plants, kitchen cart, and stylish storage solutions.'
    ]
}

# HTML template with enhanced UI
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Room Stager - Enhanced Version</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Room Stager Pro</h1>
        <p class="text-center text-gray-600 mb-8">Enhanced virtual staging with multiple style options</p>
        
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
                        <option value="">AI Decides (Best Results)</option>
                        <option value="DT-INT-011">Modern</option>
                        <option value="DT-INT-003">Contemporary</option>
                        <option value="DT-INT-013">Scandinavian</option>
                        <option value="DT-INT-010">Minimal</option>
                    </select>
                </div>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Generation Mode</label>
                <div class="grid grid-cols-2 gap-4">
                    <label class="flex items-center p-3 border rounded cursor-pointer hover:bg-gray-50">
                        <input type="radio" name="mode" value="fast" checked class="mr-2">
                        <div>
                            <div class="font-medium">Fast (1 design)</div>
                            <div class="text-sm text-gray-600">Quick results</div>
                        </div>
                    </label>
                    <label class="flex items-center p-3 border rounded cursor-pointer hover:bg-gray-50">
                        <input type="radio" name="mode" value="quality" class="mr-2">
                        <div>
                            <div class="font-medium">Quality (3 designs)</div>
                            <div class="text-sm text-gray-600">Multiple options</div>
                        </div>
                    </label>
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
            
            <div id="result" class="mt-6 hidden">
                <h3 class="text-lg font-semibold mb-4">Choose Your Favorite Staged Room:</h3>
                <div id="resultsGrid" class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <!-- Results will be inserted here -->
                </div>
                <div id="selectedResult" class="hidden">
                    <h4 class="text-md font-semibold mb-2">Selected Design:</h4>
                    <img id="selectedImage" class="w-full rounded shadow-lg mb-4">
                    <div class="flex gap-2">
                        <a id="downloadBtn" class="inline-block bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600" download>
                            Download Image
                        </a>
                        <button id="regenerateBtn" class="inline-block bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                            Try Different Styles
                        </button>
                        <button id="retryBtn" class="inline-block bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600">
                            Enhance Quality
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let imageData = null;
        let selectedImageUrl = null;
        let currentImageUrl = null;
        
        function displayResults(imageUrls) {
            const resultsGrid = document.getElementById('resultsGrid');
            resultsGrid.innerHTML = '';
            
            imageUrls.forEach((url, index) => {
                const resultDiv = document.createElement('div');
                resultDiv.className = 'cursor-pointer hover:shadow-xl transition-shadow rounded overflow-hidden';
                resultDiv.innerHTML = `
                    <img src="${url}" class="w-full h-48 object-cover" alt="Option ${index + 1}">
                    <div class="p-2 bg-gray-50 text-center">
                        <span class="text-sm font-medium">Design ${index + 1}</span>
                    </div>
                `;
                
                resultDiv.addEventListener('click', () => selectImage(url, imageUrls));
                resultsGrid.appendChild(resultDiv);
            });
            
            // Auto-select if only one result
            if (imageUrls.length === 1) {
                selectImage(imageUrls[0], imageUrls);
            }
        }
        
        function selectImage(url, allUrls) {
            selectedImageUrl = url;
            document.getElementById('selectedResult').classList.remove('hidden');
            document.getElementById('selectedImage').src = url;
            document.getElementById('downloadBtn').href = url;
            
            // Highlight selected option
            const resultsGrid = document.getElementById('resultsGrid');
            const images = resultsGrid.querySelectorAll('div');
            images.forEach((div, index) => {
                if (allUrls[index] === url) {
                    div.classList.add('ring-2', 'ring-blue-500');
                } else {
                    div.classList.remove('ring-2', 'ring-blue-500');
                }
            });
        }
        
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
        
        async function stageRoom(retryMode = false) {
            if (!imageData && !currentImageUrl) {
                alert('Please upload a room photo first');
                return;
            }
            
            const btn = document.getElementById('stageBtn');
            const status = document.getElementById('status');
            const progress = document.getElementById('progress');
            const progressBar = document.getElementById('progressBar');
            const progressText = document.getElementById('progressText');
            
            btn.disabled = true;
            btn.textContent = 'Processing...';
            progress.classList.remove('hidden');
            document.getElementById('result').classList.add('hidden');
            
            // Show initial progress
            progressBar.style.width = '10%';
            progressText.textContent = 'Uploading image...';
            
            const mode = document.querySelector('input[name="mode"]:checked').value;
            
            try {
                const response = await fetch('/api/stage-enhanced', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: imageData,
                        image_url: currentImageUrl,
                        space_type: document.getElementById('spaceType').value,
                        design_theme: document.getElementById('designTheme').value,
                        mode: mode,
                        retry_mode: retryMode
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const jobId = data.job_id;
                    currentImageUrl = data.image_url;
                    status.innerHTML = '<div class="bg-green-50 p-4 rounded"><p class="text-green-800">Job submitted! Creating your designs...</p></div>';
                    
                    // Poll for results
                    progressBar.style.width = '30%';
                    progressText.textContent = 'AI is staging your room...';
                    
                    let attempts = 0;
                    const maxAttempts = 30; // 60 seconds
                    
                    const pollInterval = setInterval(async () => {
                        attempts++;
                        const progress = Math.min(30 + (attempts * 2), 90);
                        progressBar.style.width = progress + '%';
                        progressText.textContent = `Processing... ${attempts * 2}s`;
                        
                        try {
                            const pollResponse = await fetch(`/api/poll-result/${jobId}`);
                            const pollData = await pollResponse.json();
                            
                            if (pollData.completed) {
                                clearInterval(pollInterval);
                                progressBar.style.width = '100%';
                                progressText.textContent = 'Complete!';
                                
                                if (pollData.output_urls && pollData.output_urls.length > 0) {
                                    document.getElementById('result').classList.remove('hidden');
                                    displayResults(pollData.output_urls);
                                    status.innerHTML = '<div class="bg-green-50 p-4 rounded"><p class="text-green-800 font-semibold">✨ Your room has been staged! Select your favorite design below.</p></div>';
                                } else if (pollData.output_url) {
                                    // Fallback for single image
                                    document.getElementById('result').classList.remove('hidden');
                                    displayResults([pollData.output_url]);
                                    status.innerHTML = '<div class="bg-green-50 p-4 rounded"><p class="text-green-800 font-semibold">✨ Your room has been staged!</p></div>';
                                } else {
                                    status.innerHTML = '<div class="bg-yellow-50 p-4 rounded"><p class="text-yellow-800">Processing completed but no image received. Please try again.</p></div>';
                                }
                                
                                setTimeout(() => progress.classList.add('hidden'), 2000);
                            } else if (attempts >= maxAttempts) {
                                clearInterval(pollInterval);
                                status.innerHTML = '<div class="bg-yellow-50 p-4 rounded"><p class="text-yellow-800">Processing is taking longer than expected. Please try again in a minute.</p></div>';
                                progress.classList.add('hidden');
                            }
                        } catch (error) {
                            console.error('Poll error:', error);
                        }
                    }, 2000);
                    
                } else {
                    progress.classList.add('hidden');
                    status.innerHTML = `<div class="bg-red-50 p-4 rounded"><p class="text-red-800">Error: ${data.error}</p></div>`;
                }
            } catch (error) {
                progress.classList.add('hidden');
                status.innerHTML = `<div class="bg-red-50 p-4 rounded"><p class="text-red-800">Error: ${error.message}</p></div>`;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Stage My Room';
            }
        }
        
        document.getElementById('stageBtn').addEventListener('click', () => stageRoom(false));
        
        // Regenerate button
        document.getElementById('regenerateBtn').addEventListener('click', () => {
            document.getElementById('result').classList.add('hidden');
            document.getElementById('selectedResult').classList.add('hidden');
            stageRoom(false);
        });
        
        // Retry with enhanced prompts
        document.getElementById('retryBtn').addEventListener('click', () => {
            document.getElementById('result').classList.add('hidden');
            document.getElementById('selectedResult').classList.add('hidden');
            stageRoom(true);
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stage-enhanced', methods=['POST'])
def stage_enhanced():
    """Enhanced staging endpoint with retry logic and better prompts"""
    data = request.json
    image_data = data.get('image')
    image_url = data.get('image_url')
    space_type = data.get('space_type')
    design_theme = data.get('design_theme')
    mode = data.get('mode', 'fast')
    retry_mode = data.get('retry_mode', False)
    
    if not (image_data or image_url) or not space_type:
        return jsonify({'success': False, 'error': 'Missing required fields'})
    
    try:
        # Upload image if not already uploaded
        if not image_url:
            # Extract base64 data
            base64_data = image_data.split(',')[1] if ',' in image_data else image_data
            
            # Upload to ImgBB
            if not IMGBB_API_KEY:
                return jsonify({'success': False, 'error': 'Image hosting not configured'})
                
            print("Uploading to ImgBB...")
            imgbb_response = requests.post(
                'https://api.imgbb.com/1/upload',
                data={
                    'key': IMGBB_API_KEY,
                    'image': base64_data,
                    'name': f'room_{int(time.time())}'
                },
                timeout=30
            )
            
            if imgbb_response.status_code != 200 or not imgbb_response.json().get('success'):
                return jsonify({'success': False, 'error': 'Failed to upload image'})
                
            image_url = imgbb_response.json()['data']['url']
            print(f"Image uploaded: {image_url}")
        
        # Call ReimagineHome API
        headers = {'api-key': REIMAGINEHOME_API_KEY}
        
        # Step 1: Create masks
        print("Creating masks...")
        mask_response = requests.post(
            'https://api.reimaginehome.ai/v1/create_mask',
            headers=headers,
            json={'image_url': image_url}
        )
        
        if mask_response.status_code != 200:
            error_msg = mask_response.json().get('error_message', 'Failed to process image')
            return jsonify({'success': False, 'error': error_msg})
            
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
        
        if not masks:
            return jsonify({'success': False, 'error': 'Failed to process room layout'})
            
        # Step 3: Generate staged image with enhanced prompts
        print("Generating staged image...")
        
        # Use ALL masks for comprehensive staging
        mask_urls = [mask['url'] for mask in masks]
        
        # Select prompt based on retry mode and room type
        if retry_mode:
            # Use enhanced prompts for retry
            room_key = {
                'ST-INT-011': 'living_room',
                'ST-INT-003': 'bedroom',
                'ST-INT-009': 'kitchen'
            }.get(space_type, 'living_room')
            
            prompts = ENHANCED_PROMPTS.get(room_key, ENHANCED_PROMPTS['living_room'])
            prompt = random.choice(prompts)
        else:
            # Use standard enhanced prompts
            space_prompts = {
                'ST-INT-011': 'Virtual stage this empty living room with comfortable seating, coffee table, TV stand, side tables, lamps, artwork, rugs, and decorative accessories. Create a welcoming, lived-in atmosphere with professional staging quality.',
                'ST-INT-003': 'Virtual stage this empty bedroom with a bed, nightstands, dresser, reading chair, lamps, artwork, rugs, and bedroom decor. Make it cozy and inviting with hotel-quality staging.',
                'ST-INT-009': 'Virtual stage this empty kitchen with modern appliances, kitchen island or dining table, bar stools, decorative bowls, plants, and kitchen accessories. Create a warm, functional space.',
                'ST-INT-002': 'Virtual stage this empty bathroom with vanity accessories, towels, bath mats, shower curtain, storage baskets, and bathroom decor. Make it spa-like and inviting.',
                'ST-INT-004': 'Virtual stage this empty dining room with dining table, chairs, chandelier, buffet or sideboard, artwork, and dining accessories. Create an elegant entertaining space.'
            }
            prompt = space_prompts.get(space_type, 'Virtual stage this empty room with appropriate furniture and decor')
        
        # Add design theme to prompt if specified
        if design_theme:
            theme_descriptions = {
                'DT-INT-011': 'modern style with clean lines and contemporary furniture',
                'DT-INT-003': 'contemporary style with current trends and comfortable furnishings',
                'DT-INT-013': 'Scandinavian style with minimalist furniture and light colors',
                'DT-INT-010': 'minimal style with essential furniture and clean aesthetics'
            }
            theme_desc = theme_descriptions.get(design_theme, '')
            if theme_desc:
                prompt += f' Use {theme_desc}.'
        
        # Determine generation count based on mode
        generation_count = 3 if mode == 'quality' else 1
        
        generation_payload = {
            'image_url': image_url,
            'mask_urls': mask_urls,
            'mask_category': 'furnishing',
            'space_type': space_type,
            'generation_count': generation_count,
            'additional_prompt': prompt
        }
        
        if design_theme:
            generation_payload['design_theme'] = design_theme
            
        gen_response = requests.post(
            'https://api.reimaginehome.ai/v1/generate_image',
            headers=headers,
            json=generation_payload
        )
        
        if gen_response.status_code != 200:
            return jsonify({'success': False, 'error': 'Failed to start staging process'})
            
        reimagine_job_id = gen_response.json().get('data', {}).get('job_id', 'unknown')
        
        # Store job for polling
        ACTIVE_JOBS[reimagine_job_id] = {
            'status': 'processing',
            'created_at': time.time()
        }
        
        return jsonify({
            'success': True,
            'job_id': reimagine_job_id,
            'image_url': image_url,
            'message': 'Staging job submitted successfully!'
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/poll-result/<job_id>')
def poll_result(job_id):
    """Poll for staging results"""
    headers = {'api-key': REIMAGINEHOME_API_KEY}
    
    try:
        # Check job status
        response = requests.get(
            f'https://api.reimaginehome.ai/v1/generate_image/{job_id}',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            job_status = data.get('job_status')
            
            if job_status == 'done':
                # Check for both possible field names
                output_urls = data.get('output_urls', []) or data.get('generated_images', [])
                if output_urls:
                    return jsonify({
                        'completed': True,
                        'output_urls': output_urls,  # Send all URLs
                        'output_url': output_urls[0]  # Keep for backward compatibility
                    })
                else:
                    return jsonify({
                        'completed': True,
                        'output_url': None
                    })
            else:
                return jsonify({
                    'completed': False,
                    'status': job_status
                })
        else:
            return jsonify({
                'completed': False,
                'error': 'Failed to check status'
            })
            
    except Exception as e:
        print(f"Poll error: {str(e)}")
        return jsonify({
            'completed': False,
            'error': str(e)
        })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'reimaginehome_configured': bool(REIMAGINEHOME_API_KEY),
        'imgbb_configured': bool(IMGBB_API_KEY)
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI ROOM STAGER - ENHANCED VERSION")
    print("="*60)
    print("Features:")
    print("- Multiple generation options (1 or 3 designs)")
    print("- Enhanced prompts for better quality")
    print("- Retry with different prompts")
    print("- Professional staging quality")
    print("="*60)
    app.run(host='0.0.0.0', port=5000, debug=True)