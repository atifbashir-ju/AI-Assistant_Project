"""
RAG retrieval tool — scaffolded for when you add custom knowledge sources.

Disabled by default — set ENABLE_RAG_TOOL=true in .env to turn it on.

Currently backed by the in-memory vector store in app/rag/store.py, which
starts empty. To make this useful:
  1. Add a document ingestion path (e.g. a file upload endpoint that calls
     `rag_store.add_texts(...)`), or a startup script that indexes a folder.
  2. Flip ENABLE_RAG_TOOL=true.

The tool itself doesn't need to change as you swap in a real vector
database (Chroma, Pinecone, Weaviate, pgvector, ...) later — just change
what app/rag/store.py returns from get_vectorstore().
"""
from langchain_core.tools import tool

from app.rag.store import get_vectorstore


@tool
def search_knowledge_base(query: str) -> str:
    """Search the custom knowledge base for information relevant to the query.

    Use this when the user asks about content from documents or sources
    that have been added to the assistant's knowledge base.

    Args:
        query: What to search for.
    """
    store = get_vectorstore()
    results = store.similarity_search(query, k=4)

    if not results:
        return (
            "The knowledge base is currently empty. No custom documents "
            "have been added yet."
        )

    return "\n\n".join(
        f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
        for doc in results
    )
