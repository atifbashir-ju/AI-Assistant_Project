from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- General app settings -------------------------------------------------
    APP_NAME: str = "AI Assistant"
    ENVIRONMENT: str = Field(default="development")  # development | production
    LOG_LEVEL: str = "INFO"

    # Comma-separated list of allowed CORS origins, e.g.
    # "http://localhost:5173,https://myapp.vercel.app"
    CORS_ORIGINS: str = "http://localhost:5173"

    # ---- LLM provider -----------------------------------------------------------
    # Which chat model provider to use. Adding a new provider = add a class in
    # app/llm/providers/ and register it in app/llm/factory.py.
    LLM_PROVIDER: str = "gemini"

    # Gemini / Google Generative AI
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_TEMPERATURE: float = 0.7

    # ---- Embeddings provider ----------------------------------------------------
    # Independent of LLM_PROVIDER so you can e.g. chat with Gemini but embed
    # with OpenAI, or vice versa. Add new providers in app/embeddings/providers/.
    EMBEDDINGS_PROVIDER: str = "gemini"

    GEMINI_EMBEDDINGS_MODEL: str = "models/text-embedding-004"

    # Placeholder for future providers (OpenAI, Voyage, Cohere, local, ...)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_EMBEDDINGS_MODEL: str = "text-embedding-3-small"
    VOYAGE_API_KEY: Optional[str] = None
    VOYAGE_EMBEDDINGS_MODEL: str = "voyage-3"

    # ---- Feature flags ------------------------------------------------------
    # Toggle optional agent tools without touching code.
    ENABLE_WEB_SEARCH_TOOL: bool = False
    ENABLE_RAG_TOOL: bool = False

    # ---- Memory / persistence ------------------------------------------------
    # "memory" = in-process only (resets on restart), fine for local dev.
    # "sqlite" = persisted to a local file, survives restarts.
    CHECKPOINTER_BACKEND: str = "memory"
    SQLITE_CHECKPOINT_PATH: str = "./checkpoints.sqlite"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor. Import and call this rather than
    instantiating Settings() directly, so the .env file is only parsed once."""
    return Settings()
