import os
import time
import requests
import base64
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv
import io

load_dotenv('.env.local')

app = Flask(__name__)
CORS(app)

REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
print(f"Replicate API configured: {'Yes' if REPLICATE_API_TOKEN else 'No'}")

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Interior Designer - Room Transformer</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Interior Designer</h1>
        <p class="text-center text-gray-600 mb-8">Transform YOUR room - not generate a new one</p>
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
                <p class="text-sm">
                    <strong>Tip:</strong> For best results, upload a photo showing the full room with clear walls and structure. 
                    The AI will add furniture and change colors while keeping your exact room layout.
                </p>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Upload Your Room Photo</label>
                <input type="file" id="fileInput" accept="image/*" class="w-full">
                <img id="preview" class="mt-4 max-h-64 mx-auto hidden rounded shadow">
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Design Style</label>
                <select id="styleSelect" class="w-full p-2 border rounded">
                    <option value="modern">Modern - Clean lines, minimal</option>
                    <option value="scandinavian">Scandinavian - Cozy, light wood</option>
                    <option value="industrial">Industrial - Raw, urban</option>
                    <option value="minimalist">Minimalist - Less is more</option>
                    <option value="traditional">Traditional - Classic, warm</option>
                    <option value="bohemian">Bohemian - Eclectic, colorful</option>
                </select>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Transformation Strength</label>
                <select id="strengthSelect" class="w-full p-2 border rounded">
                    <option value="0.5">Light (50%) - Subtle changes</option>
                    <option value="0.65" selected>Medium (65%) - Balanced</option>
                    <option value="0.8">Strong (80%) - Major changes</option>
                </select>
            </div>
            
            <button id="generateBtn" class="w-full bg-blue-500 text-white py-3 rounded hover:bg-blue-600 font-semibold">
                Transform My Room
            </button>
            
            <div id="status" class="mt-4 text-center"></div>
            <div id="results" class="mt-6"></div>
        </div>
    </div>
    
    <script>
        let imageData = null;
        
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
            if (!imageData) {
                alert('Please upload a room photo');
                return;
            }
            
            const btn = document.getElementById('generateBtn');
            const status = document.getElementById('status');
            const results = document.getElementById('results');
            
            btn.disabled = true;
            btn.textContent = 'Transforming Your Room...';
            status.innerHTML = '<div class="text-blue-600">🏠 Analyzing your room structure and applying new design...</div>';
            results.innerHTML = '';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: imageData,
                        style: document.getElementById('styleSelect').value,
                        strength: parseFloat(document.getElementById('strengthSelect').value)
                    })
                });
                
                const data = await response.json();
                
                if (data.success && data.images && data.images.length > 0) {
                    status.innerHTML = '<div class="text-green-600">✅ Your room has been transformed!</div>';
                    
                    results.innerHTML = `
                        <div class="space-y-4">
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <h3 class="font-semibold mb-2 text-center">Your Original Room</h3>
                                    <img src="${imageData}" class="w-full rounded shadow">
                                </div>
                                <div>
                                    <h3 class="font-semibold mb-2 text-center">Transformed to ${document.getElementById('styleSelect').value}</h3>
                                    <img src="${data.images[0]}" class="w-full rounded shadow">
                                </div>
                            </div>
                            <div class="text-sm text-gray-600 text-center">
                                ${data.method === 'interior_model' ? '✅ Using specialized interior design AI' : '⚠️ Using fallback model'}
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
    image_data_uri = data.get('image')
    style = data.get('style', 'modern')
    strength = data.get('strength', 0.65)
    
    if not image_data_uri or not REPLICATE_API_TOKEN:
        return jsonify({
            'success': False,
            'error': 'Missing image or API key'
        })
    
    try:
        headers = {
            'Authorization': f'Token {REPLICATE_API_TOKEN}',
            'Content-Type': 'application/json',
        }
        
        print(f"\nTransforming room to {style} style (strength: {strength})...")
        
        # Try specialized interior design model first
        try:
            # Using a model specifically for room redesign
            payload = {
                "version": "17e07f89d07e6b8a44065b06e97af1b999c4e6a1e1ad3c29ebd4b05b1ad03e44",  # room interior designer
                "input": {
                    "image": image_data_uri,
                    "prompt": f"Transform this exact room into {style} interior design style. Keep the same walls, windows, and room structure. Only change furniture, decor, and colors to match {style} design aesthetic.",
                    "strength": strength,
                    "guidance_scale": 7.5,
                    "num_inference_steps": 30,
                    "scheduler": "K_EULER"
                }
            }
            
            response = requests.post(
                'https://api.replicate.com/v1/predictions',
                headers=headers,
                json=payload
            )
            
            if response.status_code == 201:
                method = "interior_model"
            else:
                raise Exception("Interior model not available")
                
        except:
            # Fallback to InstructPix2Pix - better for editing existing images
            print("Using InstructPix2Pix for image editing...")
            
            edit_instructions = {
                'modern': 'Transform this room to modern interior design: add sleek furniture, use neutral colors, clean lines, minimal decor',
                'scandinavian': 'Transform this room to Scandinavian design: add light wood furniture, white walls, cozy textiles, plants',
                'industrial': 'Transform this room to industrial design: add metal furniture, exposed elements, dark colors, raw materials',
                'minimalist': 'Transform this room to minimalist design: remove clutter, use minimal furniture, white space, simple forms',
                'traditional': 'Transform this room to traditional design: add classic wooden furniture, warm colors, elegant fabrics',
                'bohemian': 'Transform this room to bohemian design: add eclectic furniture, colorful textiles, plants, artistic elements'
            }
            
            payload = {
                "version": "30c1d0b916a6f8efce20493f5d61ee27491ab2a60437c13c588468b9810ec23f",  # InstructPix2Pix
                "input": {
                    "image": image_data_uri,
                    "prompt": edit_instructions.get(style, edit_instructions['modern']),
                    "num_outputs": 1,
                    "guidance_scale": 10,
                    "image_guidance_scale": 1.5,
                    "num_inference_steps": 30
                }
            }
            
            response = requests.post(
                'https://api.replicate.com/v1/predictions',
                headers=headers,
                json=payload
            )
            
            method = "instruct_pix2pix"
            
            if response.status_code != 201:
                # Final fallback - SDXL with very specific instructions
                print("Using SDXL img2img as final fallback...")
                
                payload = {
                    "version": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                    "input": {
                        "image": image_data_uri,
                        "prompt": f"The exact same room transformed to {style} interior design, same walls and windows, only furniture and decor changed, professional interior design photo",
                        "negative_prompt": "different room, changed structure, moved walls, different windows",
                        "strength": strength,
                        "guidance_scale": 12,
                        "num_inference_steps": 30
                    }
                }
                
                response = requests.post(
                    'https://api.replicate.com/v1/predictions',
                    headers=headers,
                    json=payload
                )
                
                method = "sdxl_fallback"
                
                if response.status_code != 201:
                    raise Exception(f"All models failed: {response.status_code}")
        
        prediction = response.json()
        prediction_id = prediction['id']
        print(f"Prediction ID: {prediction_id} (method: {method})")
        
        # Poll for results
        for attempt in range(60):
            time.sleep(1)
            
            result_response = requests.get(
                f'https://api.replicate.com/v1/predictions/{prediction_id}',
                headers=headers
            )
            
            if result_response.status_code == 200:
                result = result_response.json()
                
                if result['status'] == 'succeeded':
                    output = result.get('output')
                    if output:
                        if isinstance(output, list):
                            images = output
                        else:
                            images = [output]
                        
                        print(f"Success! Room transformed using {method}")
                        return jsonify({
                            'success': True,
                            'images': images,
                            'method': method
                        })
                elif result['status'] == 'failed':
                    raise Exception(result.get('error', 'Generation failed'))
                else:
                    print(f"Status: {result['status']} ({attempt+1}/60)")
        
        raise Exception('Timeout')
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI INTERIOR DESIGNER - ROOM TRANSFORMER")
    print("="*60)
    print("This version uses multiple approaches to transform YOUR room")
    print("while preserving its structure.")
    print(f"\nAPI Key: {'[OK] Configured' if REPLICATE_API_TOKEN else '[X] Not configured'}")
    print("\nStrategies:")
    print("1. Specialized interior design model")
    print("2. InstructPix2Pix for image editing")
    print("3. SDXL with strict instructions")
    print("\nOpen http://localhost:5000 in your browser")
    print("="*60 + "\n")
    app.run(port=5000, debug=True)