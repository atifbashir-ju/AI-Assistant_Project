from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health():
    settings = get_settings()
    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
        "embeddings_provider": settings.EMBEDDINGS_PROVIDER,
        "tools_enabled": {
            "web_search": settings.ENABLE_WEB_SEARCH_TOOL,
            "rag": settings.ENABLE_RAG_TOOL,
        },
    }
