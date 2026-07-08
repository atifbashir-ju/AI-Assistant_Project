
from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """Search the public web for up-to-date information on a topic.

    Use this when the user asks about current events, recent facts, or
    anything that might have changed after your training data cutoff.

    Args:
        query: The search query.
    """
    try:
        from ddgs import DDGS
    except ImportError:
        return (
            "Web search is enabled but the `ddgs` package isn't installed. "
            "Run `pip install ddgs` and restart the server."
        )

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
    except Exception as exc:  # network errors, rate limits, etc.
        return f"Web search failed: {exc}"

    if not results:
        return "No web results found."

    formatted = []
    for r in results:
        title = r.get("title", "")
        body = r.get("body", "")
        href = r.get("href", "")
        formatted.append(f"- {title}: {body} ({href})")
    return "\n".join(formatted)
