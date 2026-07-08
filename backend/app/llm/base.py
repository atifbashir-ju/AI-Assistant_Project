from abc import ABC, abstractmethod

from langchain_core.language_models.chat_models import BaseChatModel


class LLMProvider(ABC):
    """Every concrete provider wraps a LangChain-compatible chat model."""

    @abstractmethod
    def get_chat_model(self) -> BaseChatModel:
        """Return a configured LangChain chat model instance."""
        raise NotImplementedError
