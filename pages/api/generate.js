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
  
  const { image, style, requirements, apiKey } = req.body;
  
  if (!style) {
    return res.status(400).json({ error: 'Style is required' });
  }
  
  // Use provided API key or environment variable
  const openaiApiKey = apiKey || process.env.OPENAI_API_KEY;
  
  if (!openaiApiKey) {
    return res.status(400).json({ 
      error: 'No API key provided. Please add your OpenAI API key or set OPENAI_API_KEY environment variable.' 
    });
  }

  try {
    // Build the prompt
    let prompt = `Interior design photo of a ${style} style room with furniture and decor. `;
    if (requirements) {
      prompt += `${requirements}. `;
    }
    prompt += `Keep the exact room structure, windows, walls, and architectural elements unchanged. Only add furniture and decor. High quality, photorealistic, professional interior design photography.`;
    
    // Call OpenAI DALL-E 3 API
    const response = await fetch('https://api.openai.com/v1/images/generations', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openaiApiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: "dall-e-3",
        prompt: prompt,
        n: 1,
        size: "1024x1024",
        quality: "standard",
        style: "natural"
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || 'Failed to generate image');
    }

    const data = await response.json();
    
    // Transform the response to match the expected format
    const images = data.data.map(img => img.url);

    // Return the generated images
    res.status(200).json({ 
      images: images || [],
      status: 'success'
    });
    
  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({ 
      error: error.message || 'Failed to generate images',
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
}