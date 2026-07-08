import { useEffect, useRef, useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import Message from "./components/Message.jsx";
import ChatInput from "./components/ChatInput.jsx";
import {
  streamChat,
  fetchHealth,
  fetchDocuments,
  fetchSessions,
  fetchSessionMessages,
  fetchSuggestions,
} from "./api/chatApi.js";
import { useTheme } from "./hooks/useTheme.js";
import { exportAsText, exportAsPDF } from "./utils/export.js";
import "./App.css";

export default function App() {
  const { theme, toggleTheme } = useTheme();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [attachedImage, setAttachedImage] = useState(null); // { base64, mimeType, previewUrl, name }
  const [sessionId, setSessionId] = useState(null);
  const [health, setHealth] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [activeTool, setActiveTool] = useState(null);
  const [errorBanner, setErrorBanner] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const scrollRef = useRef(null);
  const abortControllerRef = useRef(null);
  const lastUserMessageRef = useRef(null);

  function refreshDocuments() {
    fetchDocuments()
      .then((data) => setDocuments(data.sources || []))
      .catch(() => {});
  }

  function refreshSessions() {
    fetchSessions()
      .then((data) => setSessions(data.sessions || []))
      .catch(() => {});
  }

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch(() => setErrorBanner({ message: "Couldn't reach the backend. Confirm it's running." }));
    refreshDocuments();
    refreshSessions();
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isThinking]);

  function handleNewSession() {
    abortControllerRef.current?.abort();
    setSessionId(null);
    setMessages([]);
    setErrorBanner(null);
    setSuggestions([]);
    setSidebarOpen(false);
  }

  async function handleSelectSession(id) {
    if (id === sessionId) {
      setSidebarOpen(false);
      return;
    }
    abortControllerRef.current?.abort();
    setErrorBanner(null);
    setSuggestions([]);
    setSidebarOpen(false);
    try {
      const data = await fetchSessionMessages(id);
      setSessionId(id);
      setMessages(data.messages || []);
    } catch (err) {
      setErrorBanner({ message: "Couldn't load that conversation." });
    }
  }

  function handleSessionDeleted(deletedId) {
    setSessions((prev) => prev.filter((s) => s.session_id !== deletedId));
    if (deletedId === sessionId) handleNewSession();
  }

  async function sendMessage(text, image) {
    if ((!text && !image) || isStreaming) return;

    lastUserMessageRef.current = text;
    setErrorBanner(null);
    setSuggestions([]);
    const userMessage = { role: "user", content: text, image: image?.previewUrl };
    const assistantIndex = messages.length + 1;
    setMessages((prev) => [...prev, userMessage, { role: "assistant", content: "", toolEvents: [] }]);
    setIsStreaming(true);
    setIsThinking(true);

    const controller = new AbortController();
    abortControllerRef.current = controller;
    let accumulated = "";

    try {
      await streamChat({
        message: text,
        sessionId,
        imageBase64: image?.base64,
        imageMimeType: image?.mimeType,
        signal: controller.signal,
        onSession: (id) => {
          setSessionId((prev) => prev || id);
        },
        onToken: (chunk) => {
          setIsThinking(false);
          accumulated += chunk;
          setMessages((prev) => {
            const next = [...prev];
            next[assistantIndex] = { ...next[assistantIndex], content: accumulated };
            return next;
          });
        },
        onToolStart: (tool) => {
          setActiveTool(tool);
          setMessages((prev) => {
            const next = [...prev];
            const existing = next[assistantIndex].toolEvents || [];
            next[assistantIndex] = { ...next[assistantIndex], toolEvents: [...existing, tool] };
            return next;
          });
        },
        onToolEnd: () => setActiveTool(null),
        onDone: () => {
          refreshSessions();
        },
        onError: (msg) => {
          setErrorBanner({ message: msg, retryText: text });
          setMessages((prev) => {
            if (prev[assistantIndex] && !prev[assistantIndex].content) {
              return prev.slice(0, assistantIndex);
            }
            return prev;
          });
        },
      });
    } catch (err) {
      if (err?.name !== "AbortError") {
        setErrorBanner({ message: "Lost connection to the backend.", retryText: text });
      }
    } finally {
      setIsStreaming(false);
      setIsThinking(false);
      setActiveTool(null);
      abortControllerRef.current = null;
      refreshSessions();

      // Best-effort suggested follow-ups, fire-and-forget.
      setTimeout(() => {
        const currentSession = sessionId;
        if (currentSession) {
          fetchSuggestions(currentSession)
            .then((data) => setSuggestions(data.suggestions || []))
            .catch(() => {});
        }
      }, 300);
    }
  }

  function handleSend() {
    const text = input.trim();
    if (!text && !attachedImage) return;
    setInput("");
    const image = attachedImage;
    setAttachedImage(null);
    sendMessage(text, image);
  }

  function handleStop() {
    abortControllerRef.current?.abort();
  }

  function handleRetry() {
    const text = errorBanner?.retryText || lastUserMessageRef.current;
    setErrorBanner(null);
    if (text) sendMessage(text, null);
  }

  function handleSuggestionClick(suggestion) {
    setSuggestions([]);
    sendMessage(suggestion, null);
  }

  return (
    <div className="app">
      <Sidebar
        health={health}
        sessionId={sessionId}
        onNewSession={handleNewSession}
        activeTool={activeTool}
        documents={documents}
        onDocumentUploaded={refreshDocuments}
        sessions={sessions}
        onSelectSession={handleSelectSession}
        onSessionDeleted={handleSessionDeleted}
        theme={theme}
        onToggleTheme={toggleTheme}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <main className="chat-column">
        <div className="chat-topbar no-print">
          <button className="hamburger-btn" onClick={() => setSidebarOpen(true)} aria-label="Open menu">
            ☰
          </button>
          <div className="chat-topbar-spacer" />
          {messages.length > 0 && (
            <div className="export-buttons">
              <button onClick={() => exportAsText(messages, "Conversation")} title="Export as text">
                Export .txt
              </button>
              <button onClick={exportAsPDF} title="Export as PDF (print dialog)">
                Export PDF
              </button>
            </div>
          )}
        </div>

        <div className="chat-scroll" ref={scrollRef}>
          {messages.length === 0 && (
            <div className="empty-state">
              <div className="empty-mark">/&gt;_</div>
              <h1>Ask me anything.</h1>
              <p>
                General-purpose for now — connect a knowledge base or web search
                in the backend config when you're ready to extend it.
              </p>
            </div>
          )}

          {messages.map((m, i) => (
            <Message
              key={i}
              role={m.role}
              content={m.content}
              image={m.image}
              toolEvents={m.toolEvents}
              isStreaming={isStreaming && i === messages.length - 1 && m.role === "assistant"}
            />
          ))}

          {isThinking && (
            <div className="thinking-row">
              <span className="thinking-dot" />
              <span className="thinking-dot" />
              <span className="thinking-dot" />
            </div>
          )}

          {!isStreaming && suggestions.length > 0 && (
            <div className="suggestions-row no-print">
              {suggestions.map((s, i) => (
                <button key={i} className="suggestion-chip" onClick={() => handleSuggestionClick(s)}>
                  {s}
                </button>
              ))}
            </div>
          )}

          {errorBanner && (
            <div className="error-banner">
              <span>{errorBanner.message}</span>
              <div className="error-banner-actions">
                {errorBanner.retryText && (
                  <button onClick={handleRetry} className="error-retry-btn">
                    Retry
                  </button>
                )}
                <button onClick={() => setErrorBanner(null)} className="error-dismiss-btn" aria-label="Dismiss">
                  ×
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="chat-input-row no-print">
          <ChatInput
            value={input}
            onChange={setInput}
            onSend={handleSend}
            onStop={handleStop}
            disabled={isStreaming}
            image={attachedImage}
            onImageChange={setAttachedImage}
          />
        </div>
      </main>
    </div>
  );
}
