from functools import lru_cache
from typing import Dict, Type

from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import get_settings
from app.llm.base import LLMProvider
from app.llm.providers.gemini import GeminiProvider

# Register additional providers here as you add them, e.g.:
# from app.llm.providers.anthropic import AnthropicProvider
# PROVIDERS["anthropic"] = AnthropicProvider
PROVIDERS: Dict[str, Type[LLMProvider]] = {
    "gemini": GeminiProvider,
}


@lru_cache
def get_llm() -> BaseChatModel:
    settings = get_settings()
    provider_name = settings.LLM_PROVIDER.lower()
    provider_cls = PROVIDERS.get(provider_name)
    if provider_cls is None:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider_name}'. "
            f"Available providers: {list(PROVIDERS.keys())}"
        )
    return provider_cls().get_chat_model()
