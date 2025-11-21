# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AiStager is an AI-powered interior design application that transforms room photos by adding furniture, changing paint colors, and enhancing decor while preserving the exact room structure.

## Technical Stack

- **Frontend**: React (single-file component in public/index.html)
- **Backend**: 
  - Flask API (main.py) - standalone Python backend
  - Vercel Serverless Function (pages/api/generate.js) - for deployment
- **Styling**: Tailwind CSS (CDN)
- **AI Service**: OpenAI DALL-E 3 API
- **Deployment**: Vercel

## Project Structure

```
AiStager/
├── main.py                  # Flask backend (alternative to Vercel)
├── package.json            # Node.js dependencies
├── pages/
│   └── api/
│       └── generate.js     # Vercel API endpoint
├── public/
│   └── index.html         # React frontend
├── static/                # Static files for Flask
├── .gitignore
├── .env.local.example     # Environment variables template
└── CLAUDE.md
```

## Commands

### Development
```bash
# Install dependencies
npm install

# Run with Vercel CLI (recommended)
npm run dev
# or
vercel dev

# Run Flask backend (alternative)
python main.py
```

### Deployment
```bash
# Deploy to Vercel
vercel

# Set environment variable on Vercel
vercel env add REPLICATE_API_TOKEN
```

## Architecture

1. **Frontend Flow**:
   - User uploads image via drag & drop
   - Selects design style (Modern, Scandinavian, etc.)
   - Optionally adds custom requirements
   - Sends request to `/api/generate`

2. **Backend Processing**:
   - Receives image (base64), style, and requirements
   - Calls Replicate API with ControlNet model
   - Uses specific prompts to preserve room structure
   - Polls for completion
   - Returns 3 generated variations

3. **AI Integration**:
   - Model: OpenAI DALL-E 3
   - Generates 1 high-quality image per request
   - Uses prompts designed to preserve room structure while changing decor

## Key Implementation Details

- **CORS Handling**: API endpoint includes CORS headers for browser compatibility
- **Image Format**: Base64 encoded images in requests
- **Polling**: Implements timeout polling for Replicate predictions (60s max)
- **Error Handling**: Graceful fallbacks for API failures

## Environment Variables

```
OPENAI_API_KEY=sk_xxxxxxxxxxxxx  # Required for production
```

## Development Notes

- The Flask backend (main.py) is an alternative implementation
- Vercel deployment is recommended for production
- Frontend works without API key (shows mock results)
- API key can be provided via environment variable or UI input