const fetch = require('node-fetch');

module.exports = async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { image } = req.body;

  if (!image) {
    return res.status(400).json({ success: false, error: 'Missing image data' });
  }

  try {
    // Check for API key
    if (!process.env.IMGBB_API_KEY) {
      return res.status(500).json({ success: false, error: 'ImgBB API key not configured' });
    }

    // Extract base64 data (remove data:image/...;base64, prefix if present)
    let base64Data = image;
    if (image.startsWith('data:')) {
      const matches = image.match(/^data:([^;]+);base64,(.+)$/);
      if (matches) {
        base64Data = matches[2];
      }
    }

    // Upload to ImgBB using URL-encoded form (no FormData needed)
    const imgbbApiKey = process.env.IMGBB_API_KEY;

    const params = new URLSearchParams();
    params.append('image', base64Data);
    params.append('expiration', '600'); // Auto-delete after 10 minutes

    const response = await fetch(`https://api.imgbb.com/1/upload?key=${imgbbApiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: params.toString()
    });

    const data = await response.json();

    if (data.success && data.data && data.data.url) {
      return res.status(200).json({
        success: true,
        url: data.data.url,
        deleteUrl: data.data.delete_url,
        expiresIn: 600
      });
    } else {
      console.error('ImgBB upload failed:', data);
      throw new Error(data.error?.message || 'Failed to upload image to ImgBB');
    }

  } catch (error) {
    console.error('Image upload error:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Failed to upload image'
    });
  }
}
