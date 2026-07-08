from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings
from app.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    def get_chat_model(self) -> BaseChatModel:
        settings = get_settings()
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your .env file "
                "(see .env.example) or your hosting platform's environment variables."
            )
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=settings.GEMINI_TEMPERATURE,
            convert_system_message_to_human=False,
        )
