"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5 (cùng ``id``, cùng metadata) để hai bảng xếp
hạng fuse được với nhau bằng RRF ở Task 7. BM25 mạnh ở từ khóa chính xác, mã
tài liệu và tên riêng.

Output theo ``SearchResult``: ``retrieval_method="bm25"``, score giảm dần,
không vượt ``top_k``, không trùng ID, metadata nguồn giữ nguyên như Task 4.

Ghi chú đã kiểm chứng với ``rank-bm25==0.2.2``:
    - IDF của ``BM25Okapi`` có thể bằng 0 (corpus nhỏ) hoặc âm (term xuất hiện ở
      gần như mọi document), nên KHÔNG lọc kết quả bằng ``score > 0``. Ở đây chỉ
      giữ chunk có token trùng với query.
    - ``np.argsort(scores)[::-1]`` đảo thứ tự khi có tie; vì vậy dùng sort theo
      ``(-score, vị trí trong corpus)`` để thứ hạng ổn định giữa các lần chạy.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - chỉ dùng cho type hint
    from rank_bm25 import BM25Okapi


DEFAULT_TOP_K = 10
TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)

#: Corpus chunks dùng chung với Task 4/5, nạp lazy ở lần search đầu tiên.
CORPUS: list[dict] = []

_index_cache: dict = {"key": None, "bm25": None, "token_sets": []}


def tokenize(text: str) -> list[str]:
    """Tokenize: lowercase và tách theo ``\\w`` (giữ dấu tiếng Việt)."""
    return TOKEN_PATTERN.findall(text.lower())


def _corpus_from_vectorstore() -> list[dict]:
    """Đọc corpus chunks đã index trong ChromaDB (nguồn ưu tiên)."""
    from .task4_chunking_indexing import get_collection, normalize_chroma_metadata

    payload = get_collection().get(include=["documents", "metadatas"])
    ids = payload.get("ids") or []
    documents = payload.get("documents") or []
    metadatas = payload.get("metadatas") or []

    corpus = []
    for item_id, content, metadata in zip(ids, documents, metadatas):
        if not content:
            continue
        corpus.append({
            "id": item_id,
            "content": content,
            "metadata": normalize_chroma_metadata(metadata or {}),
        })
    return corpus


def _corpus_from_standardized() -> list[dict]:
    """Fallback: chunk lại dữ liệu chuẩn hóa nếu ChromaDB chưa có index."""
    from .task4_chunking_indexing import chunk_documents, load_documents

    return chunk_documents(load_documents())


def load_corpus() -> list[dict]:
    """Nạp corpus chunks cho BM25: ChromaDB trước, data/standardized sau."""
    try:
        corpus = _corpus_from_vectorstore()
    except Exception as error:  # pragma: no cover - phụ thuộc môi trường
        print(f"BM25: không đọc được ChromaDB ({error}); dùng data/standardized")
        corpus = []
    if corpus:
        return corpus
    return _corpus_from_standardized()


def build_bm25_index(corpus: list[dict]) -> "BM25Okapi":
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    from rank_bm25 import BM25Okapi

    tokenized = [tokenize(item.get("content", "")) for item in corpus]
    return BM25Okapi(tokenized)


def get_bm25_index(corpus: list[dict]) -> tuple["BM25Okapi", list[set[str]]]:
    """Trả về ``(bm25 index, token set từng chunk)`` và cache theo corpus."""
    key = (id(corpus), len(corpus))
    if _index_cache["key"] != key or _index_cache["bm25"] is None:
        _index_cache["bm25"] = build_bm25_index(corpus)
        _index_cache["token_sets"] = [
            set(tokenize(item.get("content", ""))) for item in corpus
        ]
        _index_cache["key"] = key
    return _index_cache["bm25"], _index_cache["token_sets"]


def lexical_search(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    if not query or not query.strip() or top_k <= 0:
        return []

    global CORPUS
    if not CORPUS:
        CORPUS = load_corpus()
    if not CORPUS:
        return []

    query_tokens = tokenize(query)
    if not query_tokens:
        return []
    query_token_set = set(query_tokens)

    bm25, token_sets = get_bm25_index(CORPUS)
    scores = bm25.get_scores(query_tokens)

    matches = [
        index for index, tokens in enumerate(token_sets) if query_token_set & tokens
    ]
    matches.sort(key=lambda index: (-float(scores[index]), index))

    results = []
    for index in matches[:top_k]:
        item = CORPUS[index]
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(scores[index]),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })
    return results


if __name__ == "__main__":
    hits = lexical_search("học phí", top_k=3)
    print(f"corpus={len(CORPUS)} hits={len(hits)}")
    for hit in hits:
        print(f"{hit['score']:.4f} | {hit['metadata']['source']} | {hit['id']}")
