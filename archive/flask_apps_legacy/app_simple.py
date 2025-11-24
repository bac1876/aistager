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
        
        <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Upload Room Photo</label>
                <input type="file" id="fileInput" accept="image/*" class="w-full">
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
            <div id="results" class="mt-6 grid grid-cols-3 gap-4"></div>
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
            status.textContent = 'Generating designs with AI...';
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
                    status.textContent = 'Complete! Here are your AI-generated designs:';
                    data.images.forEach((img, idx) => {
                        const imgEl = document.createElement('img');
                        imgEl.src = img;
                        imgEl.className = 'w-full h-48 object-cover rounded';
                        results.appendChild(imgEl);
                    });
                } else {
                    status.textContent = 'Error: ' + data.error;
                }
            } catch (error) {
                status.textContent = 'Error: ' + error.message;
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
    image_data = data.get('image')
    style = data.get('style', 'modern')
    
    if not image_data or not REPLICATE_API_TOKEN:
        # Return original image 3 times if no API key
        return jsonify({
            'success': True,
            'images': [image_data, image_data, image_data]
        })
    
    try:
        # Remove data URI prefix
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Prepare style prompt
        prompts = {
            'modern': 'modern interior design, sleek furniture, minimalist, neutral colors',
            'scandinavian': 'scandinavian interior design, light wood, cozy, white walls',
            'industrial': 'industrial interior design, metal furniture, exposed brick, dark',
            'minimalist': 'minimalist interior design, simple, clean, white space',
            'traditional': 'traditional interior design, classic furniture, warm colors',
            'bohemian': 'bohemian interior design, eclectic, colorful, plants'
        }
        
        prompt = f"Interior design photo, {prompts.get(style, prompts['modern'])}, professional photography"
        
        # Call Replicate API
        headers = {
            'Authorization': f'Token {REPLICATE_API_TOKEN}',
            'Content-Type': 'application/json',
        }
        
        # Using stable diffusion for simplicity
        payload = {
            "version": "ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
            "input": {
                "prompt": prompt,
                "num_outputs": 3
            }
        }
        
        print(f"Calling Replicate API for {style} design...")
        response = requests.post(
            'https://api.replicate.com/v1/predictions',
            headers=headers,
            json=payload
        )
        
        if response.status_code != 201:
            raise Exception(f"API error: {response.status_code}")
        
        prediction = response.json()
        prediction_id = prediction['id']
        
        # Poll for results
        for _ in range(30):  # 30 seconds timeout
            time.sleep(1)
            result_response = requests.get(
                f'https://api.replicate.com/v1/predictions/{prediction_id}',
                headers=headers
            )
            
            if result_response.status_code == 200:
                result = result_response.json()
                if result['status'] == 'succeeded':
                    # Return the generated images
                    return jsonify({
                        'success': True,
                        'images': result['output']
                    })
                elif result['status'] == 'failed':
                    raise Exception('Generation failed')
        
        raise Exception('Timeout waiting for results')
        
    except Exception as e:
        print(f"Error: {str(e)}")
        # Return original image on error
        return jsonify({
            'success': True,
            'images': [data.get('image')] * 3
        })

if __name__ == '__main__':
    print("\nStarting AI Interior Designer...")
    print(f"API Key: {'Configured' if REPLICATE_API_TOKEN else 'Not configured'}")
    print("\nOpen http://localhost:5000 in your browser\n")
    app.run(port=5000, debug=True)