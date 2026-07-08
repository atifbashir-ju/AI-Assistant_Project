
from fastapi import APIRouter, HTTPException, UploadFile

from app.rag.ingest import chunk_text, extract_text
from app.rag.store import get_vectorstore, list_ingested_sources, register_ingested_source

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(file: UploadFile):
    content = await file.read()

    try:
        text = extract_text(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not text.strip():
        raise HTTPException(status_code=400, detail="No extractable text found in that file.")

    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="File produced no usable chunks.")

    store = get_vectorstore()
    store.add_texts(chunks, metadatas=[{"source": file.filename} for _ in chunks])
    register_ingested_source(file.filename, len(chunks))

    return {
        "filename": file.filename,
        "chunks_added": len(chunks),
        "message": (
            "Document added to the knowledge base. Set ENABLE_RAG_TOOL=true "
            "in .env and restart the backend if you haven't already."
        ),
    }


@router.get("")
async def list_documents():
    return {"sources": list_ingested_sources()}
