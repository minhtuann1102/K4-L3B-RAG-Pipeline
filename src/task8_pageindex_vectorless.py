"""
Task 8 — PageIndex vectorless fallback.

Simple keyword-based fallback khi semantic search score thấp.
"""

import os
import re

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from .task4_gemini import load_documents, chunk_documents

DEFAULT_TOP_K = 5
SCORE_THRESHOLD = 0.3  # Ngưỡng fallback

TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)

# Cache corpus
_CORPUS: list[dict] = []


def tokenize(text: str) -> list[str]:
    """Tokenize text."""
    return TOKEN_PATTERN.findall(text.lower())


def load_corpus() -> list[dict]:
    """Load corpus chunks."""
    global _CORPUS
    if not _CORPUS:
        documents = load_documents()
        _CORPUS = chunk_documents(documents)
    return _CORPUS


def upload_documents() -> None:
<<<<<<< Updated upstream
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    if not PAGEINDEX_API_KEY:
        return
    # Implement upload if needed when PAGEINDEX_API_KEY is available


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult nếu có cấu hình PAGEINDEX_API_KEY, ngược lại fallback rỗng."""
    if not PAGEINDEX_API_KEY or not query or not query.strip() or top_k <= 0:
        return []
    try:
        # If PageIndex client is available, call it here
        return []
    except Exception:
        return []


if __name__ == "__main__":
    print("PageIndex vectorless module ready.")

=======
    """Placeholder - documents đã được load sẵn."""
    pass


def pageindex_search(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """Simple keyword matching fallback."""
    if not query or not query.strip():
        return []

    corpus = load_corpus()
    if not corpus:
        return []

    query_tokens = set(tokenize(query))
    if not query_tokens:
        return []

    # Simple keyword matching
    results = []
    for chunk in corpus:
        content_tokens = set(tokenize(chunk["content"]))
        # Tính overlap score
        overlap = query_tokens & content_tokens
        if overlap:
            score = len(overlap) / len(query_tokens)
            results.append({
                "id": chunk["id"],
                "content": chunk["content"],
                "score": float(score),
                "metadata": chunk["metadata"],
                "retrieval_method": "pageindex",
            })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    hits = pageindex_search("phí quản lý", top_k=3)
    print(f"Found {len(hits)} results")
    for hit in hits:
        print(f"  {hit['score']:.4f} | {hit['metadata']['source']}")
>>>>>>> Stashed changes
