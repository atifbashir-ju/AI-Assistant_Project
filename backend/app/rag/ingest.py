
from io import BytesIO

from langchain_text_splitters import RecursiveCharacterTextSplitter

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
)


def extract_text(filename: str, content: bytes) -> str:
    lower = filename.lower()

    if lower.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(content))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)

    if lower.endswith((".txt", ".md")):
        return content.decode("utf-8", errors="ignore")

    raise ValueError(
        f"Unsupported file type for '{filename}'. Supported: .txt, .md, .pdf"
    )


def chunk_text(text: str) -> list[str]:
    return _splitter.split_text(text)
