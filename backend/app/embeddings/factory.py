from functools import lru_cache
from typing import Dict, Type

from langchain_core.embeddings import Embeddings

from app.core.config import get_settings
from app.embeddings.base import EmbeddingsProvider
from app.embeddings.providers.gemini import GeminiEmbeddingsProvider

# Register additional providers here as you add them, e.g.:
# from app.embeddings.providers.openai import OpenAIEmbeddingsProvider
# PROVIDERS["openai"] = OpenAIEmbeddingsProvider
# from app.embeddings.providers.voyage import VoyageEmbeddingsProvider
# PROVIDERS["voyage"] = VoyageEmbeddingsProvider
PROVIDERS: Dict[str, Type[EmbeddingsProvider]] = {
    "gemini": GeminiEmbeddingsProvider,
}


@lru_cache
def get_embeddings() -> Embeddings:
    settings = get_settings()
    provider_name = settings.EMBEDDINGS_PROVIDER.lower()
    provider_cls = PROVIDERS.get(provider_name)
    if provider_cls is None:
        raise ValueError(
            f"Unknown EMBEDDINGS_PROVIDER '{provider_name}'. "
            f"Available providers: {list(PROVIDERS.keys())}"
        )
    return provider_cls().get_embeddings()
