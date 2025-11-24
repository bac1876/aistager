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
        <p class="text-center text-gray-600 mb-8">ReimagineHome API Test</p>
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
                <p class="text-sm">
                    <strong>Note:</strong> The ReimagineHome API implementation is still being finalized. 
                    Currently, we can create masks but the image generation requires additional parameters.
                    Contact info@reimaginehome.ai for complete API documentation.
                </p>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Test Image URL</label>
                <input type="text" id="imageUrl" class="w-full p-3 border rounded" 
                    value="https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800"
                    placeholder="Enter image URL">
            </div>
            
            <button id="testMaskBtn" class="w-full bg-blue-500 text-white py-3 rounded hover:bg-blue-600 font-semibold mb-3">
                Test Mask Creation
            </button>
            
            <button id="testGenerateBtn" class="w-full bg-green-500 text-white py-3 rounded hover:bg-green-600 font-semibold">
                Test Full Staging (Experimental)
            </button>
            
            <div id="status" class="mt-4 text-center"></div>
            <div id="results" class="mt-6"></div>
        </div>
    </div>
    
    <script>
        document.getElementById('testMaskBtn').addEventListener('click', async () => {
            const status = document.getElementById('status');
            const results = document.getElementById('results');
            const imageUrl = document.getElementById('imageUrl').value;
            
            status.innerHTML = '<div class="text-blue-600">Creating masks...</div>';
            results.innerHTML = '';
            
            try {
                const response = await fetch('/api/test-mask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image_url: imageUrl })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    status.innerHTML = '<div class="text-green-600">Mask creation successful!</div>';
                    results.innerHTML = '<pre class="bg-gray-100 p-4 rounded overflow-x-auto">' + 
                        JSON.stringify(data.masks, null, 2) + '</pre>';
                } else {
                    status.innerHTML = '<div class="text-red-600">Error: ' + data.error + '</div>';
                }
            } catch (error) {
                status.innerHTML = '<div class="text-red-600">Error: ' + error.message + '</div>';
            }
        });
        
        document.getElementById('testGenerateBtn').addEventListener('click', async () => {
            const status = document.getElementById('status');
            const results = document.getElementById('results');
            const imageUrl = document.getElementById('imageUrl').value;
            
            status.innerHTML = '<div class="text-blue-600">Testing full staging pipeline...</div>';
            results.innerHTML = '';
            
            try {
                const response = await fetch('/api/test-staging', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image_url: imageUrl })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    status.innerHTML = '<div class="text-green-600">Process completed!</div>';
                    results.innerHTML = '<pre class="bg-gray-100 p-4 rounded overflow-x-auto">' + 
                        JSON.stringify(data, null, 2) + '</pre>';
                } else {
                    status.innerHTML = '<div class="text-red-600">Error: ' + data.error + '</div>';
                    if (data.details) {
                        results.innerHTML = '<pre class="bg-gray-100 p-4 rounded overflow-x-auto">' + 
                            JSON.stringify(data.details, null, 2) + '</pre>';
                    }
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

@app.route('/api/test-mask', methods=['POST'])
def test_mask():
    data = request.json
    image_url = data.get('image_url')
    
    if not image_url:
        return jsonify({'success': False, 'error': 'Image URL required'})
    
    headers = {'api-key': REIMAGINEHOME_API_KEY}
    
    try:
        # Create mask
        response = requests.post(
            'https://api.reimaginehome.ai/v1/create_mask',
            headers=headers,
            json={'image_url': image_url}
        )
        
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'Mask creation failed: {response.text}'
            })
        
        result = response.json()
        job_id = result['data']['job_id']
        
        # Poll for results
        for _ in range(30):
            time.sleep(2)
            status_response = requests.get(
                f'https://api.reimaginehome.ai/v1/create_mask/{job_id}',
                headers=headers
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data.get('data', {}).get('job_status') == 'done':
                    return jsonify({
                        'success': True,
                        'masks': status_data['data']['masks']
                    })
        
        return jsonify({'success': False, 'error': 'Mask creation timed out'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-staging', methods=['POST'])
def test_staging():
    data = request.json
    image_url = data.get('image_url')
    
    if not image_url:
        return jsonify({'success': False, 'error': 'Image URL required'})
    
    headers = {'api-key': REIMAGINEHOME_API_KEY}
    
    try:
        # Step 1: Create masks
        mask_response = requests.post(
            'https://api.reimaginehome.ai/v1/create_mask',
            headers=headers,
            json={'image_url': image_url}
        )
        
        if mask_response.status_code != 200:
            return jsonify({
                'success': False,
                'error': 'Mask creation failed',
                'details': mask_response.json()
            })
        
        mask_job_id = mask_response.json()['data']['job_id']
        
        # Wait for masks
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
            return jsonify({'success': False, 'error': 'Mask creation timed out'})
        
        # Step 2: Try to generate image
        # Filter for furnishing masks
        furnishing_masks = [m['url'] for m in masks if 'furnishing' in m['category']]
        mask_urls = furnishing_masks if furnishing_masks else [masks[0]['url']]
        
        # This is where the API currently fails - we need the correct space_type value
        generation_payload = {
            'image_url': image_url,
            'mask_urls': mask_urls,
            'mask_category': 'furnishing',
            'generation_count': 1,
            'prompt': 'Modern furniture and decor'
        }
        
        gen_response = requests.post(
            'https://api.reimaginehome.ai/v1/generate_image',
            headers=headers,
            json=generation_payload
        )
        
        if gen_response.status_code != 200:
            return jsonify({
                'success': False,
                'error': 'Generation failed - API requires additional parameters',
                'details': {
                    'masks_created': len(masks),
                    'generation_error': gen_response.json(),
                    'note': 'Contact info@reimaginehome.ai for complete API documentation'
                }
            })
        
        # If it somehow works, return the result
        return jsonify({
            'success': True,
            'generation_result': gen_response.json()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("REIMAGINEHOME API TEST SERVER")
    print("="*60)
    print(f"API Key configured: {'Yes' if REIMAGINEHOME_API_KEY else 'No'}")
    print("\nNOTE: The ReimagineHome API is partially working.")
    print("- Mask creation: Working")
    print("- Image generation: Requires additional parameters")
    print("\nContact info@reimaginehome.ai for complete documentation")
    print("\nOpen http://localhost:5000 in your browser")
    print("="*60 + "\n")
    app.run(port=5000, debug=True)