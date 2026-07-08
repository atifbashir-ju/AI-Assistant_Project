from datetime import datetime, timezone

_sessions: dict[str, dict] = {}  # session_id -> {title, created_at, updated_at}

MAX_TITLE_LENGTH = 60


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def register_or_touch_session(session_id: str, first_message: str | None = None) -> None:
    """Call this on every chat turn. Creates the session on first call
    (using the first message as the title), and just bumps `updated_at`
    on subsequent calls."""
    existing = _sessions.get(session_id)
    if existing is None:
        title = (first_message or "New conversation").strip().replace("\n", " ")
        if len(title) > MAX_TITLE_LENGTH:
            title = title[:MAX_TITLE_LENGTH].rstrip() + "…"
        _sessions[session_id] = {
            "session_id": session_id,
            "title": title or "New conversation",
            "created_at": _now(),
            "updated_at": _now(),
        }
    else:
        existing["updated_at"] = _now()


def list_sessions() -> list[dict]:
    return sorted(_sessions.values(), key=lambda s: s["updated_at"], reverse=True)


def delete_session(session_id: str) -> bool:
    return _sessions.pop(session_id, None) is not None
