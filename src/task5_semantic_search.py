"""
Task 5 — Semantic search.

Embed query bằng chính ``embed_texts`` của Task 4, query ChromaDB và đổi cosine
distance thành similarity. Output phải theo ``SearchResult``,
``retrieval_method="dense"``, sort giảm dần và không vượt ``top_k``.

Metadata đọc từ ChromaDB được đưa qua ``normalize_chroma_metadata`` để giữ đúng
``ChunkMetadata`` (ChromaDB bỏ qua giá trị ``None``, xem ghi chú ở Task 4).
"""

from .task4_chunking_indexing import (
    embed_texts,
    get_collection,
    normalize_chroma_metadata,
)

DEFAULT_TOP_K = 10


def semantic_search(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    if not query or not query.strip() or top_k <= 0:
        return []

    query_vectors = embed_texts([query])
    if not query_vectors:
        return []
    query_vector = query_vectors[0]

    collection = get_collection()
    response = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    ids = response.get("ids", [[]])[0]
    documents = response.get("documents", [[]])[0]
    metadatas = response.get("metadatas", [[]])[0]
    distances = response.get("distances", [[]])[0]

    results = []
    seen_ids = set()
    for item_id, content, metadata, distance in zip(ids, documents, metadatas, distances):
        if item_id in seen_ids:
            continue
        seen_ids.add(item_id)
        # cosine distance -> similarity; clamp để score không âm.
        score = max(0.0, 1.0 - float(distance))
        results.append({
            "id": item_id,
            "content": content,
            "score": score,
            "metadata": normalize_chroma_metadata(metadata or {}),
            "retrieval_method": "dense",
        })

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    for result in semantic_search("test query", top_k=3):
        print(result)
