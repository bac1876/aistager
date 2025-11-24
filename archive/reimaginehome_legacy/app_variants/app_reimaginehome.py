import os
import time
import requests
import base64
import io
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv

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
        <p class="text-center text-gray-600 mb-8">Powered by ReimagineHome AI</p>
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
                <p class="text-sm">
                    <strong>Welcome!</strong> ReimagineHome offers professional virtual staging and 
                    room redesign powered by AI. Virtual staging works best with empty rooms, 
                    while redesign works with furnished rooms.
                </p>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Upload Room Photo</label>
                <input type="file" id="fileInput" accept="image/*" class="w-full p-2 border rounded">
                <img id="preview" class="mt-4 max-h-64 mx-auto hidden rounded shadow">
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Select Mode</label>
                <select id="modeSelect" class="w-full p-3 border rounded">
                    <option value="virtual_staging">Virtual Staging (Empty to Furnished)</option>
                    <option value="redesign">Redesign (Change Existing Furniture)</option>
                </select>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Select Room Type</label>
                <select id="roomType" class="w-full p-3 border rounded">
                    <option value="Living Room">Living Room</option>
                    <option value="Bedroom">Bedroom</option>
                    <option value="Kitchen">Kitchen</option>
                    <option value="Bathroom">Bathroom</option>
                    <option value="Dining Room">Dining Room</option>
                    <option value="Home Office">Home Office</option>
                </select>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Select Style</label>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                    <button class="style-btn p-3 border rounded hover:bg-blue-50" data-style="Modern">Modern</button>
                    <button class="style-btn p-3 border rounded hover:bg-blue-50" data-style="Scandinavian">Scandinavian</button>
                    <button class="style-btn p-3 border rounded hover:bg-blue-50" data-style="Industrial">Industrial</button>
                    <button class="style-btn p-3 border rounded hover:bg-blue-50" data-style="Minimalist">Minimalist</button>
                    <button class="style-btn p-3 border rounded hover:bg-blue-50" data-style="Traditional">Traditional</button>
                    <button class="style-btn p-3 border rounded hover:bg-blue-50" data-style="Bohemian">Bohemian</button>
                </div>
            </div>
            
            <div class="mb-6" id="aiInterventionSection">
                <label class="block text-sm font-medium mb-2">AI Intervention Level (Virtual Staging Only)</label>
                <select id="aiIntervention" class="w-full p-3 border rounded">
                    <option value="Very Low">Very Low - Minimal changes</option>
                    <option value="Low">Low - Conservative staging</option>
                    <option value="Mid" selected>Mid - Balanced staging</option>
                    <option value="Extreme">Extreme - Complete transformation</option>
                </select>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Additional Instructions (Optional)</label>
                <textarea id="requirements" rows="3" class="w-full p-3 border rounded" 
                    placeholder="e.g., Add plants, warm lighting, cozy atmosphere"></textarea>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">API Key (Optional)</label>
                <input type="password" id="apiKey" class="w-full p-3 border rounded" 
                    placeholder="Enter your ReimagineHome API key">
                <p class="text-xs text-gray-500 mt-2">
                    Get your API key from <a href="https://www.reimaginehome.ai" target="_blank" class="text-blue-600 underline">reimaginehome.ai</a>
                </p>
            </div>
            
            <button id="generateBtn" class="w-full bg-blue-500 text-white py-3 rounded hover:bg-blue-600 font-semibold">
                Transform My Room
            </button>
            
            <div id="apiKeyNotice" class="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded hidden">
                <p class="text-sm">
                    <strong>Note:</strong> You need a ReimagineHome API key. 
                    <br>Sign up at <a href="https://www.reimaginehome.ai" target="_blank" class="text-blue-600 underline">reimaginehome.ai</a>
                    <br>Then add it to your .env.local file as REIMAGINEHOME_API_KEY=your-key-here
                </p>
            </div>
            
            <div id="status" class="mt-4 text-center"></div>
            <div id="results" class="mt-6"></div>
        </div>
    </div>
    
    <script>
        let imageData = null;
        let selectedStyle = 'Modern';
        const hasApiKey = ''' + ('true' if REIMAGINEHOME_API_KEY else 'false') + ''';
        
        if (!hasApiKey) {
            document.getElementById('apiKeyNotice').classList.remove('hidden');
        }
        
        // Show/hide AI intervention based on mode
        document.getElementById('modeSelect').addEventListener('change', (e) => {
            const aiSection = document.getElementById('aiInterventionSection');
            if (e.target.value === 'virtual_staging') {
                aiSection.style.display = 'block';
            } else {
                aiSection.style.display = 'none';
            }
        });
        
        // Style selection
        document.querySelectorAll('.style-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.style-btn').forEach(b => b.classList.remove('bg-blue-100'));
                btn.classList.add('bg-blue-100');
                selectedStyle = btn.dataset.style;
            });
        });
        
        // Select first style by default
        document.querySelector('.style-btn').click();
        
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
            const mode = document.getElementById('modeSelect').value;
            const roomType = document.getElementById('roomType').value;
            const aiIntervention = document.getElementById('aiIntervention').value;
            const requirements = document.getElementById('requirements').value;
            const apiKey = document.getElementById('apiKey').value;
            
            if (!imageData) {
                alert('Please upload a room photo');
                return;
            }
            
            btn.disabled = true;
            btn.textContent = 'Processing Your Room...';
            status.innerHTML = '<div class="text-blue-600">🎨 Transforming your space... This may take 15-30 seconds.</div>';
            results.innerHTML = '';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: imageData,
                        style: selectedStyle,
                        mode: mode,
                        roomType: roomType,
                        aiIntervention: aiIntervention,
                        requirements: requirements,
                        apiKey: apiKey
                    })
                });
                
                const data = await response.json();
                
                if (data.success && data.images && data.images.length > 0) {
                    status.innerHTML = '<div class="text-green-600">✅ Your room has been transformed!</div>';
                    
                    // Show before/after comparison
                    results.innerHTML = `
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div>
                                <h3 class="font-semibold mb-2">Original</h3>
                                <img src="${imageData}" class="w-full rounded shadow">
                            </div>
                            <div>
                                <h3 class="font-semibold mb-2">${mode === 'virtual_staging' ? 'Staged' : 'Redesigned'} (${selectedStyle})</h3>
                                <img src="${data.images[0]}" class="w-full rounded shadow">
                            </div>
                        </div>
                    `;
                } else {
                    status.innerHTML = '<div class="text-red-600">❌ ' + (data.error || 'Transformation failed') + '</div>';
                }
            } catch (error) {
                status.innerHTML = '<div class="text-red-600">❌ Error: ' + error.message + '</div>';
            } finally {
                btn.disabled = false;
                btn.textContent = 'Transform My Room';
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    image = data.get('image')
    style = data.get('style')
    mode = data.get('mode', 'virtual_staging')
    room_type = data.get('roomType', 'Living Room')
    ai_intervention = data.get('aiIntervention', 'Mid')
    requirements = data.get('requirements')
    api_key = data.get('apiKey') or REIMAGINEHOME_API_KEY
    
    if not image or not style:
        return jsonify({
            'success': False,
            'error': 'Please provide an image and style'
        })
    
    if not api_key:
        return jsonify({
            'success': False,
            'error': 'ReimagineHome API key not provided. Get your API key at reimaginehome.ai'
        })
    
    try:
        # Remove data URL prefix and decode base64
        if image.startswith('data:'):
            image_data = base64.b64decode(image.split(',')[1])
        else:
            image_data = base64.b64decode(image)
        
        print(f"Processing with ReimagineHome: {style} style, {mode} mode, {room_type}")
        
        if mode == 'virtual_staging':
            # Virtual Staging API - for empty rooms
            files = {
                'image': ('room.jpg', image_data, 'image/jpeg')
            }
            
            data = {
                'design_type': 'Interior',
                'design_style': style,
                'room_type': room_type,
                'ai_intervention': ai_intervention,
                'no_design': 1  # Generate 1 design
            }
            
            if requirements:
                data['custom_instruction'] = requirements
            
            headers = {
                'api-key': api_key
            }
            
            # Step 1: Submit request
            response = requests.post(
                'https://homedesigns.ai/api/v2/virtual_staging',
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code != 200:
                error_data = response.json()
                return jsonify({
                    'success': False,
                    'error': error_data.get('message', f'API error: {response.status_code}')
                })
            
            result = response.json()
            queue_id = result.get('id')
            
            if not queue_id:
                return jsonify({
                    'success': False,
                    'error': 'Failed to get queue ID from API'
                })
            
            print(f"Virtual staging job created: {queue_id}")
            
            # Step 2: Poll for results
            max_attempts = 40  # 40 * 1.5 = 60 seconds max
            for attempt in range(max_attempts):
                time.sleep(1.5)  # Wait 1.5 seconds between checks
                
                status_response = requests.get(
                    f'https://homedesigns.ai/api/v2/virtual_staging/status_check/{queue_id}',
                    headers=headers
                )
                
                if status_response.status_code != 200:
                    continue
                
                status_data = status_response.json()
                print(f"Status check {attempt + 1}: {status_data.get('status', 'Unknown')}")
                
                if status_data.get('status') == 'SUCCESS' and status_data.get('output_images'):
                    return jsonify({
                        'success': True,
                        'images': status_data['output_images']
                    })
                elif status_data.get('status') in ['FAILED', 'ERROR']:
                    return jsonify({
                        'success': False,
                        'error': 'Virtual staging failed'
                    })
            
            return jsonify({
                'success': False,
                'error': 'Virtual staging timed out. Please try again.'
            })
            
        else:  # redesign mode
            # Redesign API - for furnished rooms
            files = {
                'image': ('room.jpg', image_data, 'image/jpeg')
            }
            
            data = {
                'design_type': 'Interior',
                'design_style': style,
                'room_type': room_type,
                'no_design': 1  # Generate 1 design
            }
            
            if requirements:
                data['prompt'] = requirements
            
            headers = {
                'api-key': api_key
            }
            
            response = requests.post(
                'https://homedesigns.ai/api/v2/redesign',
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract images from response
                images = []
                if 'output_images' in result:
                    images = result['output_images']
                elif 'data' in result and 'output_images' in result['data']:
                    images = result['data']['output_images']
                
                if images:
                    return jsonify({
                        'success': True,
                        'images': images
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'No images returned from API'
                    })
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                return jsonify({
                    'success': False,
                    'error': error_data.get('message', f'API error: {response.status_code}')
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
    print("AI ROOM STAGER - REIMAGINEHOME VERSION")
    print("="*60)
    print("Professional virtual staging powered by ReimagineHome AI")
    print(f"\nReimagineHome API Key: {'[OK] Configured' if REIMAGINEHOME_API_KEY else '[X] Not configured'}")
    if not REIMAGINEHOME_API_KEY:
        print("\nTo use this version:")
        print("1. Sign up at https://www.reimaginehome.ai")
        print("2. Get your API key from the dashboard")
        print("3. Add to .env.local: REIMAGINEHOME_API_KEY=your-key-here")
    print("\nFeatures:")
    print("- Virtual Staging: Transform empty rooms into furnished spaces")
    print("- Redesign: Update existing furniture and decor")
    print("\nOpen http://localhost:5000 in your browser")
    print("="*60 + "\n")
    app.run(port=5000, debug=True)