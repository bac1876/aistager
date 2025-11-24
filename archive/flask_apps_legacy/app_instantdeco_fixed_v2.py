from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
import base64
from datetime import datetime
import json
import uuid

load_dotenv('.env.local')

app = Flask(__name__)
CORS(app)

# API Keys
INSTANTDECO_API_KEY = os.getenv('INSTANTDECO_API_KEY')
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')

# API URLs
INSTANTDECO_API_URL = 'https://app.instantdeco.ai/api/1.1/wf/request_v2'
IMGBB_API_URL = 'https://api.imgbb.com/1/upload'

# Staging history storage (in production, use a database)
staging_history = []

# Auto-detect ngrok URL
def get_webhook_url():
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        tunnels = response.json()
        if tunnels.get('tunnels'):
            public_url = tunnels['tunnels'][0]['public_url']
            return f"{public_url}/api/webhook"
    except:
        pass
    return None

# Display webhook status on startup
webhook_url = get_webhook_url()
print("\n" + "="*60)
print("AI ROOM STAGER - FIXED VERSION 2.0")
print("="*60)
if webhook_url:
    print(f"[OK] Ngrok detected: {webhook_url.replace('/api/webhook', '')}")
    print(f"[OK] Webhook URL: {webhook_url}")
else:
    print("[WARNING] Ngrok not detected - webhooks will not work")
print("="*60 + "\n")

print(f"InstantDecoAI API configured: {'Yes' if INSTANTDECO_API_KEY else 'No'}")
print(f"ImgBB API configured: {'Yes' if IMGBB_API_KEY else 'No'}")

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>AI Room Stager - Professional</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold text-center mb-2">AI Room Stager</h1>
        <p class="text-center text-gray-600 mb-2">Powered by InstantDecoAI</p>
        <p class="text-center text-sm text-gray-500 mb-8">Professional Version - No Pets, Better Control</p>
        
        <div class="max-w-6xl mx-auto">
            <!-- Webhook Status -->
            <div id="webhookStatus" class="mb-6 p-4 rounded bg-gray-50">
                <p class="text-sm">Checking webhook status...</p>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Left Column: Upload and Stage -->
                <div>
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <div class="flex justify-between items-center mb-4">
                            <h2 class="text-xl font-semibold">Stage a Room</h2>
                            <button onclick="clearForm()" class="text-sm px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded">
                                Clear Form
                            </button>
                        </div>
                        
                        <!-- Upload Section -->
                        <div class="mb-6">
                            <label class="block text-sm font-medium mb-2">Upload Photo</label>
                            <input type="file" id="fileInput" accept="image/*" class="hidden">
                            <label for="fileInput" class="cursor-pointer bg-blue-50 border-2 border-dashed border-blue-300 rounded-lg p-6 block text-center hover:bg-blue-100 transition-colors">
                                <svg class="w-10 h-10 mx-auto mb-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                                </svg>
                                <p class="text-gray-700">Click to upload a photo</p>
                                <p class="text-xs text-gray-500 mt-1">Interior or Exterior</p>
                            </label>
                        </div>
                        
                        <!-- Current Image Preview -->
                        <div id="currentImagePreview" class="hidden mb-6">
                            <p class="text-sm font-medium mb-2">Selected Image:</p>
                            <img id="previewImage" class="w-full h-48 object-cover rounded">
                        </div>
                        
                        <!-- Space Type (Interior/Exterior) -->
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Space Type</label>
                            <select id="spaceType" class="w-full p-3 border rounded" onchange="handleSpaceTypeChange()">
                                <option value="interior">Interior Room</option>
                                <option value="exterior">Exterior/Outdoor</option>
                            </select>
                        </div>
                        
                        <!-- Transformation Type -->
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Transformation Type</label>
                            <select id="transformationType" class="w-full p-3 border rounded" onchange="handleTransformationChange()">
                                <option value="furnish">Add Furniture (Virtual Staging)</option>
                                <option value="empty">Remove All Furniture</option>
                                <option value="enhance">Enhance Photo Only</option>
                                <option value="redesign">Redesign Existing Furniture</option>
                                <option value="day_to_dusk">Convert to Evening/Dusk</option>
                            </select>
                        </div>
                        
                        <!-- Room Type (for interior) -->
                        <div id="roomTypeSection" class="mb-4">
                            <label class="block text-sm font-medium mb-2">Room Type</label>
                            <select id="roomType" class="w-full p-3 border rounded">
                                <option value="living_room">Living Room</option>
                                <option value="bedroom">Bedroom</option>
                                <option value="kitchen">Kitchen</option>
                                <option value="bathroom">Bathroom</option>
                                <option value="dining_room">Dining Room</option>
                                <option value="home_office">Home Office</option>
                                <option value="kid_bedroom">Kid's Bedroom</option>
                            </select>
                        </div>
                        
                        <!-- Outdoor Type (for exterior) -->
                        <div id="outdoorTypeSection" class="mb-4 hidden">
                            <label class="block text-sm font-medium mb-2">Outdoor Type</label>
                            <select id="outdoorType" class="w-full p-3 border rounded">
                                <option value="terrace">Terrace/Patio</option>
                                <option value="pool">Pool Area</option>
                                <option value="pergola">Pergola</option>
                            </select>
                        </div>
                        
                        <!-- Design Styles -->
                        <div id="designStyleSection" class="mb-6">
                            <label class="block text-sm font-medium mb-2">Select Design Style</label>
                            <div class="grid grid-cols-2 gap-2">
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="radio" name="designStyle" value="modern" class="design-radio" checked>
                                    <span class="text-sm">Contemporary</span>
                                </label>
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="radio" name="designStyle" value="traditional" class="design-radio">
                                    <span class="text-sm">Traditional</span>
                                </label>
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="radio" name="designStyle" value="midcentury" class="design-radio">
                                    <span class="text-sm">Mid-Century Modern</span>
                                </label>
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="radio" name="designStyle" value="rustic" class="design-radio">
                                    <span class="text-sm">Farmhouse</span>
                                </label>
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="radio" name="designStyle" value="artdeco" class="design-radio">
                                    <span class="text-sm">Vintage/Art Deco</span>
                                </label>
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="radio" name="designStyle" value="french" class="design-radio">
                                    <span class="text-sm">Colonial/French</span>
                                </label>
                            </div>
                        </div>
                        
                        <!-- Custom Instructions -->
                        <div id="customInstructionsSection" class="mb-6">
                            <label class="block text-sm font-medium mb-2">Special Instructions (Optional)</label>
                            <textarea id="customInstructions" rows="3" class="w-full p-3 border rounded resize-none" 
                                placeholder="e.g., 'Just add a couch and coffee table', 'Change carpet to hardwood floors', 'Make it bright and airy'"></textarea>
                            <p class="text-xs text-gray-500 mt-1">We'll interpret your instructions and apply the appropriate settings</p>
                        </div>
                        
                        <!-- Advanced Options -->
                        <div id="advancedOptions" class="mb-6 border-t pt-4">
                            <p class="text-sm font-medium mb-3">Advanced Options</p>
                            
                            <!-- Flooring Option -->
                            <div id="flooringSection" class="mb-3">
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="checkbox" id="updateFlooring" class="w-4 h-4">
                                    <span class="text-sm">Update flooring</span>
                                </label>
                            </div>
                            
                            <!-- Block Decorative Elements -->
                            <div id="blockDecorSection" class="mb-3">
                                <label class="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                                    <input type="checkbox" id="blockDecorative" class="w-4 h-4" checked>
                                    <span class="text-sm">Block decorative items (plants, vases, animals)</span>
                                </label>
                            </div>
                        </div>
                        
                        <!-- Stage Button -->
                        <button onclick="stageCurrentRoom()" id="stageBtn" class="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:bg-gray-400 disabled:cursor-not-allowed">
                            Stage This Room
                        </button>
                        
                        <!-- Status -->
                        <div id="status" class="mt-4"></div>
                        
                        <!-- Progress Bar -->
                        <div id="progressBar" class="hidden mt-4">
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div id="progressFill" class="bg-blue-600 h-2 rounded-full transition-all duration-500" style="width: 0%"></div>
                            </div>
                            <p id="progressText" class="text-sm text-gray-600 mt-1 text-center">Processing...</p>
                        </div>
                    </div>
                </div>
                
                <!-- Right Column: Results -->
                <div>
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <h2 class="text-xl font-semibold mb-4">Staging Results</h2>
                        <div id="resultsContainer" class="space-y-4">
                            <p class="text-gray-500 text-center py-8">No rooms staged yet. Upload a photo to get started!</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- All Staged Rooms Section -->
            <div id="allRoomsSection" class="mt-8 hidden">
                <h2 class="text-2xl font-semibold mb-4">All Staged Rooms</h2>
                <div id="allRoomsGrid" class="grid grid-cols-1 md:grid-cols-2 gap-6"></div>
            </div>
        </div>
    </div>
    
    <script>
        let currentImageData = null;
        let stagingJobs = [];
        let currentRequestId = null;
        let pollingInterval = null;
        let lastRequestData = null;
        
        // Check webhook status
        fetch('/api/health')
            .then(res => res.json())
            .then(data => {
                const statusEl = document.getElementById('webhookStatus');
                if (data.webhook_ready) {
                    statusEl.innerHTML = `<p class="text-green-700">✓ Webhook ready at: ${data.webhook_url}</p>`;
                    statusEl.classList.add('bg-green-50');
                } else {
                    statusEl.innerHTML = '<p class="text-amber-700">⚠ Webhook not configured - results may be delayed</p>';
                    statusEl.classList.add('bg-amber-50');
                }
            });
        
        // Clear form function
        function clearForm() {
            currentImageData = null;
            currentRequestId = null;
            document.getElementById('fileInput').value = '';
            document.getElementById('currentImagePreview').classList.add('hidden');
            document.getElementById('status').innerHTML = '';
            document.getElementById('progressBar').classList.add('hidden');
            document.getElementById('stageBtn').disabled = false;
            document.getElementById('stageBtn').textContent = 'Stage This Room';
            
            // Stop any polling
            if (pollingInterval) {
                clearInterval(pollingInterval);
                pollingInterval = null;
            }
        }
        
        // Handle space type change
        function handleSpaceTypeChange() {
            const spaceType = document.getElementById('spaceType').value;
            const roomTypeSection = document.getElementById('roomTypeSection');
            const outdoorTypeSection = document.getElementById('outdoorTypeSection');
            const transformationType = document.getElementById('transformationType');
            
            if (spaceType === 'exterior') {
                roomTypeSection.classList.add('hidden');
                outdoorTypeSection.classList.remove('hidden');
                
                // Update transformation options for exterior
                transformationType.innerHTML = `
                    <option value="outdoor">Add Outdoor Furniture</option>
                    <option value="enhance">Enhance Photo Only</option>
                    <option value="blue_sky">Add Blue Sky Effect</option>
                    <option value="day_to_dusk">Convert to Evening/Dusk</option>
                `;
            } else {
                roomTypeSection.classList.remove('hidden');
                outdoorTypeSection.classList.add('hidden');
                
                // Restore interior transformation options
                transformationType.innerHTML = `
                    <option value="furnish">Add Furniture (Virtual Staging)</option>
                    <option value="empty">Remove All Furniture</option>
                    <option value="enhance">Enhance Photo Only</option>
                    <option value="redesign">Redesign Existing Furniture</option>
                    <option value="day_to_dusk">Convert to Evening/Dusk</option>
                `;
            }
            
            handleTransformationChange();
        }
        
        // Handle transformation type change
        function handleTransformationChange() {
            const transformType = document.getElementById('transformationType').value;
            const spaceType = document.getElementById('spaceType').value;
            const designStyleSection = document.getElementById('designStyleSection');
            const flooringSection = document.getElementById('flooringSection');
            const blockDecorSection = document.getElementById('blockDecorSection');
            const advancedOptions = document.getElementById('advancedOptions');
            
            // Show/hide sections based on transformation type
            const needsDesign = ['furnish', 'redesign', 'outdoor'].includes(transformType);
            const needsFlooring = ['furnish', 'redesign'].includes(transformType) && spaceType === 'interior';
            const needsBlockDecor = ['furnish', 'redesign', 'outdoor'].includes(transformType);
            
            designStyleSection.style.display = needsDesign ? 'block' : 'none';
            flooringSection.style.display = needsFlooring ? 'block' : 'none';
            blockDecorSection.style.display = needsBlockDecor ? 'block' : 'none';
            advancedOptions.style.display = (needsFlooring || needsBlockDecor) ? 'block' : 'none';
        }
        
        // Handle file upload
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            // Clear any previous errors
            document.getElementById('status').innerHTML = '';
            
            const reader = new FileReader();
            reader.onload = function(event) {
                currentImageData = event.target.result;
                document.getElementById('previewImage').src = currentImageData;
                document.getElementById('currentImagePreview').classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        });
        
        async function stageCurrentRoom() {
            if (!currentImageData) {
                alert('Please upload a photo first');
                return;
            }
            
            const spaceType = document.getElementById('spaceType').value;
            const transformationType = document.getElementById('transformationType').value;
            const roomType = spaceType === 'interior' ? 
                document.getElementById('roomType').value : 
                document.getElementById('outdoorType').value;
            let selectedDesign = document.querySelector('input[name="designStyle"]:checked')?.value || 'modern';
            let updateFlooring = document.getElementById('updateFlooring').checked;
            let blockDecorative = document.getElementById('blockDecorative').checked;
            const customInstructions = document.getElementById('customInstructions').value.trim();
            
            // Process custom instructions
            if (customInstructions) {
                const processed = processCustomInstructions(customInstructions);
                if (processed.updateFlooring !== undefined) updateFlooring = processed.updateFlooring;
                if (processed.blockDecorative !== undefined) blockDecorative = processed.blockDecorative;
                if (processed.design) selectedDesign = processed.design;
                
                // Update UI to reflect interpreted settings
                document.getElementById('updateFlooring').checked = updateFlooring;
                document.getElementById('blockDecorative').checked = blockDecorative;
            }
            
            const btn = document.getElementById('stageBtn');
            const status = document.getElementById('status');
            const progressBar = document.getElementById('progressBar');
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            
            // Disable button and show progress
            btn.disabled = true;
            btn.innerHTML = '<span class="inline-block animate-spin mr-2">⟳</span> Processing...';
            progressBar.classList.remove('hidden');
            progressFill.style.width = '10%';
            progressText.textContent = 'Submitting request...';
            
            // Show cancel button in status
            status.innerHTML = `
                <div class="bg-blue-50 p-3 rounded mt-2 flex justify-between items-center">
                    <p class="text-blue-700">Submitting request...</p>
                    <button onclick="cancelRequest()" class="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded text-sm">
                        Cancel
                    </button>
                </div>
            `;
            
            // Prepare request data
            const requestData = {
                image: currentImageData,
                transformation_type: transformationType,
                space_type: spaceType,
                room_type: roomType,
                design_style: selectedDesign,
                update_flooring: updateFlooring,
                block_decorative: blockDecorative
            };
            
            // Store for retry
            lastRequestData = requestData;
            
            try {
                const response = await fetch('/api/stage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestData),
                    timeout: 30000 // 30 second timeout
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentRequestId = data.request_id;
                    
                    const job = {
                        requestId: data.request_id,
                        transformationType: transformationType,
                        spaceType: spaceType,
                        design: selectedDesign,
                        roomType: roomType,
                        status: 'processing',
                        originalImage: currentImageData,
                        timestamp: Date.now()
                    };
                    
                    stagingJobs.push(job);
                    
                    progressFill.style.width = '30%';
                    progressText.textContent = 'Request submitted. Processing...';
                    status.innerHTML = `
                        <div class="bg-green-50 p-3 rounded mt-2 flex justify-between items-center">
                            <p class="text-green-700">✓ Request submitted. Processing your image...</p>
                            <button onclick="cancelRequest()" class="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded text-sm">
                                Cancel
                            </button>
                        </div>
                    `;
                    
                    // Start polling for results
                    startPolling();
                    
                } else {
                    throw new Error(data.error || 'Failed to submit request');
                }
            } catch (error) {
                console.error('Error:', error);
                status.innerHTML = `<div class="bg-red-50 p-3 rounded mt-2"><p class="text-red-700">Error: ${error.message}</p></div>`;
                btn.disabled = false;
                btn.textContent = 'Stage This Room';
                progressBar.classList.add('hidden');
            }
        }
        
        function startPolling() {
            let pollCount = 0;
            const maxPolls = 90; // 3 minutes max
            
            pollingInterval = setInterval(async () => {
                pollCount++;
                
                const progressPercent = Math.min(30 + (pollCount * 0.7), 90);
                document.getElementById('progressFill').style.width = progressPercent + '%';
                document.getElementById('progressText').textContent = `Processing... ${Math.floor(pollCount * 2)}s`;
                
                try {
                    const response = await fetch('/api/recent-stagings');
                    const data = await response.json();
                    
                    let hasUpdates = false;
                    
                    stagingJobs.forEach(job => {
                        if (job.status === 'processing' && job.requestId === currentRequestId) {
                            const staging = data.stagings.find(s => s.request_id === job.requestId);
                            
                            if (staging && staging.webhook_received) {
                                job.status = 'completed';
                                job.outputImages = staging.output_images || [];
                                hasUpdates = true;
                                
                                // Complete progress
                                document.getElementById('progressFill').style.width = '100%';
                                document.getElementById('progressText').textContent = 'Complete!';
                                
                                // Clear current request
                                currentRequestId = null;
                                
                                // Reset form after delay
                                setTimeout(() => {
                                    clearForm();
                                }, 2000);
                            }
                        }
                    });
                    
                    if (hasUpdates) {
                        updateResults();
                        clearInterval(pollingInterval);
                        pollingInterval = null;
                    }
                    
                } catch (error) {
                    console.error('Polling error:', error);
                }
                
                // Stop polling after max attempts
                if (pollCount >= maxPolls) {
                    clearInterval(pollingInterval);
                    pollingInterval = null;
                    
                    // Hide progress bar
                    document.getElementById('progressBar').classList.add('hidden');
                    
                    // Show timeout message with options
                    document.getElementById('status').innerHTML = `
                        <div class="bg-amber-50 p-3 rounded mt-2">
                            <p class="text-amber-700 font-medium">Request timed out after 3 minutes</p>
                            <p class="text-sm text-amber-600 mt-1">The image may still be processing. You can:</p>
                            <div class="flex gap-2 mt-3">
                                <button onclick="retryLastRequest()" class="px-3 py-1 bg-amber-100 hover:bg-amber-200 text-amber-800 rounded text-sm">
                                    Try Again
                                </button>
                                <button onclick="checkForResults()" class="px-3 py-1 bg-amber-100 hover:bg-amber-200 text-amber-800 rounded text-sm">
                                    Check for Results
                                </button>
                                <button onclick="clearForm()" class="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded text-sm">
                                    Start Over
                                </button>
                            </div>
                        </div>
                    `;
                    
                    // Re-enable stage button
                    document.getElementById('stageBtn').disabled = false;
                    document.getElementById('stageBtn').textContent = 'Stage This Room';
                }
            }, 2000);
        }
        
        function getTransformationLabel(type) {
            const labels = {
                'furnish': 'Virtual Staging',
                'empty': 'Furniture Removed',
                'enhance': 'Enhanced',
                'redesign': 'Redesigned',
                'day_to_dusk': 'Evening View',
                'outdoor': 'Outdoor Staging',
                'blue_sky': 'Blue Sky Effect'
            };
            return labels[type] || type;
        }
        
        function updateResults() {
            const container = document.getElementById('resultsContainer');
            const allRoomsSection = document.getElementById('allRoomsSection');
            const allRoomsGrid = document.getElementById('allRoomsGrid');
            
            // Update recent results
            container.innerHTML = '';
            const recentJobs = stagingJobs.slice(-3).reverse();
            
            recentJobs.forEach(job => {
                if (job.status === 'completed' && job.outputImages.length > 0) {
                    const jobDiv = document.createElement('div');
                    jobDiv.className = 'border rounded-lg p-3 mb-3';
                    const label = getTransformationLabel(job.transformationType);
                    
                    jobDiv.innerHTML = `
                        <div class="flex justify-between items-center mb-2">
                            <h3 class="font-medium">${label}</h3>
                            <button onclick="downloadImage('${job.outputImages[0]}')" class="text-sm px-2 py-1 bg-blue-100 hover:bg-blue-200 rounded">
                                Download
                            </button>
                        </div>
                        <div class="mt-2">
                            ${job.outputImages.map((img, idx) => `
                                <img src="${img}" class="w-full h-48 object-cover rounded cursor-pointer hover:opacity-90" 
                                     onclick="window.open('${img}', '_blank')" 
                                     title="Click to view full size">
                            `).join('')}
                        </div>
                    `;
                    container.appendChild(jobDiv);
                } else if (job.status === 'processing') {
                    const jobDiv = document.createElement('div');
                    jobDiv.className = 'border rounded-lg p-3 mb-3 bg-gray-50';
                    jobDiv.innerHTML = `
                        <h3 class="font-medium mb-2">Processing...</h3>
                        <div class="animate-pulse bg-gray-200 h-48 rounded"></div>
                    `;
                    container.appendChild(jobDiv);
                }
            });
            
            // Update all rooms section
            if (stagingJobs.filter(j => j.status === 'completed').length > 0) {
                allRoomsSection.classList.remove('hidden');
                allRoomsGrid.innerHTML = '';
                
                stagingJobs.filter(j => j.status === 'completed').reverse().forEach(job => {
                    const roomDiv = document.createElement('div');
                    roomDiv.className = 'bg-white rounded-lg shadow-lg p-4';
                    
                    const date = new Date(job.timestamp);
                    const timeStr = date.toLocaleTimeString();
                    const label = getTransformationLabel(job.transformationType);
                    
                    roomDiv.innerHTML = `
                        <div class="flex items-start gap-4 mb-3">
                            <img src="${job.originalImage}" class="w-24 h-24 object-cover rounded">
                            <div class="flex-1">
                                <h3 class="font-semibold">${label}</h3>
                                <p class="text-sm text-gray-600">Staged at ${timeStr}</p>
                                <button onclick="downloadImage('${job.outputImages[0]}')" class="mt-2 text-sm px-2 py-1 bg-blue-100 hover:bg-blue-200 rounded">
                                    Download
                                </button>
                            </div>
                        </div>
                        <div class="mt-2">
                            ${job.outputImages.map((img, idx) => `
                                <img src="${img}" class="w-full h-32 object-cover rounded cursor-pointer hover:opacity-90 mb-2" 
                                     onclick="window.open('${img}', '_blank')">
                            `).join('')}
                        </div>
                    `;
                    
                    allRoomsGrid.appendChild(roomDiv);
                });
            }
        }
        
        // Download image function
        function downloadImage(url) {
            const link = document.createElement('a');
            link.href = url;
            link.download = 'staged-room-' + Date.now() + '.jpg';
            link.target = '_blank';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        
        // Process custom instructions text
        function processCustomInstructions(text) {
            const lower = text.toLowerCase();
            const result = {};
            
            // Floor-related instructions
            if (lower.includes('hardwood') || lower.includes('change floor') || lower.includes('new floor') || 
                lower.includes('update floor') || lower.includes('wood floor') || lower.includes('laminate')) {
                result.updateFlooring = true;
            }
            if (lower.includes('keep floor') || lower.includes('existing floor') || lower.includes('same floor')) {
                result.updateFlooring = false;
            }
            
            // Furniture-specific instructions
            if (lower.includes('just') || lower.includes('only') || lower.includes('minimal')) {
                result.blockDecorative = true;
                
                // If they want specific items only, we might switch to minimalist design
                if (lower.includes('couch') || lower.includes('sofa')) {
                    result.design = 'minimalist';
                }
            }
            
            // Style keywords
            if (lower.includes('bright') || lower.includes('airy') || lower.includes('light')) {
                result.design = 'scandinavian';
            }
            if (lower.includes('modern') || lower.includes('contemporary')) {
                result.design = 'modern';
            }
            if (lower.includes('farmhouse') || lower.includes('rustic') || lower.includes('country')) {
                result.design = 'rustic';
            }
            if (lower.includes('traditional') || lower.includes('classic')) {
                result.design = 'traditional';
            }
            if (lower.includes('vintage') || lower.includes('retro') || lower.includes('antique')) {
                result.design = 'artdeco';
            }
            
            // Decoration preferences
            if (lower.includes('no plants') || lower.includes('no decor') || lower.includes('no decoration')) {
                result.blockDecorative = true;
            }
            if (lower.includes('add plants') || lower.includes('with plants') || lower.includes('decorations')) {
                result.blockDecorative = false;
            }
            
            return result;
        }
        
        // Initialize form state
        handleSpaceTypeChange();
        
        // Cancel current request
        function cancelRequest() {
            if (pollingInterval) {
                clearInterval(pollingInterval);
                pollingInterval = null;
            }
            
            currentRequestId = null;
            document.getElementById('progressBar').classList.add('hidden');
            document.getElementById('status').innerHTML = '<div class="bg-gray-50 p-3 rounded mt-2"><p class="text-gray-700">Request cancelled</p></div>';
            document.getElementById('stageBtn').disabled = false;
            document.getElementById('stageBtn').textContent = 'Stage This Room';
        }
        
        // Retry last request
        async function retryLastRequest() {
            if (lastRequestData) {
                // Clear status
                document.getElementById('status').innerHTML = '';
                
                // Re-submit with same data
                await stageCurrentRoom();
            }
        }
        
        // Check for results manually
        async function checkForResults() {
            if (!currentRequestId) {
                alert('No active request to check');
                return;
            }
            
            document.getElementById('status').innerHTML = '<div class="bg-blue-50 p-3 rounded mt-2"><p class="text-blue-700">Checking for results...</p></div>';
            
            try {
                const response = await fetch('/api/recent-stagings');
                const data = await response.json();
                
                const staging = data.stagings.find(s => s.request_id === currentRequestId);
                
                if (staging && staging.webhook_received) {
                    // Found results!
                    stagingJobs.forEach(job => {
                        if (job.requestId === currentRequestId) {
                            job.status = 'completed';
                            job.outputImages = staging.output_images || [];
                        }
                    });
                    
                    updateResults();
                    document.getElementById('status').innerHTML = '<div class="bg-green-50 p-3 rounded mt-2"><p class="text-green-700">✓ Results found!</p></div>';
                    clearForm();
                } else {
                    document.getElementById('status').innerHTML = '<div class="bg-amber-50 p-3 rounded mt-2"><p class="text-amber-700">No results yet. Try again later.</p></div>';
                }
            } catch (error) {
                document.getElementById('status').innerHTML = '<div class="bg-red-50 p-3 rounded mt-2"><p class="text-red-700">Error checking results</p></div>';
            }
        }
    </script>
</body>
</html>
    ''')

@app.route('/api/health')
def health():
    webhook_url = get_webhook_url()
    return jsonify({
        'status': 'healthy',
        'instantdeco_configured': bool(INSTANTDECO_API_KEY),
        'imgbb_configured': bool(IMGBB_API_KEY),
        'webhook_ready': bool(webhook_url),
        'webhook_url': webhook_url
    })

@app.route('/api/stage', methods=['POST'])
def stage_room():
    """Submit staging request to InstantDecoAI"""
    data = request.json
    image_data = data.get('image')
    transformation_type = data.get('transformation_type', 'furnish')
    space_type = data.get('space_type', 'interior')
    room_type = data.get('room_type', 'living_room')
    design_style = data.get('design_style', 'modern')
    update_flooring = data.get('update_flooring', False)
    block_decorative = data.get('block_decorative', True)
    
    if not image_data:
        return jsonify({'success': False, 'error': 'Missing image data'})
    
    if not INSTANTDECO_API_KEY:
        return jsonify({'success': False, 'error': 'InstantDecoAI API key not configured'})
    
    try:
        # Extract base64 data
        base64_data = image_data.split(',')[1] if ',' in image_data else image_data
        
        # Upload to ImgBB first
        if not IMGBB_API_KEY:
            return jsonify({'success': False, 'error': 'ImgBB API key not configured'})
        
        imgbb_response = requests.post(
            IMGBB_API_URL,
            data={
                'key': IMGBB_API_KEY,
                'image': base64_data
            },
            timeout=30
        )
        
        if imgbb_response.status_code != 200:
            return jsonify({'success': False, 'error': 'Failed to upload image to ImgBB'})
        
        imgbb_data = imgbb_response.json()
        if not imgbb_data.get('success'):
            return jsonify({'success': False, 'error': 'ImgBB upload failed'})
        
        image_url = imgbb_data['data']['url']
        
        # Get webhook URL
        webhook_url = get_webhook_url()
        
        # Prepare InstantDecoAI payload
        payload = {
            "transformation_type": transformation_type,
            "img_url": image_url,
            "num_images": 1
        }
        
        # Add webhook if available
        if webhook_url:
            payload["webhook_url"] = webhook_url
        
        # Add parameters based on transformation type
        if transformation_type in ['furnish', 'redesign', 'outdoor']:
            payload["room_type"] = room_type
            payload["design"] = design_style
            
            # Build block_element list
            block_elements = ["wall", "ceiling", "windowpane", "door"]
            
            # Add floor to block list if not updating flooring
            if not update_flooring and transformation_type != 'outdoor':
                block_elements.append("floor")
            
            # Add decorative elements to block list if requested
            if block_decorative:
                # Add animal and common decorative items
                block_elements.extend(["animal", "plant", "vase", "basket"])
            
            # For outdoor, add outdoor-specific blocks
            if transformation_type == 'outdoor':
                block_elements.extend(["sky", "house", "building", "tree", "car"])
            
            payload["block_element"] = ",".join(block_elements)
        
        # Call InstantDecoAI
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {INSTANTDECO_API_KEY}'
        }
        
        response = requests.post(INSTANTDECO_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                request_id = result.get('response', {}).get('request_id')
                
                # Store in history
                staging_history.append({
                    'request_id': request_id,
                    'timestamp': datetime.now().isoformat(),
                    'transformation_type': transformation_type,
                    'space_type': space_type,
                    'room_type': room_type,
                    'design_style': design_style,
                    'update_flooring': update_flooring,
                    'block_decorative': block_decorative,
                    'status': 'processing',
                    'webhook_received': False,
                    'input_image': image_url
                })
                
                return jsonify({
                    'success': True,
                    'request_id': request_id,
                    'webhook_url': webhook_url,
                    'message': 'Staging request submitted successfully!'
                })
            else:
                app.logger.error(f"InstantDeco API error response: {result}")
                return jsonify({'success': False, 'error': f"API error: {result.get('message', 'Unknown error')}"})
        else:
            app.logger.error(f"InstantDeco HTTP error: {response.status_code} - {response.text}")
            return jsonify({'success': False, 'error': f'API request failed: HTTP {response.status_code}'})
        
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Request timed out. Please try again.'})
    except Exception as e:
        app.logger.error(f"Stage room error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Handle InstantDecoAI webhook"""
    try:
        data = request.json
        request_id = data.get('request_id')
        
        app.logger.info(f"Webhook received for request: {request_id}")
        
        # Find the staging request
        for staging in staging_history:
            if staging['request_id'] == request_id:
                staging['webhook_received'] = True
                staging['webhook_timestamp'] = datetime.now().isoformat()
                staging['status'] = data.get('status', 'completed')
                
                # Extract output images
                output = data.get('output', '')
                if output and isinstance(output, str):
                    # Split by comma and clean up URLs
                    images = [url.strip() for url in output.split(',') if url.strip()]
                    staging['output_images'] = images
                
                app.logger.info(f"Webhook processed successfully: {len(images)} images")
                break
        
        return jsonify({'status': 'ok'})
    except Exception as e:
        app.logger.error(f"Webhook error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/recent-stagings')
def recent_stagings():
    """Get recent staging requests"""
    # Return last 50 stagings, newest first
    recent = sorted(staging_history, key=lambda x: x['timestamp'], reverse=True)[:50]
    return jsonify({'stagings': recent})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)