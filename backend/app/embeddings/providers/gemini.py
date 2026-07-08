from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import get_settings
from app.embeddings.base import EmbeddingsProvider


class GeminiEmbeddingsProvider(EmbeddingsProvider):
    def get_embeddings(self) -> Embeddings:
        settings = get_settings()
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your .env file "
                "(embeddings and chat share the same Gemini API key)."
            )
        return GoogleGenerativeAIEmbeddings(
            model=settings.GEMINI_EMBEDDINGS_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
        )
