/**
 * Thin client for the backend's chat API.
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function streamChat({
  message,
  sessionId,
  imageBase64,
  imageMimeType,
  signal,
  onSession,
  onToken,
  onToolStart,
  onToolEnd,
  onDone,
  onError,
}) {
  const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      image_base64: imageBase64 || undefined,
      image_mime_type: imageMimeType || undefined,
    }),
    signal,
  });

  if (!response.ok || !response.body) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) detail = errJson.detail;
    } catch {
      // response wasn't JSON; keep the generic message
    }
    onError?.(detail);
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const rawEvents = buffer.split("\n\n");
    buffer = rawEvents.pop();

    for (const rawEvent of rawEvents) {
      const lines = rawEvent.split("\n");
      let eventName = "message";
      let dataStr = "";
      for (const line of lines) {
        if (line.startsWith("event:")) eventName = line.slice(6).trim();
        if (line.startsWith("data:")) dataStr += line.slice(5).trim();
      }
      if (!dataStr) continue;

      let data;
      try {
        data = JSON.parse(dataStr);
      } catch {
        continue;
      }

      switch (eventName) {
        case "session":
          onSession?.(data.session_id);
          break;
        case "token":
          onToken?.(data.text);
          break;
        case "tool_start":
          onToolStart?.(data.tool);
          break;
        case "tool_end":
          onToolEnd?.(data.tool);
          break;
        case "done":
          onDone?.();
          break;
        case "error":
          onError?.(data.message);
          break;
        default:
          break;
      }
    }
  }
}

export async function fetchHealth() {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) throw new Error("Health check failed");
  return response.json();
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
    method: "POST",
    body: formData,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Upload failed");
  }
  return data;
}

export async function fetchDocuments() {
  const response = await fetch(`${API_BASE_URL}/api/documents`);
  if (!response.ok) throw new Error("Failed to fetch documents");
  return response.json();
}

export async function fetchSessions() {
  const response = await fetch(`${API_BASE_URL}/api/sessions`);
  if (!response.ok) throw new Error("Failed to fetch sessions");
  return response.json();
}

export async function fetchSessionMessages(sessionId) {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/messages`);
  if (!response.ok) throw new Error("Failed to load conversation");
  return response.json();
}

export async function deleteSession(sessionId) {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`, { method: "DELETE" });
  if (!response.ok) throw new Error("Failed to delete session");
  return response.json();
}

export async function fetchSuggestions(sessionId) {
  const response = await fetch(`${API_BASE_URL}/api/chat/suggestions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
  if (!response.ok) return { suggestions: [] };
  return response.json();
}
