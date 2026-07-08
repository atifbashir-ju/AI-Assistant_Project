from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, documents, health, sessions
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="A modular, LangGraph-powered AI assistant backend.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(sessions.router)


@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} API is running. See /docs for the API reference."}
