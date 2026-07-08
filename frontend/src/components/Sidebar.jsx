import { useRef, useState } from "react";
import { uploadDocument, deleteSession } from "../api/chatApi.js";
import "./Sidebar.css";

export default function Sidebar({
  health,
  sessionId,
  onNewSession,
  activeTool,
  documents,
  onDocumentUploaded,
  sessions,
  onSelectSession,
  onSessionDeleted,
  theme,
  onToggleTheme,
  isOpen,
  onClose,
}) {
  const tools = health?.tools_enabled || {};
  const fileInputRef = useRef(null);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploading, setUploading] = useState(false);

  async function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadStatus(null);
    try {
      const result = await uploadDocument(file);
      setUploadStatus({ type: "success", message: `Added ${result.chunks_added} chunks from ${result.filename}` });
      onDocumentUploaded?.();
    } catch (err) {
      setUploadStatus({ type: "error", message: err.message });
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleDeleteSession(e, id) {
    e.stopPropagation();
    try {
      await deleteSession(id);
      onSessionDeleted?.(id);
    } catch {
      // best-effort; ignore failures here
    }
  }

  return (
    <>
      {isOpen && <div className="sidebar-scrim" onClick={onClose} />}
      <aside className={`sidebar ${isOpen ? "sidebar--open" : ""}`}>
        <div className="sidebar-header">
          <div className="sidebar-mark">/&gt;_</div>
          <div className="sidebar-header-text">
            <div className="sidebar-title">{health?.app_name || "Assistant"}</div>
            <div className="sidebar-subtitle">
              {health ? health.llm_provider : "connecting…"}
            </div>
          </div>
          <button className="theme-toggle" onClick={onToggleTheme} aria-label="Toggle theme" title="Toggle theme">
            {theme === "dark" ? "☀" : "☾"}
          </button>
          <button className="sidebar-close" onClick={onClose} aria-label="Close sidebar">
            ×
          </button>
        </div>

        <button className="new-session-btn" onClick={onNewSession}>
          + New conversation
        </button>

        {sessions?.length > 0 && (
          <div className="sidebar-section">
            <div className="sidebar-section-label">History</div>
            <ul className="history-list">
              {sessions.map((s) => (
                <li
                  key={s.session_id}
                  className={`history-item ${s.session_id === sessionId ? "history-item--active" : ""}`}
                  onClick={() => onSelectSession?.(s.session_id)}
                  title={s.title}
                >
                  <span className="history-item-title">{s.title}</span>
                  <button
                    className="history-item-delete"
                    onClick={(e) => handleDeleteSession(e, s.session_id)}
                    aria-label="Delete conversation"
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="sidebar-section">
          <div className="sidebar-section-label">Tools</div>
          <ToolStatus label="Web search" enabled={!!tools.web_search} active={activeTool === "web_search"} />
          <ToolStatus label="Knowledge base" enabled={!!tools.rag} active={activeTool === "search_knowledge_base"} />
          <ToolStatus label="Memory" enabled={true} active={false} note="always on" />
        </div>

        <div className="sidebar-section">
          <div className="sidebar-section-label">Knowledge base</div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".txt,.md,.pdf"
            style={{ display: "none" }}
          />
          <button
            className="upload-btn"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            {uploading ? "Uploading…" : "+ Upload document"}
          </button>

          {uploadStatus && (
            <div className={`upload-status upload-status--${uploadStatus.type}`}>
              {uploadStatus.message}
            </div>
          )}

          {documents?.length > 0 ? (
            <ul className="doc-list">
              {documents.map((d) => (
                <li key={d.source} title={d.source}>
                  {d.source} <span className="doc-chunks">· {d.chunks}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="doc-empty">No documents yet</div>
          )}

          {!tools.rag && documents?.length > 0 && (
            <div className="doc-hint">
              Set <code>ENABLE_RAG_TOOL=true</code> in backend/.env and restart to let the assistant use these.
            </div>
          )}
        </div>

        <div className="sidebar-footer">
          Add more tools in{" "}
          <code>backend/app/agent/tools/</code>
        </div>
      </aside>
    </>
  );
}

function ToolStatus({ label, enabled, active, note }) {
  return (
    <div className={`tool-row ${enabled ? "" : "tool-row--disabled"}`}>
      <span className={`tool-dot ${active ? "tool-dot--active" : ""} ${enabled ? "" : "tool-dot--off"}`} />
      <span className="tool-label">{label}</span>
      {note && <span className="tool-note">{note}</span>}
      {!enabled && !note && <span className="tool-note">off</span>}
    </div>
  );
}
