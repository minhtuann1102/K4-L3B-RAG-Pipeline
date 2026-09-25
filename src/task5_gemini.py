"""
Task 5 — Semantic search với FAISS + Gemini.

Embed query bằng Gemini embeddings, query FAISS vectorstore.
"""

import os
import ssl

# SSL fix
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["PYTHONHTTPSVERIFY"] = "0"

from .task4_gemini import get_vectorstore

DEFAULT_TOP_K = 10


def semantic_search(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    if not query or not query.strip() or top_k <= 0:
        return []

    try:
        vectorstore = get_vectorstore()
        docs_and_scores = vectorstore.similarity_search_with_score(query, k=top_k)

        results = []
        seen_ids = set()
        for doc, score in docs_and_scores:
            doc_id = doc.metadata.get("id", doc.page_content[:50])
            if doc_id in seen_ids:
                continue
            seen_ids.add(doc_id)

            # Convert L2 distance to similarity
            similarity = max(0.0, 1.0 / (1.0 + float(score)))

            results.append({
                "id": doc_id,
                "content": doc.page_content,
                "score": float(similarity),
                "metadata": {
                    "source": doc.metadata.get("source", ""),
                    "title": doc.metadata.get("title", ""),
                    "doc_type": doc.metadata.get("doc_type", ""),
                    "url": doc.metadata.get("url"),
                    "chunk_index": int(doc.metadata.get("chunk_index", 0)),
                },
                "retrieval_method": "dense",
            })

        results.sort(key=lambda item: item["score"], reverse=True)
        return results

    except Exception as e:
        print(f"Semantic search error: {e}")
        return []


if __name__ == "__main__":
    for result in semantic_search("phí quản lý chung cư", top_k=3):
        print(f"{result['score']:.4f} | {result['id']}")
