# app.py
# FastAPI backend — exposes /process_video and /ask_question endpoints

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from transcript import get_transcript_from_url
from rag_pipeline import build_vector_store, generate_summary, answer_question, get_vector_store
from utils import is_valid_youtube_url

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="YouTube Video Summarizer API",
    description="Process YouTube videos, generate summaries, and answer questions via RAG.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS — allow the React frontend to call this API
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ProcessVideoRequest(BaseModel):
    url: str  # Full YouTube URL


class ProcessVideoResponse(BaseModel):
    video_id: str
    summary: str
    transcript_preview: str  # First 300 chars of the transcript
    chunk_count: int


class AskQuestionRequest(BaseModel):
    video_id: str
    question: str


class AskQuestionResponse(BaseModel):
    answer: str
    video_id: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "YouTube Summarizer API is running."}


@app.post("/process_video", response_model=ProcessVideoResponse)
def process_video(req: ProcessVideoRequest):
    """
    Main processing endpoint:
    1. Validate the YouTube URL
    2. Fetch the transcript
    3. Build FAISS vector store (for RAG)
    4. Generate a summary
    5. Return everything to the frontend
    """
    url = req.url.strip()

    # Step 1 — Validate URL format
    if not is_valid_youtube_url(url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL format.")

    # Step 2 — Fetch transcript
    try:
        video_id, transcript = get_transcript_from_url(url)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if not transcript or len(transcript) < 50:
        raise HTTPException(status_code=422, detail="Transcript is too short or empty.")

    # Step 3 — Build vector store (chunking + embedding)
    try:
        vector_store = build_vector_store(video_id, transcript)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build vector store: {str(e)}")

    # Step 4 — Generate summary
    try:
        summary = generate_summary(transcript)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

    # Count the chunks that were created
    chunk_count = vector_store.index.ntotal

    return ProcessVideoResponse(
        video_id=video_id,
        summary=summary,
        transcript_preview=transcript[:300] + ("..." if len(transcript) > 300 else ""),
        chunk_count=chunk_count,
    )


@app.post("/ask_question", response_model=AskQuestionResponse)
def ask_question(req: AskQuestionRequest):
    """
    RAG Q&A endpoint:
    1. Check that the video has already been processed
    2. Embed the question and retrieve relevant transcript chunks
    3. Pass context + question to the LLM
    4. Return the answer
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Ensure the video has been processed (vector store exists)
    if get_vector_store(req.video_id) is None:
        raise HTTPException(
            status_code=404,
            detail=f"Video '{req.video_id}' has not been processed. Call /process_video first.",
        )

    try:
        answer = answer_question(req.video_id, req.question)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {str(e)}")

    return AskQuestionResponse(answer=answer, video_id=req.video_id)


# ---------------------------------------------------------------------------
# Run locally with:  uvicorn app:app --reload --port 8000
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
