import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./Message.css";

export default function Message({ role, content, isStreaming, toolEvents, image }) {
  const isUser = role === "user";
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  }

  return (
    <div className={`message ${isUser ? "message--user" : "message--assistant"}`}>
      {!isUser && <div className="message-rail" aria-hidden="true" />}
      <div className="message-body">
        {!isUser && (
          <div className="message-meta">
            <span className="message-author">assistant</span>
            {toolEvents?.length > 0 && (
              <span className="message-tool-trail">
                {toolEvents.map((t, i) => (
                  <span key={i} className="tool-chip">
                    {t}
                  </span>
                ))}
              </span>
            )}
          </div>
        )}

        {image && (
          <img src={image} alt="Attached" className="message-image" />
        )}

        <div className="message-content">
          {isUser ? (
            content
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          )}
          {isStreaming && <span className="cursor" aria-hidden="true" />}
        </div>
        {!isUser && content && !isStreaming && (
          <button className="copy-btn" onClick={handleCopy} aria-label="Copy message">
            {copied ? "copied" : "copy"}
          </button>
        )}
      </div>
    </div>
  );
}
