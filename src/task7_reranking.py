"""
Task 7 — Reciprocal Rank Fusion.

RRF gộp nhiều bảng xếp hạng mà không cộng trực tiếp cosine score với BM25
score. Công thức: RRF(d) = sum(1 / (k + rank)), rank bắt đầu từ 1.
"""


def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Fuse nhiều ranked lists và trả hybrid SearchResult."""
    if not ranked_lists:
        return []
<<<<<<< Updated upstream
        
    scores: dict[str, float] = {}
    items: dict[str, dict] = {}
    
    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            item_id = item["id"]
            scores[item_id] = scores.get(item_id, 0.0) + (1.0 / (k + rank))
            if item_id not in items:
                items[item_id] = item
                
    ranked_ids = sorted(scores.keys(), key=lambda i: scores[i], reverse=True)
    results = []
    for item_id in ranked_ids[:top_k]:
        result = items[item_id].copy()
        result["score"] = float(scores[item_id])
        result["retrieval_method"] = "hybrid"
        results.append(result)
        
=======

    scores = {}
    items = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            item_id = item["id"]
            # RRF formula: 1 / (k + rank)
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
            items[item_id] = item

    # Sort by RRF score descending
    ranked_ids = sorted(scores, key=lambda x: scores[x], reverse=True)

    results = []
    for item_id in ranked_ids[:top_k]:
        result = items[item_id].copy()
        result["score"] = scores[item_id]
        result["retrieval_method"] = "hybrid"
        results.append(result)

>>>>>>> Stashed changes
    return results


if __name__ == "__main__":
<<<<<<< Updated upstream
    test_d = [{"id": "doc1", "content": "c1", "metadata": {"source": "s1", "title": "t1", "doc_type": "legal", "url": None, "chunk_index": 0}, "score": 0.9, "retrieval_method": "dense"}]
    test_b = [{"id": "doc1", "content": "c1", "metadata": {"source": "s1", "title": "t1", "doc_type": "legal", "url": None, "chunk_index": 0}, "score": 1.2, "retrieval_method": "bm25"}]
    print(rerank_rrf([test_d, test_b], top_k=5))

=======
    # Test RRF
    dense_results = [
        {"id": "doc1", "content": "test1", "score": 0.9, "metadata": {}, "retrieval_method": "dense"},
        {"id": "doc2", "content": "test2", "score": 0.8, "metadata": {}, "retrieval_method": "dense"},
    ]
    bm25_results = [
        {"id": "doc2", "content": "test2", "score": 10.0, "metadata": {}, "retrieval_method": "bm25"},
        {"id": "doc3", "content": "test3", "score": 8.0, "metadata": {}, "retrieval_method": "bm25"},
    ]

    fused = rerank_rrf([dense_results, bm25_results], top_k=3)
    print("Fused results:")
    for r in fused:
        print(f"  {r['id']}: score={r['score']:.4f}, method={r['retrieval_method']}")
>>>>>>> Stashed changes
