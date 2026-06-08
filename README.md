# 🎬 YT Summarizer — YouTube RAG Chat App

Paste any YouTube link → get an AI-generated summary → chat with the video using RAG.

Built with **FastAPI · LangChain · FAISS · HuggingFace · React (Vite)**

---

## 📁 Project Structure

```
yt-summarizer/
├── backend/
│   ├── app.py              ← FastAPI app (API endpoints)
│   ├── transcript.py       ← YouTube URL parsing + transcript fetching
│   ├── rag_pipeline.py     ← Chunking, embeddings, FAISS, RAG Q&A
│   ├── utils.py            ← Shared helpers
│   ├── requirements.txt    ← Python dependencies
│   └── .env.example        ← Environment variable template
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── App.jsx             ← Root component / page
│   │   ├── components/
│   │   │   ├── VideoInput.jsx      ← URL input bar
│   │   │   ├── SummaryPanel.jsx    ← AI summary display
│   │   │   ├── ChatInterface.jsx   ← ChatGPT-style Q&A
│   │   │   └── LoadingOverlay.jsx  ← Full-screen loading state
│   │   ├── services/
│   │   │   └── api.js              ← All fetch calls to the backend
│   │   ├── styles.css              ← Full app CSS
│   │   └── index.jsx               ← React entry point
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── vercel.json
│   └── .env.example
│
├── render.yaml             ← One-click Render deployment config
└── .gitignore
```

---

## ⚙️ Architecture

```
User pastes YouTube URL
        │
        ▼
[FastAPI /process_video]
   ├── Extract video ID from URL
   ├── Fetch transcript (youtube-transcript-api)
   ├── Chunk transcript (RecursiveCharacterTextSplitter 1000/200)
   ├── Embed chunks (sentence-transformers/all-MiniLM-L6-v2)
   ├── Store in FAISS vector index (in-memory, keyed by video_id)
   └── Generate summary (LLM via HuggingFace Inference API)
        │
        ▼
User asks a question
        │
        ▼
[FastAPI /ask_question]
   ├── Embed question
   ├── Retrieve top-4 chunks from FAISS (similarity search)
   ├── Build prompt: context + question
   └── LLM generates answer → returned to frontend
```

---

## 🚀 Setup & Run Locally

### Prerequisites

- Python 3.11+
- Node.js 18+
- A free [HuggingFace account](https://huggingface.co/settings/tokens) with an API token

---

### Step 1 — Clone the repo

```bash
git clone https://github.com/your-username/yt-summarizer.git
cd yt-summarizer
```

---

### Step 2 — Set up the Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Create your .env file from the template
cp .env.example .env
```

Open `backend/.env` and add your HuggingFace token:

```
HUGGINGFACEHUB_API_TOKEN=hf_your_real_token_here
```

> **Where do I get a token?**
> Go to https://huggingface.co/settings/tokens → New token → Role: Read → Copy it.

---

### Step 3 — Run the Backend

```bash
# Make sure you're in the backend/ directory with venv activated
uvicorn app:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Test it at: http://127.0.0.1:8000

---

### Step 4 — Set up the Frontend

Open a **new terminal tab**:

```bash
cd frontend
npm install
```

---

### Step 5 — Run the Frontend

```bash
npm run dev
```

Open http://localhost:3000 in your browser.

> The Vite dev server automatically proxies `/process_video` and `/ask_question`
> to `http://localhost:8000` — no CORS issues in development.

---

## 🌐 Deploy to Production

### Backend → Render (free tier)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render will auto-detect `render.yaml` and configure everything
5. In the Render dashboard → Environment → add:
   ```
   HUGGINGFACEHUB_API_TOKEN = hf_your_token
   ```
6. Deploy → copy the URL (e.g. `https://yt-summarizer-backend.onrender.com`)

---

### Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → New Project
2. Import your GitHub repo
3. Set **Root Directory** to `frontend`
4. Add environment variable:
   ```
   REACT_APP_API_URL = https://yt-summarizer-backend.onrender.com
   ```
5. Deploy → your app is live!

---

## 🔑 Environment Variables Summary

| Variable | Where | Description |
|---|---|---|
| `HUGGINGFACEHUB_API_TOKEN` | `backend/.env` | HuggingFace API token |
| `REACT_APP_API_URL` | `frontend/.env` | Backend URL (production only) |

---

## 📡 API Reference

### `POST /process_video`

```json
// Request
{ "url": "https://youtube.com/watch?v=VIDEO_ID" }

// Response
{
  "video_id": "VIDEO_ID",
  "summary": "**Summary of the video**\n- Key point 1\n...",
  "transcript_preview": "First 300 characters of transcript...",
  "chunk_count": 42
}
```

### `POST /ask_question`

```json
// Request
{ "video_id": "VIDEO_ID", "question": "Who is the speaker?" }

// Response
{ "answer": "The speaker is Johnny Harris.", "video_id": "VIDEO_ID" }
```

### `GET /`

Health check — returns `{ "status": "ok" }`.

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `TranscriptsDisabled` error | Video has no captions. Try a video with CC enabled. |
| `HUGGINGFACEHUB_API_TOKEN` not set | Make sure `.env` exists in `backend/` with the token. |
| CORS error in browser | Check that `REACT_APP_API_URL` points to your backend. |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside the venv. |
| Slow first request | The embedding model downloads ~90MB on first run. Subsequent calls are fast. |
| Render free tier sleeps | Free Render services sleep after 15 min of inactivity. First request will be slow (~30s). |

---

## 🧠 How the AI Works (from notebook → production)

| Notebook cell | Production file | What it does |
|---|---|---|
| `get_youtube_id()` | `transcript.py` | Parse video ID from any URL format |
| `ytt_api.fetch()` | `transcript.py` | Download transcript text |
| `RecursiveCharacterTextSplitter` | `rag_pipeline.py` | Split into 1000-char chunks |
| `HuggingFaceEmbeddings` | `rag_pipeline.py` | Embed with `all-MiniLM-L6-v2` |
| `FAISS.from_documents` | `rag_pipeline.py` | Build searchable vector index |
| `retriever.invoke()` | `rag_pipeline.py` | Find top-4 relevant chunks |
| `RunnableParallel` chain | `rag_pipeline.py` | Full RAG chain |
| `HuggingFaceEndpoint` | `rag_pipeline.py` | Call `openai/gpt-oss-120b` |
