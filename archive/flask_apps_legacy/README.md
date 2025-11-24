# Flask Apps Legacy Archive

**Date Archived**: November 24, 2025
**Reason**: Current deployment uses Vercel serverless functions, not Flask

## Contents

This directory contains legacy Flask-based implementations that are no longer used in production.

### Current Architecture (Vercel)

The production app at https://aistager.vercel.app uses:
- **Frontend**: `public/index.html` (React single-file component)
- **Backend**: Vercel serverless functions in `api/` directory
  - `api/kie-stage.js` - Primary AI service (Kie.ai)
  - `api/kie-check-status.js` - Status polling
  - `api/gemini-stage.js` - Backup AI service (Google Gemini)
- **No Flask server required**

### Archived Flask Apps

All these apps follow the same pattern:
- Single-file Flask server with embedded HTML
- Various AI service integrations
- Local development focus

**Main Apps**:
- `main.py` - Original Flask implementation (15KB)
- `app.py` - Alternative Flask version
- `app_production.py` - Production-focused version

**Service-Specific Variants**:
- `app_cloudinary.py` - Uses Cloudinary for image hosting
- `app_local_upload.py` - Local file uploads
- `app_serve_local.py` - Serves local files
- `app_complete.py` - Full-featured version
- `app_polling.py` - Polling-based status checks
- `app_polling_enhanced.py` - Enhanced polling

**Debug Versions**:
- `app_debug.py` - Debug mode
- `app_debug_complete.py` - Debug with all features

### Why Flask Was Replaced

1. **Deployment Simplicity**: Vercel serverless functions require no server management
2. **Scalability**: Auto-scaling with serverless vs. single Flask instance
3. **Cost**: Free tier on Vercel vs. hosting Flask server
4. **Modern Architecture**: JAMstack pattern (static frontend + API functions)
5. **No Webhook Issues**: Serverless functions work with async APIs seamlessly

### Historical Context

**Development Timeline**:
```
Flask Apps (Multiple iterations) → Vercel Serverless Functions (Current)
```

These Flask apps were developed during the exploration phase when testing:
- ReimagineHome API
- InstantDeco API
- Various image upload services (Cloudinary, ImgBB)
- Webhook vs polling approaches

### Reactivation (If Needed)

To run a Flask app locally for testing:

```bash
# Install dependencies
pip install flask flask-cors python-dotenv requests

# Run an app
python main.py

# Visit
http://localhost:5000
```

**Note**: You'll need to set up `.env.local` with appropriate API keys.

### Current Production Stack

```
Architecture: JAMstack
Frontend: React (CDN) + Tailwind CSS (CDN)
Backend: Vercel Serverless Functions (Node.js)
AI Service: Kie.ai (primary), Google Gemini (backup)
Image Hosting: ImgBB
Deployment: Vercel
Status: ✅ Deployed and operational
```

### Summary

These Flask apps represent valuable development history but are **not part of the current production system**. The project has evolved to a serverless architecture that better fits modern deployment practices.

**Total Files**: 13 Flask applications
**Total Code**: ~5,000+ lines
**Status**: Archived for reference, fully replaced by Vercel functions
