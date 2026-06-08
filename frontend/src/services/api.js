// src/services/api.js
// All API calls to the FastAPI backend live here

const BASE_URL = import.meta.env.VITE_API_URL || "";

/**
 * Process a YouTube video — fetches transcript, builds vector store, generates summary.
 * @param {string} url - Full YouTube URL
 * @returns {Promise<{video_id, summary, transcript_preview, chunk_count}>}
 */
export async function processVideo(url) {
  const response = await fetch(`http://localhost:8000/process_video`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  const data = await response.json();

  if (!response.ok) {
    // Backend returns { detail: "..." } on errors
    throw new Error(data.detail || "Failed to process video.");
  }

  return data;
}

/**
 * Ask a question about an already-processed video (RAG).
 * @param {string} videoId - The video ID returned by processVideo
 * @param {string} question - User's question
 * @returns {Promise<{answer, video_id}>}
 */
export async function askQuestion(videoId, question) {
  const response = await fetch(`http://localhost:8000/ask_question`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ video_id: videoId, question }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to get an answer.");
  }

  return data;
}
