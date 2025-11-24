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
  
  const { 
    image, 
    style, 
    requirements, 
    apiKey, 
    roomType = 'ST-INT-0011', // Default to Living Room
    colorPreference,
    generationCount = 1
  } = req.body;
  
  if (!image || !roomType) {
    return res.status(400).json({ error: 'Image and room type are required' });
  }
  
  // Use provided API key or environment variable
  const reimagineApiKey = apiKey || process.env.REIMAGINEHOME_API_KEY;
  
  if (!reimagineApiKey) {
    return res.status(400).json({ 
      error: 'No API key provided. Please add your ReimagineHome API key.' 
    });
  }

  try {
    // In production, you would:
    // 1. Upload the base64 image to cloud storage (S3, Cloudinary, etc.)
    // 2. Get a public URL for the image
    // For this example, we'll use a placeholder URL
    const imageUrl = 'https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800';
    
    // Step 1: Create masks
    const maskResponse = await fetch('https://api.reimaginehome.ai/v1/create_mask', {
      method: 'POST',
      headers: {
        'api-key': reimagineApiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        image_url: imageUrl
      })
    });

    if (!maskResponse.ok) {
      const error = await maskResponse.json();
      throw new Error(error.error || 'Failed to create masks');
    }

    const maskData = await maskResponse.json();
    const maskJobId = maskData.data.job_id;
    
    // Step 2: Poll for mask completion
    let masks = null;
    const maxAttempts = 30;
    
    for (let i = 0; i < maxAttempts; i++) {
      await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
      
      const statusResponse = await fetch(
        `https://api.reimaginehome.ai/v1/create_mask/${maskJobId}`,
        {
          headers: { 'api-key': reimagineApiKey }
        }
      );
      
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        if (statusData.data.job_status === 'done') {
          masks = statusData.data.masks;
          break;
        } else if (statusData.data.job_status === 'error') {
          throw new Error('Mask creation failed');
        }
      }
    }
    
    if (!masks) {
      throw new Error('Mask creation timed out');
    }
    
    // Step 3: Generate staged image
    // Filter for furnishing masks (for virtual staging)
    const furnishingMasks = masks
      .filter(m => m.category.includes('furnishing'))
      .map(m => m.url);
    
    const maskUrls = furnishingMasks.length > 0 ? furnishingMasks : [masks[0].url];
    
    // Build generation payload
    const generationPayload = {
      image_url: imageUrl,
      mask_urls: maskUrls,
      mask_category: 'furnishing', // For virtual staging
      space_type: roomType,
      generation_count: generationCount
    };
    
    // Add optional parameters
    if (style) {
      generationPayload.design_theme = style.toLowerCase();
    }
    if (colorPreference) {
      generationPayload.color_preference = colorPreference;
    }
    if (requirements) {
      generationPayload.additional_prompt = requirements;
    }
    
    // In production, you'd add:
    // generationPayload.webhook_url = 'https://your-app.com/api/reimagine-webhook';
    
    const genResponse = await fetch('https://api.reimaginehome.ai/v1/generate_image', {
      method: 'POST',
      headers: {
        'api-key': reimagineApiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(generationPayload)
    });

    if (!genResponse.ok) {
      const error = await genResponse.json();
      throw new Error(error.error_message || error.error || 'Failed to generate image');
    }

    const genResult = await genResponse.json();
    
    // Since REimagineHome uses webhooks for results, in production you would:
    // 1. Store the job_id in a database
    // 2. Return immediately with the job_id
    // 3. Handle the webhook callback to get the final images
    
    // For this example, we'll return a success message
    res.status(200).json({ 
      status: 'success',
      message: 'Staging job initiated',
      job_id: genResult.job_id,
      note: 'Results will be delivered via webhook in production',
      // In a real implementation, these would come from the webhook
      images: [imageUrl] // Placeholder
    });
    
  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({ 
      error: error.message || 'Failed to generate images',
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
}