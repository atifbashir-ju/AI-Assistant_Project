import { useEffect, useRef, useState } from "react";
import "./ChatInput.css";

const SpeechRecognitionAPI =
  typeof window !== "undefined" && (window.SpeechRecognition || window.webkitSpeechRecognition);

export default function ChatInput({ value, onChange, onSend, onStop, disabled, image, onImageChange }) {
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);
  const recognitionRef = useRef(null);
  const [isListening, setIsListening] = useState(false);

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if ((value.trim() || image) && !disabled) onSend();
    }
  }

  // Auto-resize: grow with content, up to a max height (CSS also caps it).
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [value]);

  function handleImageSelect(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result; // "data:image/png;base64,AAAA..."
      const [meta, base64] = dataUrl.split(",");
      const mimeType = meta.match(/data:(.*);base64/)?.[1] || file.type;
      onImageChange?.({ base64, mimeType, previewUrl: dataUrl, name: file.name });
    };
    reader.readAsDataURL(file);
    e.target.value = "";
  }

  function toggleVoiceInput() {
    if (!SpeechRecognitionAPI) return;

    if (isListening) {
      recognitionRef.current?.stop();
      return;
    }

    const recognition = new SpeechRecognitionAPI();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      onChange(value ? `${value} ${transcript}` : transcript);
    };
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognitionRef.current = recognition;
    recognition.start();
    setIsListening(true);
  }

  return (
    <div className="chat-input-wrapper">
      {image && (
        <div className="image-preview">
          <img src={image.previewUrl} alt="Attached" />
          <button className="image-preview-remove" onClick={() => onImageChange?.(null)} aria-label="Remove image">
            ×
          </button>
        </div>
      )}

      <div className="chat-input">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleImageSelect}
          accept="image/*"
          style={{ display: "none" }}
        />
        <button
          className="icon-btn"
          onClick={() => fileInputRef.current?.click()}
          aria-label="Attach image"
          title="Attach image"
          disabled={disabled}
        >
          📎
        </button>

        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Message the assistant…"
          rows={1}
          disabled={disabled}
        />

        {SpeechRecognitionAPI && (
          <button
            className={`icon-btn ${isListening ? "icon-btn--active" : ""}`}
            onClick={toggleVoiceInput}
            aria-label="Voice input"
            title="Voice input"
            disabled={disabled}
          >
            {isListening ? "●" : "🎤"}
          </button>
        )}

        {disabled ? (
          <button className="send-btn send-btn--stop" onClick={onStop} aria-label="Stop generating">
            ■
          </button>
        ) : (
          <button
            className="send-btn"
            onClick={onSend}
            disabled={!value.trim() && !image}
            aria-label="Send message"
          >
            →
          </button>
        )}
      </div>
    </div>
  );
}
