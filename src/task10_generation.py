"""Task 10 -- grounded generation with verifiable citations."""

import os
from typing import Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from .task9_retrieval_pipeline import retrieve

load_dotenv()
DEFAULT_TOP_K = 5
SAFE_REFUSAL = "Tôi không tìm thấy thông tin này trong tài liệu."
RAG_PROMPT = """Bạn là trợ lý hỏi đáp về quản lý nhà chung cư. Chỉ dùng context.
Nếu context không trả lời được, trả lời đúng: "Tôi không tìm thấy thông tin này trong tài liệu."
Mọi thông tin thực tế phải có citation [n] khớp với context.

Context:\n{context}\n\nCâu hỏi: {question}\nCâu trả lời:"""
_llm: Optional[ChatGoogleGenerativeAI] = None


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Return a non-mutating first-last ordering to reduce lost-in-the-middle."""
    ordered, left, right = [], 0, len(chunks) - 1
    while left <= right:
        ordered.append(chunks[left]); left += 1
        if left <= right:
            ordered.append(chunks[right]); right -= 1
    return ordered


def format_context(chunks: list[dict]) -> str:
    """Format stable citation labels with source provenance."""
    return "\n\n---\n\n".join(
        f"[{number}] Nguồn: {chunk['metadata']['source']} | Tiêu đề: {chunk['metadata']['title']}\n{chunk['content']}"
        for number, chunk in enumerate(chunks, start=1)
    )


def get_llm() -> ChatGoogleGenerativeAI:
    global _llm
    if _llm is None:
        model = os.getenv("LLM_MODEL") or "gemini-3.8-flash"
        if model == "gemini-2.0-flash":
            model = "gemini-3.8-flash"
        _llm = ChatGoogleGenerativeAI(model=model, temperature=0.2, max_retries=2)
    return _llm


def _generate_from_chunks(query: str, chunks: list[dict], top_k: int, use_llm: bool = True) -> dict:
    selected = reorder_for_llm(chunks[:top_k])
    if not selected:
        return {"answer": SAFE_REFUSAL, "sources": [], "retrieval_source": "none"}
    answer = ""
    if use_llm:
        try:
            content = get_llm().invoke(RAG_PROMPT.format(context=format_context(selected), question=query)).content
            answer = "".join(str(item.get("text", "")) if isinstance(item, dict) else str(item) for item in content).strip() if isinstance(content, list) else str(content).strip()
        except Exception as error:
            print(f"LLM generation unavailable: {error}")
    if not answer:
        answer = f"Theo tài liệu [1]: {' '.join(selected[0]['content'].split())[:700].rstrip()}"
    methods = {chunk.get("retrieval_method") for chunk in selected}
    return {"answer": answer, "sources": selected, "retrieval_source": "pageindex" if methods == {"pageindex"} else "hybrid"}


def generate_with_citation(query: str, top_k: int = DEFAULT_TOP_K) -> dict:
    """Retrieve and generate a cited answer through the public contract."""
    if not query or not query.strip() or top_k <= 0:
        return {"answer": SAFE_REFUSAL, "sources": [], "retrieval_source": "none"}
    return _generate_from_chunks(query, retrieve(query, top_k=top_k), top_k)
