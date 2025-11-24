import os
import time
import requests
import base64
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv
import openai

load_dotenv('.env.local')

app = Flask(__name__)
CORS(app)

# You'll need an OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

print(f"OpenAI API configured: {'Yes' if OPENAI_API_KEY else 'No'}")

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Room Stager - DALL-E 3</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Room Stager</h1>
        <p class="text-center text-gray-600 mb-8">Using DALL-E 3 (same as Microsoft Copilot)</p>
        
        <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
            <div class="bg-green-50 border-l-4 border-green-400 p-4 mb-6">
                <p class="text-sm">
                    <strong>Success!</strong> This uses the same AI as Microsoft Copilot. 
                    Just describe how you want the room staged.
                </p>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Describe your room and desired staging</label>
                <textarea id="promptInput" rows="4" class="w-full p-3 border rounded" 
                    placeholder="Example: A modern living room with white walls and hardwood floors. Stage it with contemporary furniture including a grey sectional sofa, glass coffee table, and minimalist decor.">Stage this room with modern furniture and decor while keeping the exact same room structure, windows, and walls</textarea>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Upload Room Photo (Optional for reference)</label>
                <input type="file" id="fileInput" accept="image/*" class="w-full p-2 border rounded">
                <img id="preview" class="mt-4 max-h-64 mx-auto hidden rounded shadow">
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2">Quick Staging Options</label>
                <div class="grid grid-cols-2 gap-2">
                    <button onclick="setPrompt('Stage this room with modern furniture including a sleek sofa, minimalist coffee table, and contemporary decor. Keep the exact room structure.')" 
                        class="p-2 bg-gray-100 rounded hover:bg-gray-200 text-sm">Modern Staging</button>
                    <button onclick="setPrompt('Stage this room with Scandinavian furniture including light wood pieces, cozy textiles, and plants. Keep the exact room structure.')" 
                        class="p-2 bg-gray-100 rounded hover:bg-gray-200 text-sm">Scandinavian</button>
                    <button onclick="setPrompt('Stage this room with traditional furniture including classic wooden pieces and elegant fabrics. Keep the exact room structure.')" 
                        class="p-2 bg-gray-100 rounded hover:bg-gray-200 text-sm">Traditional</button>
                    <button onclick="setPrompt('Stage this room as a home office with a desk, chair, and bookshelves. Keep the exact room structure.')" 
                        class="p-2 bg-gray-100 rounded hover:bg-gray-200 text-sm">Home Office</button>
                </div>
            </div>
            
            <button id="generateBtn" class="w-full bg-blue-500 text-white py-3 rounded hover:bg-blue-600 font-semibold">
                Stage My Room
            </button>
            
            <div id="apiKeyNotice" class="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded hidden">
                <p class="text-sm">
                    <strong>Note:</strong> You need an OpenAI API key. Add it to your .env.local file as OPENAI_API_KEY=sk-...
                    <br>Get one at <a href="https://platform.openai.com/api-keys" target="_blank" class="text-blue-600 underline">platform.openai.com</a>
                </p>
            </div>
            
            <div id="status" class="mt-4 text-center"></div>
            <div id="results" class="mt-6"></div>
        </div>
    </div>
    
    <script>
        let imageData = null;
        const hasApiKey = ''' + ('true' if OPENAI_API_KEY else 'false') + ''';
        
        if (!hasApiKey) {
            document.getElementById('apiKeyNotice').classList.remove('hidden');
        }
        
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
            const btn = document.getElementById('generateBtn');
            const status = document.getElementById('status');
            const results = document.getElementById('results');
            const prompt = document.getElementById('promptInput').value;
            
            if (!prompt) {
                alert('Please describe how you want the room staged');
                return;
            }
            
            btn.disabled = true;
            btn.textContent = 'Staging Your Room...';
            status.innerHTML = '<div class="text-blue-600">🎨 Creating your staged room... (20-30 seconds)</div>';
            results.innerHTML = '';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: prompt,
                        image: imageData
                    })
                });
                
                const data = await response.json();
                
                if (data.success && data.images && data.images.length > 0) {
                    status.innerHTML = '<div class="text-green-600">✅ Your room has been staged!</div>';
                    
                    results.innerHTML = '<div class="grid grid-cols-1 gap-4">';
                    data.images.forEach((img, idx) => {
                        results.innerHTML += `
                            <div>
                                <h3 class="font-semibold mb-2">Staged Room ${idx + 1}</h3>
                                <img src="${img.url}" class="w-full rounded shadow">
                                <p class="text-sm text-gray-600 mt-2">${img.revised_prompt || prompt}</p>
                            </div>
                        `;
                    });
                    results.innerHTML += '</div>';
                    
                    if (imageData) {
                        results.innerHTML = `
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                <div>
                                    <h3 class="font-semibold mb-2">Original</h3>
                                    <img src="${imageData}" class="w-full rounded shadow">
                                </div>
                                <div>
                                    <h3 class="font-semibold mb-2">Staged</h3>
                                    <img src="${data.images[0].url}" class="w-full rounded shadow">
                                </div>
                            </div>
                        ` + results.innerHTML;
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

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt')
    image_data = data.get('image')  # Optional reference image
    
    if not prompt:
        return jsonify({
            'success': False,
            'error': 'Please provide a prompt'
        })
    
    if not OPENAI_API_KEY:
        return jsonify({
            'success': False,
            'error': 'OpenAI API key not configured. Add OPENAI_API_KEY to your .env.local file'
        })
    
    try:
        # If image is provided, mention it in the prompt
        full_prompt = prompt
        if image_data:
            full_prompt = f"Based on the uploaded room photo: {prompt}"
        
        print(f"Generating with DALL-E 3: {full_prompt}")
        
        # Call DALL-E 3
        response = openai.Image.create(
            model="dall-e-3",
            prompt=full_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        images = []
        for img in response.data:
            images.append({
                'url': img.url,
                'revised_prompt': img.revised_prompt if hasattr(img, 'revised_prompt') else prompt
            })
        
        print("Successfully generated staged room")
        
        return jsonify({
            'success': True,
            'images': images
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI ROOM STAGER - DALL-E 3 VERSION")
    print("="*60)
    print("This uses the same AI as Microsoft Copilot")
    print(f"\nOpenAI API Key: {'[OK] Configured' if OPENAI_API_KEY else '[X] Not configured'}")
    if not OPENAI_API_KEY:
        print("\nTo use this version:")
        print("1. Get an OpenAI API key from https://platform.openai.com")
        print("2. Add to .env.local: OPENAI_API_KEY=sk-...")
    print("\nOpen http://localhost:5000 in your browser")
    print("="*60 + "\n")
    app.run(port=5000, debug=True)