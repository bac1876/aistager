module.exports = async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  const geminiKey = process.env.GEMINI_API_KEY;

  return res.status(200).json({
    gemini_configured: !!geminiKey,
    gemini_preview: geminiKey ? `${geminiKey.substring(0, 15)}...` : 'NOT SET',
    node_env: process.env.NODE_ENV,
    vercel_env: process.env.VERCEL_ENV,
    version: '2.0.0'
  });
}
