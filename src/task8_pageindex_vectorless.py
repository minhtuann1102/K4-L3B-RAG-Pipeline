"""Task 8 -- local keyword fallback compatible with the PageIndex contract."""

import re

from .task4_gemini import chunk_documents, load_documents

DEFAULT_TOP_K = 5
TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)
_CORPUS: list[dict] = []


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def load_corpus() -> list[dict]:
    global _CORPUS
    if not _CORPUS:
        _CORPUS = chunk_documents(load_documents())
    return _CORPUS


def upload_documents() -> None:
    """Compatibility hook; the local fallback reads the standardized corpus."""


def pageindex_search(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """Return keyword-overlap results when the vector search is not confident."""
    if not query or not query.strip() or top_k <= 0:
        return []
    query_tokens = set(tokenize(query))
    if not query_tokens:
        return []

    results = []
    for chunk in load_corpus():
        overlap = query_tokens & set(tokenize(chunk["content"]))
        if overlap:
            results.append({
                "id": chunk["id"], "content": chunk["content"],
                "score": float(len(overlap) / len(query_tokens)),
                "metadata": chunk["metadata"], "retrieval_method": "pageindex",
            })
    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]
