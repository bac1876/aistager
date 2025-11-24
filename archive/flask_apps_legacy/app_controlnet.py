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
    <title>AI Interior Designer - ControlNet</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Interior Designer</h1>
        <p class="text-center text-gray-600 mb-8">Using ControlNet to preserve your room structure</p>
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Upload Room Photo</label>
                <input type="file" id="fileInput" accept="image/*" class="w-full">
                <img id="preview" class="mt-4 max-h-64 mx-auto hidden rounded">
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
            
            <button id="generateBtn" class="w-full bg-blue-500 text-white py-3 rounded hover:bg-blue-600 font-semibold">
                Transform Room with AI
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
                alert('Please upload an image');
                return;
            }
            
            const btn = document.getElementById('generateBtn');
            const status = document.getElementById('status');
            const results = document.getElementById('results');
            
            btn.disabled = true;
            btn.textContent = 'Generating...';
            status.innerHTML = '<div class="text-blue-600">🎨 Transforming your room with AI... This takes 30-60 seconds...</div>';
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
                
                if (data.success && data.images && data.images.length > 0) {
                    status.innerHTML = '<div class="text-green-600">✅ Complete! Your room has been transformed:</div>';
                    
                    // Show original vs transformed
                    results.innerHTML = `
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <h3 class="font-semibold mb-2">Original Room</h3>
                                <img src="${imageData}" class="w-full rounded shadow">
                            </div>
                            <div>
                                <h3 class="font-semibold mb-2">AI Transformed (${document.getElementById('styleSelect').value} style)</h3>
                                <img src="${data.images[0]}" class="w-full rounded shadow">
                            </div>
                        </div>
                    `;
                    
                    // Show additional variations if any
                    if (data.images.length > 1) {
                        results.innerHTML += '<h3 class="font-semibold mt-6 mb-2">Additional Variations</h3>';
                        results.innerHTML += '<div class="grid grid-cols-2 md:grid-cols-3 gap-4">';
                        for (let i = 1; i < data.images.length; i++) {
                            results.innerHTML += `<img src="${data.images[i]}" class="w-full rounded shadow">`;
                        }
                        results.innerHTML += '</div>';
                    }
                } else {
                    status.innerHTML = '<div class="text-red-600">❌ Error: ' + (data.error || 'Unknown error') + '</div>';
                }
            } catch (error) {
                status.innerHTML = '<div class="text-red-600">❌ Error: ' + error.message + '</div>';
            } finally {
                btn.disabled = false;
                btn.textContent = 'Transform Room with AI';
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
        return jsonify({
            'success': False,
            'error': 'Missing image or API key'
        })
    
    try:
        # Style-specific prompts
        style_prompts = {
            'modern': 'modern interior design, sleek furniture, minimalist decor, neutral colors, clean lines',
            'scandinavian': 'scandinavian interior design, light wood furniture, cozy textiles, white walls, hygge',
            'industrial': 'industrial interior design, metal furniture, exposed brick, concrete, edison bulbs',
            'minimalist': 'minimalist interior design, essential furniture only, white space, clean, simple',
            'traditional': 'traditional interior design, classic furniture, warm colors, elegant, timeless',
            'bohemian': 'bohemian interior design, eclectic furniture, colorful textiles, plants, artistic'
        }
        
        prompt = f"interior design photo, {style_prompts.get(style, style_prompts['modern'])}, professional photography, high quality"
        
        headers = {
            'Authorization': f'Token {REPLICATE_API_TOKEN}',
            'Content-Type': 'application/json',
        }
        
        print(f"\nGenerating {style} interior design transformation...")
        print("Using ControlNet to preserve room structure...")
        
        # Using ControlNet Canny model - preserves edges/structure
        payload = {
            "version": "854e8727697a057c525cdb45ab037f64ecca770a1769cc52287c2e56472a247b",  # jagilley/controlnet-canny
            "input": {
                "image": image_data_uri,
                "prompt": prompt,
                "negative_prompt": "ugly, distorted, deformed, low quality, bad architecture",
                "structure": "canny",  # Use canny edge detection to preserve structure
                "num_samples": "1",
                "image_resolution": "512",
                "steps": 20,
                "scale": 9,
                "seed": 42,
                "eta": 0,
                "a_prompt": "best quality, extremely detailed, interior design photography",
                "detect_resolution": "512",
                "low_threshold": 100,
                "high_threshold": 200
            }
        }
        
        response = requests.post(
            'https://api.replicate.com/v1/predictions',
            headers=headers,
            json=payload
        )
        
        if response.status_code != 201:
            print(f"API error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            # Try alternative model if first one fails
            print("Trying alternative ControlNet model...")
            
            # Alternative: lllyasviel/control_v11p_sd15_mlsd
            payload = {
                "version": "8e07480062ba59b0e350256cae02171f58b90daf99ae3b93204f0a208e3f98f6",
                "input": {
                    "image": image_data_uri,
                    "prompt": prompt,
                    "n_prompt": "ugly, distorted, deformed",
                    "num_samples": 1,
                    "image_resolution": "512",
                    "ddim_steps": 20,
                    "scale": 9,
                    "seed": 42,
                    "eta": 0,
                    "a_prompt": "best quality, extremely detailed",
                }
            }
            
            response = requests.post(
                'https://api.replicate.com/v1/predictions',
                headers=headers,
                json=payload
            )
            
            if response.status_code != 201:
                raise Exception(f"API error: {response.status_code}")
        
        prediction = response.json()
        prediction_id = prediction['id']
        print(f"Prediction ID: {prediction_id}")
        
        # Poll for results
        for attempt in range(60):
            time.sleep(1)
            
            result_response = requests.get(
                f'https://api.replicate.com/v1/predictions/{prediction_id}',
                headers=headers
            )
            
            if result_response.status_code == 200:
                result = result_response.json()
                print(f"Status: {result['status']} ({attempt+1}/60)")
                
                if result['status'] == 'succeeded':
                    output = result.get('output')
                    if output:
                        # Handle different output formats
                        if isinstance(output, list):
                            images = output
                        else:
                            images = [output]
                        
                        print(f"Success! Generated {len(images)} image(s)")
                        return jsonify({
                            'success': True,
                            'images': images
                        })
                elif result['status'] == 'failed':
                    error_msg = result.get('error', 'Unknown error')
                    print(f"Generation failed: {error_msg}")
                    raise Exception(error_msg)
        
        raise Exception('Timeout waiting for results')
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI INTERIOR DESIGNER - CONTROLNET VERSION")
    print("="*60)
    print("This version uses ControlNet to preserve your room's structure")
    print("while transforming the interior design style.")
    print(f"\nAPI Key: {'[OK] Configured' if REPLICATE_API_TOKEN else '[X] Not configured'}")
    print("\nOpen http://localhost:5000 in your browser")
    print("="*60 + "\n")
    app.run(port=5000, debug=True)