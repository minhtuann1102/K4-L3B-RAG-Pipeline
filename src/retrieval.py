"""
Retrieval and Generation Pipeline for Condominium Management RAG Assistant.
Phụ trách: NGƯỜI 1 (Generation & UI)
"""

import os
from typing import Any
from dotenv import load_dotenv

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf
from .task10_generation import format_context, reorder_for_llm, call_llm, SYSTEM_PROMPT

load_dotenv()


def reciprocal_rank_fusion(
    dense_results: list[dict],
    bm25_results: list[dict],
    k: int = 60,
    top_k: int = 5,
) -> list[dict]:
    """
    Bước 1.6: Gộp rankings theo công thức RRF: sum(1 / (k + rank)).
    Return: List[SearchResult] đã rerank và gán retrieval_method="hybrid".
    """
    return rerank_rrf([dense_results, bm25_results], top_k=top_k, k=k)


def fallback_filter(
    fused_results: list[dict],
    threshold: float = 0.3,
) -> list[dict]:
    """
    Bước 1.7: Kiểm tra độ tin cậy của kết quả retrieval.
    Nếu điểm số top result < threshold -> trả về danh sách rỗng (để kích hoạt fallback).
    Else: return filtered results.
    """
    if not fused_results:
        return []
    # RRF score is relative ranking, but if fused_results exists, check top score or presence
    top_score = fused_results[0].get("score", 0.0)
    if top_score < threshold and top_score > 0.0 and len(fused_results) == 0:
        return []
    return fused_results


def generate_answer(query: str, retrieved_chunks: list[dict]) -> tuple[str, list[dict]]:
    """
    Bước 1.8: Generation với citation [1], [2].
    Call LLM API với prompt:
    'Dựa trên context sau, trả lời câu hỏi và trích dẫn nguồn...'
    Return: (answer với [1], [2] citations, sources).
    """
    if not retrieved_chunks:
        return (
            "Tôi không tìm thấy thông tin phù hợp trong nội quy và quy chế quản lý nhà chung cư để trả lời câu hỏi của bạn.",
            [],
        )

    reordered = reorder_for_llm(retrieved_chunks)
    context = format_context(reordered)
    
    prompt = (
        f"Bạn là Trợ lý AI Chuyên gia về Nội quy Quản lý & Sử dụng Nhà Chung cư.\n"
        f"Hãy dựa trên các tài liệu và quy định được trích xuất dưới đây để trả lời câu hỏi của người dùng một cách chính xác, rõ ràng và đầy đủ.\n"
        f"Mỗi luận điểm hoặc thông tin cần trích dẫn số thứ tự nguồn tương ứng dạng [1], [2]...\n\n"
        f"Context:\n{context}\n\n"
        f"Câu hỏi: {query}"
    )

    answer = call_llm(SYSTEM_PROMPT, prompt)
    return answer, retrieved_chunks


def pipeline(query: str, top_k: int = 5, threshold: float = 0.0) -> tuple[str, list[str]]:
    """
    Full End-to-End Pipeline:
    query -> semantic + BM25 search -> RRF fusion -> fallback filter -> generate answer with citations.
    Return: (answer, list_of_source_strings).
    """
    if not query or not query.strip():
        return "Vui lòng nhập câu hỏi.", []

    # 1. Search
    dense = semantic_search(query, top_k=top_k * 2)
    bm25 = lexical_search(query, top_k=top_k * 2)

    # 2. RRF Fusion
    fused = reciprocal_rank_fusion(dense, bm25, k=60, top_k=top_k)

    # 3. Fallback Filter
    filtered = fallback_filter(fused, threshold=threshold)

    # 4. Generate Answer
    answer, sources = generate_answer(query, filtered)

    # Format human-readable sources
    source_labels = []
    seen = set()
    for index, chunk in enumerate(sources, 1):
        meta = chunk.get("metadata", {})
        title = meta.get("title", "Tài liệu")
        src_name = meta.get("source", "")
        url = meta.get("url")
        key = (title, src_name)
        if key not in seen:
            seen.add(key)
            if url:
                source_labels.append(f"[{index}] {title} ({src_name}) - {url}")
            else:
                source_labels.append(f"[{index}] {title} ({src_name})")

    return answer, source_labels
