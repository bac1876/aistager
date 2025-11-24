# Deploying to Render.com

## Step-by-Step Instructions

### 1. Prepare Your Code

First, you need to get this code into a GitHub repository:

Option A - Create new repo:
1. Go to https://github.com/new
2. Name it "aistager"
3. Create repository
4. Upload these files:
   - `app.py`
   - `requirements.txt`
   - `render.yaml`

Option B - Use GitHub Desktop:
1. Open GitHub Desktop
2. Add this folder as a repository
3. Commit and push to GitHub

### 2. Deploy to Render

1. **Sign up** at https://render.com (free, no credit card)

2. **Connect GitHub**:
   - Click "New +" → "Web Service"
   - Click "Connect account" under GitHub
   - Authorize Render

3. **Select your repository**:
   - Find your "aistager" repo
   - Click "Connect"

4. **Configure the service**:
   - Name: `aistager` (or choose your own)
   - Region: Oregon (US West) or closest to you
   - Branch: main
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

5. **Add environment variable**:
   - Scroll down to "Environment Variables"
   - Click "Add Environment Variable"
   - Key: `REIMAGINEHOME_API_KEY`
   - Value: `687bc04ed95da6f6b52b0276` (your API key)

6. **Create Web Service**:
   - Click the "Create Web Service" button
   - Wait 2-5 minutes for deployment

### 3. Use Your App

Once deployed, you'll get a URL like:
`https://aistager.onrender.com`

This URL is public and permanent - no more ngrok issues!

### Benefits of Render:

✅ Free tier (no credit card)
✅ Automatic HTTPS
✅ No interstitial pages
✅ Works perfectly with APIs
✅ Auto-deploys when you update GitHub

### Important Notes:

- Free tier apps sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Once awake, it's fast
- Perfect for testing and personal use