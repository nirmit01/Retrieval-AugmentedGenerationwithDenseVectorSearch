// src/components/LoadingOverlay.jsx
// Full-screen loading state while video is being processed

import React from "react";

const STEPS = [
  "🔗 Fetching transcript…",
  "✂️  Chunking text…",
  "🧠 Building embeddings…",
  "📝 Generating summary…",
];

export default function LoadingOverlay() {
  return (
    <div className="loading-overlay">
      <div className="loading-card">
        <div className="big-spinner" aria-hidden="true" />
        <h3>Processing your video</h3>
        <p>This may take 20–60 seconds on first run.</p>
        <ul className="step-list">
          {STEPS.map((step, i) => (
            <li key={i} className="step-item">
              {step}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
