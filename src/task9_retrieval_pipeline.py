"""
Task 9 — Retrieval pipeline hoàn chỉnh.

Luồng xử lý:
    1. Chạy semantic_search và lexical_search.
    2. Fuse hai danh sách bằng RRF đúng một lần.
    3. Lấy best cosine score gốc từ dense results.
    4. Nếu score dưới threshold, thử PageIndex fallback.
"""

import os
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["PYTHONHTTPSVERIFY"] = "0"

from .task5_gemini import semantic_search
from .task6_gemini import lexical_search
from .task7_reranking import rerank_rrf
from .task8_pageindex_vectorless import pageindex_search

# Tuned against the golden set: in-domain fee query = 0.685, unrelated pho
# query = 0.514 after FAISS distance-to-similarity conversion.
SCORE_THRESHOLD = 0.55
MIN_FALLBACK_SCORE = 0.60
DEFAULT_TOP_K = 5


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """Trả về hybrid hoặc pageindex SearchResult."""
<<<<<<< Updated upstream
    if not query or not query.strip() or top_k <= 0:
        return []

    dense = semantic_search(query, top_k=top_k * 2)
    sparse = lexical_search(query, top_k=top_k * 2)

    if not dense and not sparse:
        return []

    if use_reranking and (dense or sparse):
        hybrid = rerank_rrf([dense, sparse], top_k=top_k)
    else:
        hybrid = dense[:top_k] if dense else sparse[:top_k]

    best_dense_score = dense[0]["score"] if dense else 0.0
    if best_dense_score < score_threshold:
        try:
            fallback = pageindex_search(query, top_k=top_k)
            if fallback:
                return fallback[:top_k]
=======
    dense = semantic_search(query, top_k=top_k * 2)
    sparse = lexical_search(query, top_k=top_k * 2)

    if use_reranking:
        hybrid = rerank_rrf([dense, sparse], top_k=top_k)
    else:
        hybrid = dense[:top_k]

    # Check fallback threshold (dùng dense score gốc)
    best_dense_score = dense[0]["score"] if dense else 0.0

    if best_dense_score < score_threshold:
        try:
            fallback = pageindex_search(query, top_k=top_k)
            if fallback and fallback[0]["score"] >= MIN_FALLBACK_SCORE:
                return fallback
            # A weak lexical overlap is not evidence that the question is in-domain.
            return []
>>>>>>> Stashed changes
        except Exception:
            pass

    return hybrid[:top_k]


if __name__ == "__main__":
<<<<<<< Updated upstream
    for result in retrieve("quy định nuôi chó mèo", top_k=3):
        print(result["metadata"]["title"], "->", result["score"])

=======
    results = retrieve("phí quản lý chung cư", top_k=3)
    print(f"Found {len(results)} results")
    for r in results:
        print(f"  {r['score']:.4f} | {r['id']} | {r['retrieval_method']}")
>>>>>>> Stashed changes
