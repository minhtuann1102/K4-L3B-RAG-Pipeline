"""
Task 6 — Lexical search với BM25.
"""

import os
import re

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["PYTHONHTTPSVERIFY"] = "0"

from .task4_gemini import load_documents, chunk_documents

DEFAULT_TOP_K = 10
TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)

CORPUS: list[dict] = []
_index_cache: dict = {"key": None, "bm25": None, "token_sets": []}


def tokenize(text: str) -> list[str]:
    """Tokenize: lowercase và tách theo ``\\w``."""
    return TOKEN_PATTERN.findall(text.lower())


def load_corpus() -> list[dict]:
    """Load corpus chunks."""
    global CORPUS
    if not CORPUS:
        documents = load_documents()
        CORPUS = chunk_documents(documents)
    return CORPUS


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index."""
    from rank_bm25 import BM25Okapi
    tokenized = [tokenize(item.get("content", "")) for item in corpus]
    return BM25Okapi(tokenized)


def get_bm25_index(corpus: list[dict]):
    """Get cached BM25 index."""
    global _index_cache
    key = (id(corpus), len(corpus))
    if _index_cache["key"] != key or _index_cache["bm25"] is None:
        _index_cache["bm25"] = build_bm25_index(corpus)
        _index_cache["token_sets"] = [
            set(tokenize(item.get("content", ""))) for item in corpus
        ]
        _index_cache["key"] = key
    return _index_cache["bm25"], _index_cache["token_sets"]


def lexical_search(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """Trả về BM25 SearchResult."""
    if not query or not query.strip() or top_k <= 0:
        return []

    corpus = load_corpus()
    if not corpus:
        return []

    query_tokens = tokenize(query)
    if not query_tokens:
        return []
    query_token_set = set(query_tokens)

    bm25, token_sets = get_bm25_index(corpus)
    scores = bm25.get_scores(query_tokens)

    matches = [
        index for index, tokens in enumerate(token_sets) if query_token_set & tokens
    ]
    matches.sort(key=lambda index: (-float(scores[index]), index))

    results = []
    for index in matches[:top_k]:
        item = corpus[index]
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(scores[index]),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })
    return results


if __name__ == "__main__":
    hits = lexical_search("phí quản lý", top_k=3)
    print(f"corpus={len(CORPUS)} hits={len(hits)}")
    for hit in hits:
        print(f"{hit['score']:.4f} | {hit['metadata']['source']} | {hit['id']}")
