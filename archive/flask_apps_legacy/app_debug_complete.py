import os
import time
import requests
import base64
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv
import json
from datetime import datetime
import uuid
import traceback

load_dotenv()

app = Flask(__name__)
CORS(app)

# Get API key from environment
REIMAGINEHOME_API_KEY = os.getenv('REIMAGINEHOME_API_KEY')

# Store staging results in memory
STAGING_JOBS = {}
COMPLETED_STAGINGS = {}
DEBUG_LOGS = []

print(f"ReimagineHome API configured: {'Yes' if REIMAGINEHOME_API_KEY else 'No'}")

def log_debug(message, data=None):
    """Log debug information"""
    entry = {
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'data': data
    }
    DEBUG_LOGS.append(entry)
    print(f"[DEBUG] {message}")
    if data:
        print(f"[DATA] {json.dumps(data, indent=2)}")

# HTML template with debug info
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Room Stager - Debug Mode</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Room Stager - Debug Mode</h1>
        <p class="text-center text-gray-600 mb-8">Detailed Error Tracking Enabled</p>
        
        <div class="max-w-4xl mx-auto">
            <!-- Debug Panel -->
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6 rounded">
                <p class="font-semibold mb-2">🔍 Debug Mode Active</p>
                <button id="testBtn" class="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600 mr-2">
                    Run System Test
                </button>
                <button id="clearBtn" class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">
                    Clear Logs
                </button>
            </div>
            
            <div class="bg-white rounded-lg shadow-lg p-6">
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
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-2">Design Style</label>
                        <select id="designTheme" class="w-full p-3 border rounded">
                            <option value="">AI Decides</option>
                            <option value="DT-INT-011">Modern</option>
                        </select>
                    </div>
                </div>
                
                <button id="stageBtn" class="w-full bg-blue-500 text-white py-3 rounded hover:bg-blue-600 font-semibold">
                    Stage My Room (Debug Mode)
                </button>
                
                <div id="status" class="mt-4"></div>
                
                <!-- Debug Output -->
                <div id="debugOutput" class="mt-6 hidden">
                    <h3 class="font-semibold mb-2">Debug Information:</h3>
                    <div id="debugContent" class="bg-gray-100 p-4 rounded text-xs font-mono overflow-x-auto max-h-96 overflow-y-auto"></div>
                </div>
                
                <div id="results" class="mt-6"></div>
            </div>
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
        
        document.getElementById('testBtn').addEventListener('click', async () => {
            const debugOutput = document.getElementById('debugOutput');
            const debugContent = document.getElementById('debugContent');
            
            debugOutput.classList.remove('hidden');
            debugContent.innerHTML = 'Running system test...';
            
            try {
                const response = await fetch('/api/system-test');
                const data = await response.json();
                debugContent.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
            } catch (error) {
                debugContent.innerHTML = `Error: ${error.message}`;
            }
        });
        
        document.getElementById('clearBtn').addEventListener('click', () => {
            document.getElementById('debugOutput').classList.add('hidden');
            document.getElementById('status').innerHTML = '';
            document.getElementById('results').innerHTML = '';
        });
        
        document.getElementById('stageBtn').addEventListener('click', async () => {
            const btn = document.getElementById('stageBtn');
            const status = document.getElementById('status');
            const debugOutput = document.getElementById('debugOutput');
            const debugContent = document.getElementById('debugContent');
            
            if (!imageData) {
                alert('Please upload a room photo first');
                return;
            }
            
            btn.disabled = true;
            btn.textContent = 'Processing (Debug Mode)...';
            status.innerHTML = '<div class="text-blue-600">Starting debug processing...</div>';
            
            debugOutput.classList.remove('hidden');
            debugContent.innerHTML = 'Processing...';
            
            try {
                const response = await fetch('/api/stage-debug', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: imageData,
                        space_type: document.getElementById('spaceType').value,
                        design_theme: document.getElementById('designTheme').value
                    })
                });
                
                const data = await response.json();
                
                // Show debug info
                debugContent.innerHTML = `<pre>${JSON.stringify(data.debug_info, null, 2)}</pre>`;
                
                if (data.success) {
                    status.innerHTML = `
                        <div class="bg-green-50 p-4 rounded">
                            <p class="text-green-800 font-semibold">✓ Debug: Staging submitted</p>
                            <p class="text-sm text-green-600">Job ID: ${data.job_id}</p>
                        </div>
                    `;
                } else {
                    status.innerHTML = `
                        <div class="bg-red-50 p-4 rounded">
                            <p class="text-red-800 font-semibold">✗ Error at step: ${data.failed_step}</p>
                            <p class="text-sm text-red-600 mt-1">${data.error}</p>
                            <details class="mt-2">
                                <summary class="cursor-pointer text-sm text-red-700">Click for details</summary>
                                <pre class="mt-2 text-xs overflow-x-auto">${JSON.stringify(data.error_details, null, 2)}</pre>
                            </details>
                        </div>
                    `;
                }
            } catch (error) {
                status.innerHTML = `
                    <div class="bg-red-50 p-4 rounded">
                        <p class="text-red-800">Frontend Error: ${error.message}</p>
                    </div>
                `;
                debugContent.innerHTML = `Frontend error: ${error.message}`;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Stage My Room (Debug Mode)';
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/system-test')
def system_test():
    """Test all components of the system"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }
    
    # Test 1: API Key
    results['tests']['api_key'] = {
        'present': bool(REIMAGINEHOME_API_KEY),
        'length': len(REIMAGINEHOME_API_KEY) if REIMAGINEHOME_API_KEY else 0
    }
    
    # Test 2: Test with known working image
    try:
        test_url = "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800"
        headers = {'api-key': REIMAGINEHOME_API_KEY}
        
        response = requests.post(
            'https://api.reimaginehome.ai/v1/create_mask',
            headers=headers,
            json={'image_url': test_url},
            timeout=10
        )
        
        results['tests']['api_connectivity'] = {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'response': response.json() if response.status_code != 200 else 'Success'
        }
    except Exception as e:
        results['tests']['api_connectivity'] = {
            'error': str(e),
            'success': False
        }
    
    # Test 3: File.io upload test
    try:
        test_data = b"test image data"
        upload_response = requests.post(
            'https://file.io',
            files={'file': ('test.txt', test_data, 'text/plain')},
            data={'expires': '1h'},
            timeout=10
        )
        
        results['tests']['file_io'] = {
            'status_code': upload_response.status_code,
            'success': upload_response.status_code == 200,
            'response': upload_response.json() if upload_response.status_code == 200 else upload_response.text
        }
        
        # Test if we can access the uploaded file
        if upload_response.status_code == 200:
            file_url = upload_response.json().get('link')
            if file_url:
                access_response = requests.get(file_url, timeout=5)
                results['tests']['file_io']['accessible'] = access_response.status_code == 200
    except Exception as e:
        results['tests']['file_io'] = {
            'error': str(e),
            'success': False
        }
    
    # Test 4: Server environment
    results['tests']['environment'] = {
        'is_render': 'RENDER' in os.environ,
        'port': os.environ.get('PORT', 'Not set'),
        'python_version': os.sys.version
    }
    
    return jsonify(results)

@app.route('/api/stage-debug', methods=['POST'])
def stage_debug():
    """Debug version of staging with detailed logging"""
    data = request.json
    image_data = data.get('image')
    space_type = data.get('space_type')
    design_theme = data.get('design_theme')
    
    debug_info = {
        'steps': [],
        'start_time': datetime.now().isoformat()
    }
    
    try:
        # Step 1: Validate input
        debug_info['steps'].append({
            'step': 'validate_input',
            'image_size': len(image_data) if image_data else 0,
            'space_type': space_type,
            'design_theme': design_theme
        })
        
        if not image_data or not space_type:
            return jsonify({
                'success': False,
                'error': 'Missing required fields',
                'failed_step': 'validate_input',
                'debug_info': debug_info
            })
        
        # Step 2: Extract and prepare image
        log_debug("Extracting base64 image")
        base64_data = image_data.split(',')[1] if ',' in image_data else image_data
        image_bytes = base64.b64decode(base64_data)
        
        debug_info['steps'].append({
            'step': 'prepare_image',
            'image_bytes_size': len(image_bytes),
            'success': True
        })
        
        # Step 3: Upload to file.io
        log_debug("Uploading to file.io")
        upload_start = time.time()
        
        upload_response = requests.post(
            'https://file.io',
            files={'file': ('room.jpg', image_bytes, 'image/jpeg')},
            data={'expires': '1h'},
            timeout=30
        )
        
        upload_time = time.time() - upload_start
        
        debug_info['steps'].append({
            'step': 'file_io_upload',
            'status_code': upload_response.status_code,
            'upload_time': f"{upload_time:.2f}s",
            'response': upload_response.json() if upload_response.status_code == 200 else upload_response.text[:500]
        })
        
        if upload_response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'File.io upload failed with status {upload_response.status_code}',
                'failed_step': 'file_io_upload',
                'error_details': upload_response.text,
                'debug_info': debug_info
            })
        
        upload_data = upload_response.json()
        if not upload_data.get('success'):
            return jsonify({
                'success': False,
                'error': 'File.io upload failed',
                'failed_step': 'file_io_upload',
                'error_details': upload_data,
                'debug_info': debug_info
            })
        
        image_url = upload_data['link']
        log_debug(f"Image uploaded to: {image_url}")
        
        # Step 4: Test if URL is accessible
        log_debug("Testing URL accessibility")
        try:
            access_test = requests.head(image_url, timeout=5)
            debug_info['steps'].append({
                'step': 'url_accessibility',
                'url': image_url,
                'status_code': access_test.status_code,
                'accessible': access_test.status_code == 200
            })
        except Exception as e:
            debug_info['steps'].append({
                'step': 'url_accessibility',
                'url': image_url,
                'error': str(e)
            })
        
        # Step 5: Create masks with ReimagineHome
        log_debug("Creating masks with ReimagineHome")
        headers = {'api-key': REIMAGINEHOME_API_KEY}
        
        mask_response = requests.post(
            'https://api.reimaginehome.ai/v1/create_mask',
            headers=headers,
            json={'image_url': image_url},
            timeout=30
        )
        
        debug_info['steps'].append({
            'step': 'create_mask',
            'status_code': mask_response.status_code,
            'response': mask_response.json() if mask_response.status_code == 200 else mask_response.text[:500]
        })
        
        if mask_response.status_code != 200:
            error_data = mask_response.json() if mask_response.headers.get('content-type') == 'application/json' else {'error': mask_response.text}
            return jsonify({
                'success': False,
                'error': error_data.get('error_message', f'Mask creation failed with status {mask_response.status_code}'),
                'failed_step': 'create_mask',
                'error_details': error_data,
                'debug_info': debug_info
            })
        
        mask_job_id = mask_response.json()['data']['job_id']
        log_debug(f"Mask job created: {mask_job_id}")
        
        # Step 6: Wait for masks
        log_debug("Waiting for masks to process")
        masks = None
        for i in range(15):
            time.sleep(2)
            status_response = requests.get(
                f'https://api.reimaginehome.ai/v1/create_mask/{mask_job_id}',
                headers=headers,
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                job_status = status_data.get('data', {}).get('job_status')
                
                if job_status == 'done':
                    masks = status_data['data']['masks']
                    break
                elif job_status == 'error':
                    debug_info['steps'].append({
                        'step': 'mask_processing',
                        'status': 'error',
                        'details': status_data
                    })
                    return jsonify({
                        'success': False,
                        'error': 'Mask processing failed',
                        'failed_step': 'mask_processing',
                        'error_details': status_data,
                        'debug_info': debug_info
                    })
        
        if not masks:
            return jsonify({
                'success': False,
                'error': 'Mask processing timeout',
                'failed_step': 'mask_processing',
                'debug_info': debug_info
            })
        
        debug_info['steps'].append({
            'step': 'mask_processing',
            'status': 'success',
            'masks_found': len(masks),
            'mask_categories': [m.get('category') for m in masks]
        })
        
        # If we got here, basic functionality works!
        return jsonify({
            'success': True,
            'message': 'Debug test passed - system is working',
            'job_id': 'debug_test_' + str(uuid.uuid4())[:8],
            'debug_info': debug_info
        })
        
    except Exception as e:
        log_debug(f"Exception occurred: {str(e)}")
        debug_info['steps'].append({
            'step': 'exception',
            'error': str(e),
            'traceback': traceback.format_exc()
        })
        
        return jsonify({
            'success': False,
            'error': str(e),
            'failed_step': 'exception',
            'debug_info': debug_info
        })

@app.route('/api/debug-logs')
def get_debug_logs():
    """Get recent debug logs"""
    return jsonify({
        'logs': DEBUG_LOGS[-50:],  # Last 50 entries
        'total': len(DEBUG_LOGS)
    })

# Health check
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'api_configured': bool(REIMAGINEHOME_API_KEY),
        'debug_mode': True
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)