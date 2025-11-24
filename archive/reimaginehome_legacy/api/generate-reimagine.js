export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  // Handle OPTIONS request
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  const { image, style, requirements, apiKey, mode = 'virtual_staging', roomType = 'Living Room' } = req.body;
  
  if (!image || !style) {
    return res.status(400).json({ error: 'Image and style are required' });
  }
  
  // Use provided API key or environment variable
  const reimagineApiKey = apiKey || process.env.REIMAGINEHOME_API_KEY;
  
  if (!reimagineApiKey) {
    return res.status(400).json({ 
      error: 'No API key provided. Please add your ReimagineHome API key or set REIMAGINEHOME_API_KEY environment variable.' 
    });
  }

  try {
    // Convert base64 to buffer for form data
    const base64Data = image.replace(/^data:image\/\w+;base64,/, '');
    const imageBuffer = Buffer.from(base64Data, 'base64');
    
    // Prepare form data
    const FormData = require('form-data');
    const form = new FormData();
    
    // Common parameters
    form.append('design_type', 'Interior');
    form.append('design_style', style);
    form.append('room_type', roomType);
    form.append('no_design', '1'); // Generate 1 design
    
    if (mode === 'virtual_staging') {
      // Virtual staging specific parameters
      form.append('image', imageBuffer, { filename: 'room.jpg', contentType: 'image/jpeg' });
      form.append('ai_intervention', 'Mid'); // Can be 'Very Low', 'Low', 'Mid', 'Extreme'
      if (requirements) {
        form.append('custom_instruction', requirements);
      }
      
      // Step 1: Submit virtual staging request
      const response = await fetch('https://homedesigns.ai/api/v2/virtual_staging', {
        method: 'POST',
        headers: {
          'api-key': reimagineApiKey,
          ...form.getHeaders()
        },
        body: form
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || errorData.error || 'Failed to initiate virtual staging');
      }

      const { id: queueId } = await response.json();
      
      // Step 2: Poll for results
      let attempts = 0;
      const maxAttempts = 40; // 40 attempts * 1.5 seconds = 60 seconds max
      let result;
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 1500)); // Wait 1.5 seconds
        
        const statusResponse = await fetch(
          `https://homedesigns.ai/api/v2/virtual_staging/status_check/${queueId}`,
          {
            method: 'GET',
            headers: {
              'api-key': reimagineApiKey
            }
          }
        );
        
        if (!statusResponse.ok) {
          throw new Error('Failed to check status');
        }
        
        result = await statusResponse.json();
        
        if (result.status === 'SUCCESS' && result.output_images) {
          break;
        } else if (result.status === 'FAILED' || result.status === 'ERROR') {
          throw new Error('Virtual staging failed');
        }
        
        attempts++;
      }
      
      if (!result || !result.output_images) {
        throw new Error('Virtual staging timed out');
      }
      
      // Return the generated images
      res.status(200).json({ 
        images: result.output_images || [],
        status: 'success'
      });
      
    } else if (mode === 'redesign') {
      // Redesign endpoint for furnished rooms
      form.append('image', imageBuffer, { filename: 'room.jpg', contentType: 'image/jpeg' });
      if (requirements) {
        form.append('prompt', requirements);
      }
      
      const response = await fetch('https://homedesigns.ai/api/v2/redesign', {
        method: 'POST',
        headers: {
          'api-key': reimagineApiKey,
          ...form.getHeaders()
        },
        body: form
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || errorData.error || 'Failed to redesign room');
      }

      const result = await response.json();
      
      // Extract images from response
      let images = [];
      if (result.output_images) {
        images = result.output_images;
      } else if (result.data && result.data.output_images) {
        images = result.data.output_images;
      }
      
      res.status(200).json({ 
        images: images || [],
        status: 'success'
      });
    } else {
      throw new Error('Invalid mode. Use "virtual_staging" or "redesign"');
    }
    
  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({ 
      error: error.message || 'Failed to generate images',
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
}