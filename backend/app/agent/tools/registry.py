
from langchain_core.tools import BaseTool

from app.core.config import get_settings


def get_active_tools() -> list[BaseTool]:
    settings = get_settings()
    tools: list[BaseTool] = []

    if settings.ENABLE_WEB_SEARCH_TOOL:
        from app.agent.tools.web_search import web_search

        tools.append(web_search)

    if settings.ENABLE_RAG_TOOL:
        from app.agent.tools.rag_search import search_knowledge_base

        tools.append(search_knowledge_base)

    # Add future tools here, e.g.:
    # if settings.ENABLE_CALCULATOR_TOOL:
    #     from app.agent.tools.calculator import calculator
    #     tools.append(calculator)

    return tools
