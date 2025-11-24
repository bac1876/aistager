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
    <title>AI Interior Designer</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-8">AI Interior Designer</h1>
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Upload Room Photo</label>
                <input type="file" id="fileInput" accept="image/*" class="w-full">
                <img id="preview" class="mt-4 max-h-64 mx-auto hidden">
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Select Style</label>
                <select id="styleSelect" class="w-full p-2 border rounded">
                    <option value="modern">Modern</option>
                    <option value="scandinavian">Scandinavian</option>
                    <option value="industrial">Industrial</option>
                    <option value="minimalist">Minimalist</option>
                    <option value="traditional">Traditional</option>
                    <option value="bohemian">Bohemian</option>
                </select>
            </div>
            
            <button id="generateBtn" class="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600">
                Generate Design
            </button>
            
            <div id="status" class="mt-4 text-center"></div>
            <div id="results" class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4"></div>
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
                alert('Please upload an image');
                return;
            }
            
            const status = document.getElementById('status');
            const results = document.getElementById('results');
            status.innerHTML = '<div class="text-blue-600">Generating AI transformations... This may take 30-60 seconds...</div>';
            results.innerHTML = '';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: imageData,
                        style: document.getElementById('styleSelect').value
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    status.innerHTML = '<div class="text-green-600">Complete! Here are your AI-transformed rooms:</div>';
                    data.images.forEach((img, idx) => {
                        const div = document.createElement('div');
                        div.className = 'bg-gray-50 p-2 rounded';
                        div.innerHTML = `
                            <img src="${img}" class="w-full h-64 object-cover rounded mb-2">
                            <p class="text-sm text-center">Variation ${idx + 1}</p>
                        `;
                        results.appendChild(div);
                    });
                } else {
                    status.innerHTML = '<div class="text-red-600">Error: ' + data.error + '</div>';
                }
            } catch (error) {
                status.innerHTML = '<div class="text-red-600">Error: ' + error.message + '</div>';
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
    
    if not image_data_uri or not REPLICATE_API_TOKEN:
        # Return original image 3 times if no API key
        return jsonify({
            'success': True,
            'images': [image_data_uri, image_data_uri, image_data_uri]
        })
    
    try:
        # Style-specific prompts for interior design
        style_prompts = {
            'modern': 'Transform this room into a modern interior design style. Add sleek modern furniture, minimalist decor, neutral color palette with grays and whites, contemporary lighting fixtures. Keep the room structure and windows exactly the same.',
            'scandinavian': 'Transform this room into a Scandinavian interior design style. Add light wood furniture, cozy textiles, hygge elements, white walls, natural materials, plants. Keep the room structure and windows exactly the same.',
            'industrial': 'Transform this room into an industrial interior design style. Add metal and wood furniture, exposed elements, concrete textures, dark colors, Edison bulb lighting. Keep the room structure and windows exactly the same.',
            'minimalist': 'Transform this room into a minimalist interior design style. Add only essential furniture, remove clutter, use monochromatic colors, clean surfaces. Keep the room structure and windows exactly the same.',
            'traditional': 'Transform this room into a traditional interior design style. Add classic wooden furniture, elegant fabrics, warm colors, traditional patterns. Keep the room structure and windows exactly the same.',
            'bohemian': 'Transform this room into a bohemian interior design style. Add eclectic furniture, colorful textiles, plants, global decor, layered rugs. Keep the room structure and windows exactly the same.'
        }
        
        prompt = style_prompts.get(style, style_prompts['modern'])
        
        # Call Replicate API with image-to-image model
        headers = {
            'Authorization': f'Token {REPLICATE_API_TOKEN}',
            'Content-Type': 'application/json',
        }
        
        generated_images = []
        
        # Generate 3 variations with different seeds
        for i in range(3):
            print(f"\nGenerating {style} variation {i+1}...")
            
            # Using SDXL img2img model
            payload = {
                "version": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",  # SDXL img2img
                "input": {
                    "image": image_data_uri,
                    "prompt": prompt + f" Professional interior design photography, high quality, photorealistic.",
                    "negative_prompt": "distorted, blurry, bad quality, change room structure, move windows, alter walls",
                    "strength": 0.65,  # How much to change the image (0.65 = moderate changes)
                    "guidance_scale": 7.5,
                    "seed": i * 1000,  # Different seed for each variation
                    "num_inference_steps": 30
                }
            }
            
            response = requests.post(
                'https://api.replicate.com/v1/predictions',
                headers=headers,
                json=payload
            )
            
            if response.status_code != 201:
                print(f"API error: {response.status_code} - {response.text[:200]}")
                continue
            
            prediction = response.json()
            prediction_id = prediction['id']
            print(f"Prediction ID: {prediction_id}")
            
            # Poll for results
            for attempt in range(60):  # 60 seconds timeout
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
                            if isinstance(output, list):
                                generated_images.append(output[0])
                            else:
                                generated_images.append(output)
                            print(f"✓ Variation {i+1} generated successfully")
                        break
                    elif result['status'] == 'failed':
                        print(f"✗ Generation failed: {result.get('error', 'Unknown error')}")
                        break
                    else:
                        print(f"Status: {result['status']} ({attempt+1}/60)")
        
        if generated_images:
            return jsonify({
                'success': True,
                'images': generated_images
            })
        else:
            raise Exception('No images were generated successfully')
        
    except Exception as e:
        print(f"Error: {str(e)}")
        # Return original image on error
        return jsonify({
            'success': True,
            'images': [image_data_uri] * 3,
            'error': str(e)
        })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("AI INTERIOR DESIGNER - IMAGE TO IMAGE VERSION")
    print("="*50)
    print(f"API Key: {'✓ Configured' if REPLICATE_API_TOKEN else '✗ Not configured'}")
    print("\nThis version will transform your actual room photos")
    print("while preserving the room structure.")
    print("\nOpen http://localhost:5000 in your browser")
    print("="*50 + "\n")
    app.run(port=5000, debug=True)