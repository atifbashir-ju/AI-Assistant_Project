
from functools import lru_cache

from langchain_core.vectorstores import InMemoryVectorStore

from app.embeddings.factory import get_embeddings


@lru_cache
def get_vectorstore() -> InMemoryVectorStore:
    """Returns a process-wide singleton vector store.

    NOTE: in-memory means data is lost on server restart. Fine for
    prototyping; replace with a persistent store before relying on it.
    """
    return InMemoryVectorStore(embedding=get_embeddings())


# Lightweight registry of what's been ingested, purely for the "what's in my
# knowledge base?" UI/endpoint. The vector store itself doesn't need this to
# function — it's just bookkeeping since InMemoryVectorStore doesn't expose
# an easy "list distinct sources" query.
_ingested_sources: dict[str, int] = {}  # filename -> chunk count


def register_ingested_source(filename: str, chunk_count: int) -> None:
    _ingested_sources[filename] = _ingested_sources.get(filename, 0) + chunk_count


def list_ingested_sources() -> list[dict]:
    return [{"source": name, "chunks": count} for name, count in _ingested_sources.items()]
