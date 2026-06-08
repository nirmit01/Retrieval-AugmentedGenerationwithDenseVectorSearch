# Deployment Guide

## Quick Deployment Options

### Option 1: Deploy to Render.com (Recommended)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/youtube-video-chatbot.git
   git push -u origin main
   ```

2. **Deploy Backend on Render**
   - Go to render.com and connect GitHub
   - Click "New +" → "Web Service"
   - Select your repo
   - Add environment variable: `HUGGINGFACEHUB_API_TOKEN` with your token
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app:app --host 0.0.0.0 --port 10000`

3. **Deploy Frontend on Render**
   - Create another "Web Service" for the same repo
   - Build Command: `npm install && npm run build`
   - Publish directory: `dist`
   - Add environment variable: `VITE_API_URL` with your backend URL
   - Note: Change frontend api.js to use BASE_URL

### Option 2: Docker Compose (Local Testing)

```bash
docker-compose up --build
```
Access at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

### Option 3: Frontend Static Hosting

1. Build frontend:
```bash
cd frontend
npm run build
```

2. Upload `dist` folder to:
   - Netlify (drag and drop)
   - Vercel
   - GitHub Pages

3. Set frontend to use:
```javascript
const BASE_URL = "YOUR_BACKEND_URL";
```

### Environment Variables Needed

```
HUGGINGFACEHUB_API_TOKEN=hf_xxxxxxxxxxxxxxx
```

## Production Notes

1. **Memory Usage**: The LLM model `openai/gpt-oss-120b` is large. Consider using a smaller model for production.

2. **API Costs**: HuggingFace API usage costs money. Monitor usage.

3. **Security**: Never expose HuggingFace tokens in client-side code.

4. **Scaling**: For multiple users, consider:
   - Using a proper vector database (Pinecone, ChromaDB)
   - Adding Redis for session management
   - Using a queue system (Celery) for processing

## Heroku Deployment (Alternative)

1. Create `requirements.txt` in backend with:
```
fastapi==0.111.0
uvicorn[standard]==0.29.0
...
```

2. Create `Procfile`:
```
web: uvicorn app:app --host 0.0.0.0 --port $PORT
```

3. Create frontend buildpack for static files

## Quick Test Commands

After deployment, test with:
```bash
curl YOUR_BACKEND_URL/process_video -X POST -d '{"url": "https://youtu.be/BmUZ2wp1lM8"}'
```