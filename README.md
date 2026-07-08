# AI Assistant

A modular, general-purpose AI assistant: **FastAPI + LangGraph** backend
(Google Gemini as the LLM), **React** frontend, streaming responses, and a
clean structure for bolting on RAG, web search, memory, and file uploads
later without a rewrite.

```
ai-assistant/
├── backend/          FastAPI + LangGraph app
│   └── app/
│       ├── core/         settings (all env vars live here)
│       ├── llm/           LLM provider abstraction (Gemini today, swappable)
│       ├── embeddings/    embeddings provider abstraction (for RAG later)
│       ├── agent/         the LangGraph graph + tool registry
│       │   └── tools/     individual tools (web_search, rag_search, ...)
│       ├── rag/           vector store scaffold (empty until you add docs)
│       ├── memory/        conversation memory (LangGraph checkpointer)
│       ├── api/routes/    HTTP endpoints
│       └── main.py        FastAPI app entrypoint
└── frontend/          React (Vite) chat UI
    └── src/
        ├── components/    Sidebar, Message, ChatInput
        ├── api/           SSE streaming client
        └── App.jsx
```

## How it works

- The backend exposes a LangGraph agent: `agent` node calls Gemini, and if
  the model requests a tool, a `tools` node runs it and loops back. Today no
  tools are registered by default, so it behaves as a plain chatbot until you
  flip a feature flag.
- Conversation memory is handled by a LangGraph checkpointer keyed on
  `session_id` — the frontend generates one per conversation and the backend
  remembers everything under that id, no manual history management needed.
- The frontend talks to `/api/chat/stream` (Server-Sent Events) and renders
  tokens as they arrive, plus shows which tool is firing in real time.

## Features

- Streaming chat with Gemini, tool-calling agent loop (LangGraph)
- Conversation memory per session
- Chat history sidebar — browse and reopen past conversations, delete old ones
- Markdown rendering (bold, lists, code blocks, tables, links)
- Web search tool (free, DuckDuckGo, opt-in via env flag)
- RAG: upload .txt/.md/.pdf documents from the sidebar, assistant searches them
- Image/vision input — attach a photo and ask about it (Gemini vision)
- Voice input (browser Speech Recognition, Chrome/Edge)
- Suggested follow-up questions after each reply
- Export a conversation as .txt or PDF (via print dialog)
- Dark/light theme toggle
- Mobile-responsive layout (sidebar becomes a slide-out drawer)
- Stop-generating button, retry-on-error, copy-to-clipboard on replies
- Friendly error messages instead of raw stack traces

## 1. Run the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set GEMINI_API_KEY (get one free at https://aistudio.google.com/app/apikey)

uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` to confirm it's up and try the API directly.
Visit `http://localhost:8000/api/health` for a quick status check.

## 2. Run the frontend

```bash
cd frontend
npm install
cp .env.example .env    # defaults to http://localhost:8000, adjust if needed
npm run dev
```

Visit `http://localhost:5173`.

## Extending it

**Turn on web search** (free, no API key, via DuckDuckGo):
Set `ENABLE_WEB_SEARCH_TOOL=true` in `backend/.env` and restart the backend.
Swap in Tavily/SerpAPI/Bing later by editing `app/agent/tools/web_search.py` —
the tool interface stays the same.

**Add RAG (your own documents) — already wired up:**
1. Start both servers, open the app, and use **"+ Upload document"** in the
   sidebar (.txt, .md, or .pdf). It chunks the file, embeds it, and stores it
   in the vector store.
2. Set `ENABLE_RAG_TOOL=true` in `backend/.env` and restart the backend.
3. Ask the assistant something about the document's contents — it'll call
   `search_knowledge_base` automatically when relevant.

Note: the default store (`InMemoryVectorStore`) resets when the backend
restarts. For production, swap it out in `app/rag/store.py` for a persistent
store (Chroma, pgvector, Pinecone) — nothing else in the app needs to change.

**Add memory that persists across restarts:**
Set `CHECKPOINTER_BACKEND=sqlite` in `.env` (uncomment
`langgraph-checkpoint-sqlite` in `requirements.txt` first). For multi-instance
production deployments, use `PostgresSaver` or `RedisSaver` instead — only
`app/memory/checkpointer.py` needs to change.

**Add file uploads:**
Add a route under `app/api/routes/`, save/parse the file, and either feed
extracted text straight into the conversation or into the RAG store above.

**Add a new tool of any kind:**
Write a `@tool`-decorated function in `app/agent/tools/`, register it in
`app/agent/tools/registry.py` behind a feature flag. Nothing else in the
graph needs to change.

**Switch LLM or embeddings provider:**
Add a class in `app/llm/providers/` (or `app/embeddings/providers/`)
implementing the base interface, register it in the corresponding
`factory.py`, then just change `LLM_PROVIDER` / `EMBEDDINGS_PROVIDER` in `.env`.

## 3. Deploy it so others can use it

**Backend** — any Python host works (Railway, Render, Fly.io, a VPS). General shape:
1. Push `backend/` to a GitHub repo (or deploy directly).
2. Set the start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Set environment variables in the platform's dashboard: `GEMINI_API_KEY`,
   `CORS_ORIGINS` (your deployed frontend URL), and any others from `.env.example`.

**Frontend** — Vercel or Netlify are the easiest for a Vite app:
1. Push `frontend/` to a GitHub repo (or deploy directly).
2. Build command: `npm run build`, output directory: `dist`.
3. Set `VITE_API_BASE_URL` to your deployed backend's URL.

Once both are deployed, update `CORS_ORIGINS` on the backend to match your
actual frontend domain, and you're live.

## Notes

- Get a Gemini API key at https://aistudio.google.com/app/apikey — it has a
  generous free tier, good for getting started.
- Model names are configurable (`GEMINI_MODEL` in `.env`) since Google
  updates its lineup fairly often — check
  https://ai.google.dev/gemini-api/docs/models for the current list if the
  default stops working.
