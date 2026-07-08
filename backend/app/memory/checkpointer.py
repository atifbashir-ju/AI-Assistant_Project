from functools import lru_cache

from langgraph.checkpoint.base import BaseCheckpointSaver

from app.core.config import get_settings


@lru_cache
def get_checkpointer() -> BaseCheckpointSaver:
    settings = get_settings()
    backend = settings.CHECKPOINTER_BACKEND.lower()

    if backend == "sqlite":
        import sqlite3

        from langgraph.checkpoint.sqlite import SqliteSaver

        conn = sqlite3.connect(settings.SQLITE_CHECKPOINT_PATH, check_same_thread=False)
        return SqliteSaver(conn)

    if backend == "memory":
        from langgraph.checkpoint.memory import MemorySaver

        return MemorySaver()

    raise ValueError(
        f"Unknown CHECKPOINTER_BACKEND '{backend}'. Use 'memory' or 'sqlite'."
    )
