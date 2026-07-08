import logging

logger = logging.getLogger("app.errors")


def friendly_error_message(exc: Exception) -> str:
    logger.exception("Agent error")  # full traceback in the server console

    text = str(exc).lower()

    if "api key not valid" in text or "api_key_invalid" in text or "permission" in text and "denied" in text:
        return "Your Gemini API key looks invalid. Double-check GEMINI_API_KEY in backend/.env."

    if "quota" in text or "resource_exhausted" in text or "rate limit" in text:
        return "You've hit Gemini's rate limit or quota. Wait a moment and try again."

    if "not found" in text and "model" in text:
        return "The configured Gemini model wasn't found. Check GEMINI_MODEL in backend/.env."

    if any(k in text for k in ("connection", "timeout", "network", "dns", "unreachable")):
        return "Couldn't reach Gemini's servers. Check your internet connection and try again."

    if "gemini_api_key is not set" in text:
        return "GEMINI_API_KEY is missing. Add it to backend/.env and restart the backend."

    # Fallback: still short, but not a scary raw stack trace.
    return "Something went wrong generating a response. Check the backend terminal for details."
