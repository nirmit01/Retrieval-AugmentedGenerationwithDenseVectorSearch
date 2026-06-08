// src/components/VideoInput.jsx
// URL input bar + submit button

import React, { useState } from "react";

export default function VideoInput({ onSubmit, isLoading }) {
  const [url, setUrl] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (!url.trim()) return;
    onSubmit(url.trim());
  }

  return (
    <div className="video-input-wrapper">
      <form onSubmit={handleSubmit} className="video-input-form">
        <div className="input-row">
          {/* YouTube icon */}
          <span className="yt-icon" aria-hidden="true">▶</span>

          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste a YouTube URL…  e.g. https://youtube.com/watch?v=..."
            className="url-input"
            disabled={isLoading}
            aria-label="YouTube video URL"
          />

          <button
            type="submit"
            className="process-btn"
            disabled={isLoading || !url.trim()}
          >
            {isLoading ? (
              <span className="spinner" aria-label="Loading…" />
            ) : (
              "Summarize"
            )}
          </button>
        </div>
      </form>

      <p className="input-hint">
        Paste any YouTube link — we'll transcribe it, summarise it, and let you
        chat with the content.
      </p>
    </div>
  );
}
