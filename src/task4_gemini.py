"""
Task 4 — Chunking, embedding và indexing với FAISS + Gemini.

Sử dụng GoogleGenerativeAIEmbeddings thay vì HuggingFace.
"""

import os
import re
import ssl
from pathlib import Path
from typing import Optional

# Disable SSL verification for corporate proxies
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["PYTHONHTTPSVERIFY"] = "0"
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""
os.environ["SSL_CERT_FILE"] = ""
os.environ["SSL_CERT_DIR"] = ""
os.environ["HF_HUB_DISABLE_SSL"] = "1"

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .contracts import validate_document

load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
FAISS_DIR = Path(__file__).parent.parent / "faiss_index"

# Chunking parameters
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = "gemini-embedding-2-preview"
EMBEDDING_DIM = 3072  # Gemini embedding dimension

_title_pattern = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_url_pattern = re.compile(r"https?://[^\s)\]>\"]+")
_url_search_chars = 500

_vectorstore: Optional[FAISS] = None


def get_embeddings():
    """Get Gemini embeddings instance."""
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        output_dimensionality=EMBEDDING_DIM,
    )


def _extract_title(content: str, fallback: str) -> str:
    """Lấy heading H1 đầu tiên của Markdown."""
    match = _title_pattern.search(content)
    if match and match.group(1).strip():
        return match.group(1).strip()
    return fallback


def _extract_url(content: str) -> str | None:
    """Lấy URL nguồn trong header Markdown."""
    match = _url_pattern.search(content[:_url_search_chars])
    return match.group(0) if match else None


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document."""
    documents = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if path.name.startswith("."):
            continue
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        doc_type = "legal" if "legal" in path.parts else "news"
        document = {
            "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
            "content": content,
            "metadata": {
                "source": path.name,
                "title": _extract_title(
                    content,
                    path.stem.replace("-", " ").replace("_", " ").title(),
                ),
                "doc_type": doc_type,
                "url": _extract_url(content),
            },
        }
        validate_document(document)
        documents.append(document)
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for document in documents:
        for chunk_index, text in enumerate(splitter.split_text(document["content"])):
            chunks.append({
                "id": f"{document['id']}::chunk-{chunk_index}",
                "content": text.strip(),
                "metadata": {
                    **document["metadata"],
                    "chunk_index": chunk_index,
                },
            })
    return chunks


def get_vectorstore() -> FAISS:
    """Get or create FAISS vectorstore."""
    global _vectorstore
    if _vectorstore is None:
        if FAISS_DIR.exists() and (FAISS_DIR / "index.faiss").exists():
            print(f"Loading existing FAISS index from {FAISS_DIR}")
            _vectorstore = FAISS.load_local(
                str(FAISS_DIR),
                get_embeddings(),
                allow_dangerous_deserialization=True,
            )
        else:
            _vectorstore = _build_index()
    return _vectorstore


def _build_index() -> FAISS:
    """Build FAISS index from chunks."""
    documents = load_documents()
    if not documents:
        print(f"No documents found in {STANDARDIZED_DIR}")
        return FAISS.from_texts(["placeholder"], get_embeddings())

    chunks = chunk_documents(documents)
    for chunk in chunks:
        validate_document(chunk, require_chunk=True)

    texts = [chunk["content"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    ids = [chunk["id"] for chunk in chunks]

    # Create FAISS index
    vectorstore = FAISS.from_texts(
        texts=texts,
        embedding=get_embeddings(),
        metadatas=metadatas,
        ids=ids,
    )

    # Save index
    FAISS_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(FAISS_DIR))
    print(f"Indexed {len(chunks)} chunks from {len(documents)} documents")

    return vectorstore


def save_vectorstore() -> None:
    """Save vectorstore to disk."""
    global _vectorstore
    if _vectorstore is not None:
        FAISS_DIR.mkdir(parents=True, exist_ok=True)
        _vectorstore.save_local(str(FAISS_DIR))
        print(f"Saved FAISS index to {FAISS_DIR}")


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    global _vectorstore
    _vectorstore = _build_index()
    save_vectorstore()


if __name__ == "__main__":
    run_pipeline()
