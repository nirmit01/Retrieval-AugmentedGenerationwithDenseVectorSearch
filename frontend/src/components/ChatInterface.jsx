// src/components/ChatInterface.jsx
// ChatGPT-style chat panel for asking questions about the video

import React, { useState, useRef, useEffect } from "react";
import { askQuestion } from "../services/api";

// Individual chat bubble
function Message({ role, text }) {
  const isUser = role === "user";
  return (
    <div className={`message ${isUser ? "user-msg" : "ai-msg"}`}>
      <span className="msg-avatar">{isUser ? "🧑" : "🤖"}</span>
      <div className="msg-bubble">
        {text.split("\n").map((line, i) => (
          <p key={i}>{line}</p>
        ))}
      </div>
    </div>
  );
}

// Animated typing indicator while waiting for AI answer
function TypingIndicator() {
  return (
    <div className="message ai-msg">
      <span className="msg-avatar">🤖</span>
      <div className="msg-bubble typing-indicator">
        <span /><span /><span />
      </div>
    </div>
  );
}

export default function ChatInterface({ videoId }) {
  const [messages, setMessages] = useState([
    {
      role: "ai",
      text: "Hi! I've processed the video. Ask me anything about it — key topics, specific facts, quotes, and more.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  // Auto-scroll to the latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  async function handleSend(e) {
    e.preventDefault();
    const question = input.trim();
    if (!question || isThinking) return;

    setInput("");
    setError("");
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setIsThinking(true);

    try {
      const { answer } = await askQuestion(videoId, question);
      setMessages((prev) => [...prev, { role: "ai", text: answer }]);
    } catch (err) {
      setError(err.message);
      setMessages((prev) => [
        ...prev,
        { role: "ai", text: `⚠️ Sorry, I couldn't answer that. (${err.message})` },
      ]);
    } finally {
      setIsThinking(false);
    }
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>💬 Chat with the Video</h2>
        <span className="chat-hint">Powered by RAG + HuggingFace LLM</span>
      </div>

      {/* Message list */}
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <Message key={i} role={msg.role} text={msg.text} />
        ))}
        {isThinking && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <form onSubmit={handleSend} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about the video…"
          className="chat-input"
          disabled={isThinking}
          aria-label="Your question"
        />
        <button
          type="submit"
          className="send-btn"
          disabled={isThinking || !input.trim()}
          aria-label="Send"
        >
          {isThinking ? <span className="spinner" /> : "Send ➤"}
        </button>
      </form>

      {error && <p className="error-text">{error}</p>}
    </div>
  );
}
