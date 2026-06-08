// src/components/SummaryPanel.jsx
// Displays the generated video summary and metadata

import React, { useState } from "react";

export default function SummaryPanel({ summary, videoId, chunkCount, transcriptPreview }) {
  const [showPreview, setShowPreview] = useState(false);

  return (
    <div className="summary-panel">
      <div className="summary-header">
        <h2>📋 Video Summary</h2>
        <div className="meta-badges">
          <span className="badge">🆔 {videoId}</span>
          <span className="badge">🧩 {chunkCount} chunks indexed</span>
        </div>
      </div>

      {/* Render markdown-style bullet points from the LLM */}
      <div className="summary-body">
        {summary.split("\n").map((line, i) => (
          <p key={i} className={line.startsWith("-") || line.startsWith("•") ? "bullet" : ""}>
            {line}
          </p>
        ))}
      </div>

      {/* Collapsible transcript preview */}
      <button
        className="toggle-preview"
        onClick={() => setShowPreview((v) => !v)}
      >
        {showPreview ? "Hide" : "Show"} transcript preview
      </button>

      {showPreview && (
        <div className="transcript-preview">
          <p>{transcriptPreview}</p>
        </div>
      )}
    </div>
  );
}
