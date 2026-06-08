// src/pages/App.jsx
// Root component — orchestrates the whole UI flow

import React, { useState } from "react";
import VideoInput from "../components/VideoInput";
import SummaryPanel from "../components/SummaryPanel";
import ChatInterface from "../components/ChatInterface";
import LoadingOverlay from "../components/LoadingOverlay";
import { processVideo } from "../services/api";
import "./App.css";

export default function App() {
  // null → not processed yet
  // { video_id, summary, transcript_preview, chunk_count } → done
  const [videoData, setVideoData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleVideoSubmit(url) {
    setError("");
    setVideoData(null);
    setIsLoading(true);

    try {
      const data = await processVideo(url);
      setVideoData(data);
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="app">
      {/* Show loading overlay while processing */}
      {isLoading && <LoadingOverlay />}

      {/* Header */}
      <header className="app-header">
        <div className="header-inner">
          <span className="logo-icon">▶</span>
          <h1 className="logo-text">YT Summarizer</h1>
          <p className="tagline">Summarize & chat with any YouTube video</p>
        </div>
      </header>

      <main className="app-main">
        {/* URL input — always visible */}
        <VideoInput onSubmit={handleVideoSubmit} isLoading={isLoading} />

        {/* Error banner */}
        {error && (
          <div className="error-banner" role="alert">
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Results — shown only after successful processing */}
        {videoData && !isLoading && (
          <div className="results-grid">
            <SummaryPanel
              summary={videoData.summary}
              videoId={videoData.video_id}
              chunkCount={videoData.chunk_count}
              transcriptPreview={videoData.transcript_preview}
            />
            <ChatInterface videoId={videoData.video_id} />
          </div>
        )}

        {/* Welcome state — shown before any video is processed */}
        {!videoData && !isLoading && !error && (
          <div className="welcome-state">
            <div className="welcome-icon">🎬</div>
            <h2>How it works</h2>
            <ol className="how-it-works">
              <li>Paste a YouTube link above</li>
              <li>We extract the transcript automatically</li>
              <li>An AI generates a structured summary</li>
              <li>Chat with the video using RAG</li>
            </ol>
          </div>
        )}
      </main>

      <footer className="app-footer">
        Built with FastAPI · LangChain · FAISS · HuggingFace · React
      </footer>
    </div>
  );
}
