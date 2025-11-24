import os
import time
import requests
import base64
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv

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
    <title>AI Room Redesigner - Specialized Model</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Room Redesigner</h1>
        <p class="text-center text-gray-600 mb-8">Using specialized room transformation model</p>
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
                <p class="text-sm">
                    <strong>How it works:</strong> This uses a model specifically trained for room redesign. 
                    Upload your room photo and describe what changes you want to see.
                </p>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Upload Your Room Photo</label>
                <input type="file" id="fileInput" accept="image/*" class="w-full p-2 border rounded">
                <img id="preview" class="mt-4 max-h-64 mx-auto hidden rounded shadow">
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">What changes do you want?</label>
                <textarea id="promptInput" rows="3" class="w-full p-2 border rounded" 
                    placeholder="Example: Transform to modern style with white walls, add a grey sofa, wooden coffee table, and minimalist decor">Transform to modern interior design style with contemporary furniture</textarea>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Quick Style Options</label>
                <div class="grid grid-cols-2 gap-2">
                    <button onclick="setPrompt('Transform to modern style with sleek furniture and neutral colors')" 
                        class="p-2 bg-gray-100 rounded hover:bg-gray-200 text-sm">Modern</button>
                    <button onclick="setPrompt('Transform to Scandinavian style with light wood furniture and cozy textiles')" 
                        class="p-2 bg-gray-100 rounded hover:bg-gray-200 text-sm">Scandinavian</button>
                    <button onclick="setPrompt('Transform to industrial style with metal furniture and exposed elements')" 
                        class="p-2 bg-gray-100 rounded hover:bg-gray-200 text-sm">Industrial</button>
                    <button onclick="setPrompt('Transform to minimalist style with essential furniture only')" 
                        class="p-2 bg-gray-100 rounded hover:bg-gray-200 text-sm">Minimalist</button>
                </div>
            </div>
            
            <button id="generateBtn" class="w-full bg-blue-500 text-white py-3 rounded hover:bg-blue-600 font-semibold">
                Redesign My Room
            </button>
            
            <div id="status" class="mt-4 text-center"></div>
            <div id="results" class="mt-6"></div>
        </div>
    </div>
    
    <script>
        let imageData = null;
        
        function setPrompt(text) {
            document.getElementById('promptInput').value = text;
        }
        
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
            const prompt = document.getElementById('promptInput').value;
            
            btn.disabled = true;
            btn.textContent = 'Redesigning Your Room...';
            status.innerHTML = '<div class="text-blue-600">🎨 AI is redesigning your room... (30-45 seconds)</div>';
            results.innerHTML = '';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: imageData,
                        prompt: prompt
                    })
                });
                
                const data = await response.json();
                
                if (data.success && data.image) {
                    status.innerHTML = '<div class="text-green-600">✅ Your room has been redesigned!</div>';
                    
                    results.innerHTML = `
                        <div class="space-y-4">
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <h3 class="font-semibold mb-2 text-center">Original Room</h3>
                                    <img src="${imageData}" class="w-full rounded shadow">
                                </div>
                                <div>
                                    <h3 class="font-semibold mb-2 text-center">Redesigned Room</h3>
                                    <img src="${data.image}" class="w-full rounded shadow">
                                </div>
                            </div>
                            <div class="mt-4 p-4 bg-gray-50 rounded">
                                <p class="text-sm text-gray-600"><strong>Your request:</strong> ${prompt}</p>
                                <p class="text-sm text-gray-500 mt-1">Model: ${data.model || 'Room transformation model'}</p>
                            </div>
                        </div>
                    `;
                } else {
                    status.innerHTML = '<div class="text-red-600">❌ ' + (data.error || 'Redesign failed') + '</div>';
                    if (data.details) {
                        status.innerHTML += '<div class="text-sm text-gray-600 mt-2">' + data.details + '</div>';
                    }
                }
            } catch (error) {
                status.innerHTML = '<div class="text-red-600">❌ Error: ' + error.message + '</div>';
            } finally {
                btn.disabled = false;
                btn.textContent = 'Redesign My Room';
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
    prompt = data.get('prompt', 'Transform to modern interior design style')
    
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
        
        print(f"\nRedesigning room with prompt: {prompt}")
        
        # Try multiple room-specific models
        models_to_try = [
            {
                "name": "room-redesign",
                "version": "76604baddc85b1b4616e1c6475eca080da339c8875bd4996705440484a6cac81",
                "input": {
                    "image": image_data_uri,
                    "prompt": prompt,
                    "guidance_scale": 7,
                    "num_inference_steps": 50
                }
            },
            {
                "name": "interior-design",
                "version": "376b74fbbf024bb0f96af4b346d4e863e23701cd3c14035c86f0ff884fda9e42",
                "input": {
                    "image": image_data_uri,
                    "prompt": prompt,
                    "negative_prompt": "ugly, distorted",
                    "num_inference_steps": 30
                }
            },
            {
                "name": "sdxl-controlnet",
                "version": "435061a1b5a4c1e26740464bf786efdfa9cb3a3ac488595a2de23e143fdb0117",
                "input": {
                    "image": image_data_uri,
                    "prompt": f"Interior design photo, {prompt}, preserve room structure",
                    "strength": 0.7,
                    "guidance_scale": 10,
                    "num_outputs": 1
                }
            }
        ]
        
        for model in models_to_try:
            try:
                print(f"Trying model: {model['name']}")
                
                payload = {
                    "version": model["version"],
                    "input": model["input"]
                }
                
                response = requests.post(
                    'https://api.replicate.com/v1/predictions',
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 201:
                    prediction = response.json()
                    prediction_id = prediction['id']
                    print(f"Prediction started: {prediction_id}")
                    
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
                                    # Handle different output formats
                                    if isinstance(output, list) and len(output) > 0:
                                        image_url = output[0]
                                    elif isinstance(output, str):
                                        image_url = output
                                    else:
                                        continue
                                    
                                    print(f"Success with model: {model['name']}")
                                    return jsonify({
                                        'success': True,
                                        'image': image_url,
                                        'model': model['name']
                                    })
                            elif result['status'] == 'failed':
                                print(f"Model {model['name']} failed: {result.get('error', 'Unknown error')}")
                                break
                            else:
                                if attempt % 10 == 0:
                                    print(f"Status: {result['status']} ({attempt}/60)")
                else:
                    print(f"Model {model['name']} returned status {response.status_code}")
                    
            except Exception as e:
                print(f"Error with model {model['name']}: {str(e)}")
                continue
        
        # If all models failed
        raise Exception("All models failed to generate. The models might be unavailable or the prompt might be too complex.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'details': 'Try a simpler prompt or check if the models are available on Replicate.'
        })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI ROOM REDESIGNER - SPECIALIZED MODELS")
    print("="*60)
    print("This version tries multiple room-specific models")
    print(f"\nAPI Key: {'[OK] Configured' if REPLICATE_API_TOKEN else '[X] Not configured'}")
    print("\nModels being tried:")
    print("1. Room redesign model")
    print("2. Interior design model")
    print("3. SDXL with ControlNet")
    print("\nOpen http://localhost:5000 in your browser")
    print("="*60 + "\n")
    app.run(port=5000, debug=True)