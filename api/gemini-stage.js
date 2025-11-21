const { GoogleGenAI, Modality } = require("@google/genai");

module.exports = async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const {
    image,
    transformation_type = 'furnish',
    space_type = 'interior',
    room_type = 'living_room',
    design_style = 'modern',
    update_flooring = false,
    block_decorative = true
  } = req.body;

  if (!image) {
    return res.status(400).json({ success: false, error: 'Missing image data' });
  }

  if (!process.env.GEMINI_API_KEY) {
    return res.status(500).json({ success: false, error: 'Gemini API key not configured' });
  }

  try {
    // Initialize Gemini AI
    const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

    // Extract base64 data and determine mime type
    let base64Data, mimeType;

    if (image.startsWith('data:')) {
      const matches = image.match(/^data:([^;]+);base64,(.+)$/);
      if (!matches) {
        throw new Error('Invalid base64 image format');
      }
      mimeType = matches[1];
      base64Data = matches[2];
    } else {
      // Assume it's already base64 without prefix
      base64Data = image;
      mimeType = 'image/jpeg'; // Default to JPEG
    }

    // Build prompt based on transformation type
    let prompt = '';
    const rules = [
      'Do not make any structural changes to the room (do not add or remove walls, windows, doors, or permanent fixtures).',
      'Preserve the exact room layout and architectural features.'
    ];

    // Format room type for natural language
    const roomName = room_type.replace(/_/g, ' ');
    const styleName = design_style.replace(/_/g, ' ');
    const spaceTypeText = space_type === 'exterior' ? 'outdoor space' : roomName;

    switch (transformation_type) {
      case 'furnish':
        prompt = `Professionally stage this empty ${spaceTypeText} by adding furniture and decor in a ${styleName} style. Create a high-end, aesthetically pleasing result suitable for a real estate listing with enhanced lighting and beautiful furniture placement.`;
        if (block_decorative) {
          rules.push('Minimize or avoid adding decorative items like plants, vases, or animals.');
        }
        break;

      case 'empty':
        prompt = `Remove all furniture, decor, and movable items from this ${spaceTypeText}. Show the empty room with clean walls and floors. Preserve all architectural features, windows, doors, and built-in fixtures.`;
        // No design style for empty rooms
        break;

      case 'redesign':
        prompt = `Redesign this ${spaceTypeText} in a ${styleName} style. Replace existing furniture and decor with new pieces that match the ${styleName} aesthetic. Create a cohesive, professionally designed space suitable for real estate marketing.`;
        if (block_decorative) {
          rules.push('Minimize decorative items like plants, vases, or animals.');
        }
        break;

      case 'enhance':
        prompt = `Enhance this ${spaceTypeText} photo by improving lighting, color balance, and overall visual quality. Make the space look more appealing and professional for real estate marketing. Do not add, remove, or change any furniture or decor.`;
        rules.push('Do not add or remove any furniture or objects.');
        rules.push('Do not change the room layout or furniture placement.');
        break;

      case 'renovate':
        prompt = `Dramatically transform and renovate this ${spaceTypeText} in a ${styleName} style. Apply creative AI processing to completely reimagine the space with new furniture, enhanced lighting, and a fresh design. Create a stunning, high-end result that showcases the room's potential.`;
        break;

      case 'day_to_dusk':
        prompt = `Convert this ${spaceTypeText} to an evening/dusk scene. Add warm, ambient lighting with sunset or twilight tones. Make the space look cozy and inviting with appropriate evening lighting. Do not change furniture, decor, or room layout.`;
        rules.push('Do not change furniture or decor.');
        break;

      case 'outdoor':
        prompt = `Add outdoor furniture and decor to this ${spaceTypeText} in a ${styleName} style. Create an inviting outdoor living space suitable for real estate marketing.`;
        rules.push('Preserve all existing structures, buildings, and landscape features.');
        break;

      case 'blue_sky':
        prompt = `Enhance this outdoor space photo by adding a beautiful blue sky with natural clouds. Improve overall lighting and make the space look more appealing. Do not change the space itself, furniture, or landscape.`;
        rules.push('Do not change the outdoor space or furniture.');
        break;

      default:
        throw new Error(`Unknown transformation type: ${transformation_type}`);
    }

    // Add flooring instructions
    if (transformation_type !== 'empty' && transformation_type !== 'enhance' && transformation_type !== 'day_to_dusk') {
      if (update_flooring) {
        prompt += ` Update the flooring with new, stylish flooring that fits the ${styleName} theme.`;
      } else {
        rules.push('Do not change the flooring material, color, or pattern.');
      }
    }

    // Combine prompt with rules
    const fullPrompt = `${prompt}\n\nIMPORTANT RULES: ${rules.join(' ')}`;

    console.log('Gemini API Request:', {
      transformation_type,
      room_type,
      design_style,
      promptLength: fullPrompt.length
    });

    // Call Gemini API
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash-image',
      contents: {
        parts: [
          {
            inlineData: {
              data: base64Data,
              mimeType: mimeType,
            },
          },
          {
            text: fullPrompt,
          },
        ],
      },
      config: {
        responseModalities: [Modality.IMAGE, Modality.TEXT],
      },
    });

    // Check for safety blocks
    const firstCandidate = response.candidates?.[0];
    if (!firstCandidate) {
      const blockReason = response.promptFeedback?.blockReason;
      if (blockReason) {
        console.error('Request blocked:', blockReason);
        throw new Error(`Request was blocked by safety filters: ${blockReason}. Please try a different image.`);
      }
      throw new Error('The AI model did not return a valid response.');
    }

    // Extract the generated image
    let generatedImageBase64 = null;
    for (const part of firstCandidate.content?.parts || []) {
      if (part.inlineData && part.inlineData.mimeType.startsWith('image/')) {
        generatedImageBase64 = part.inlineData.data;
        break;
      }
    }

    if (!generatedImageBase64) {
      throw new Error('No staged image was returned from the Gemini API.');
    }

    // Return the staged image
    const imageDataUrl = `data:image/jpeg;base64,${generatedImageBase64}`;

    return res.status(200).json({
      success: true,
      images: [imageDataUrl],
      status: 'completed',
      message: 'Image staged successfully with Gemini AI'
    });

  } catch (error) {
    console.error('Gemini staging error:', error);

    // Handle specific error types
    if (error.message && error.message.includes('API key not valid')) {
      return res.status(500).json({
        success: false,
        error: 'Invalid Gemini API key. Please check your configuration.'
      });
    }

    if (error.message && error.message.includes('blocked')) {
      return res.status(400).json({
        success: false,
        error: error.message
      });
    }

    return res.status(500).json({
      success: false,
      error: error.message || 'Failed to stage image with Gemini AI'
    });
  }
}
