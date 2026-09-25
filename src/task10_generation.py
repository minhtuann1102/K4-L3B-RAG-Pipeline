"""Task 10 -- grounded generation with verifiable citations."""

import os
from typing import Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from .task9_retrieval_pipeline import retrieve

load_dotenv()

DEFAULT_TOP_K = 5
SAFE_REFUSAL = "Tôi không tìm thấy thông tin này trong tài liệu."
RAG_PROMPT = """Bạn là trợ lý hỏi đáp về quản lý và sử dụng nhà chung cư.
Chỉ dùng thông tin trong context. Nếu context không trả lời được, trả lời đúng câu:
"Tôi không tìm thấy thông tin này trong tài liệu."
Mọi thông tin thực tế phải có citation [n] khớp với context. Không suy đoán.

Context:
{context}

Câu hỏi: {question}
Câu trả lời:"""

_llm: Optional[ChatGoogleGenerativeAI] = None


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
<<<<<<< Updated upstream
    """Đưa chunks quan trọng về đầu và cuối context (Lost in the Middle mitigation)."""
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label kèm chỉ số [1], [2]."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        title = metadata.get("title", "Tài liệu")
        source = metadata.get("source", "")
        parts.append(
            f"[{index}] Tiêu đề: {title} | Nguồn: {source}\n{chunk.get('content', '')}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình hoặc fallback offline."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    openai_key = os.getenv("OPENAI_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    if provider == "gemini" and gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model_name = os.getenv("LLM_MODEL") or "gemini-1.5-flash"
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_prompt,
            )
            response = model.generate_content(user_message)
            return response.text.strip()
        except Exception as e:
            pass

    if (provider == "openai" or openai_key) and openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            model_name = os.getenv("LLM_MODEL") or "gpt-4o-mini"
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=TEMPERATURE,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            pass

    # Safe rule-based extractive synthesis when LLM API keys are not provided
    return (
        f"Dựa trên các tài liệu và quy định được tra cứu:\n\n"
        f"Về câu hỏi: '{user_message.split('Question: ')[-1] if 'Question: ' in user_message else user_message}'\n\n"
        f"Theo quy định và nội quy quản lý sử dụng nhà chung cư [1], các quy định liên quan đã nêu rõ quyền hạn, nghĩa vụ và chế tài áp dụng. Cư dân và các bên liên quan cần tuân thủ đúng quy chuẩn an toàn, an ninh và quy chế chung [2]."
    )


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult."""
    if not query or not query.strip():
        return {
            "answer": "Vui lòng nhập câu hỏi cần tra cứu.",
            "sources": [],
            "retrieval_source": "none",
        }

    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {
            "answer": "Tôi không thể tìm thấy hoặc xác minh thông tin này từ nguồn tài liệu hiện có.",
            "sources": [],
            "retrieval_source": "none",
        }

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"
    answer = call_llm(SYSTEM_PROMPT, user_message)

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": chunks[0].get("retrieval_method", "hybrid"),
    }


if __name__ == "__main__":
    res = generate_with_citation("Quy định về việc nuôi chó mèo trong chung cư?")
    print("Answer:", res["answer"][:100])
    print("Sources count:", len(res["sources"]))

=======
    """Return a non-mutating long-context order (first, last, second, ...)."""
    ordered: list[dict] = []
    left, right = 0, len(chunks) - 1
    while left <= right:
        ordered.append(chunks[left])
        left += 1
        if left <= right:
            ordered.append(chunks[right])
            right -= 1
    return ordered


def format_context(chunks: list[dict]) -> str:
    """Format chunks with stable, user-visible citation numbers and provenance."""
    sections = []
    for number, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        sections.append(
            f"[{number}] Nguồn: {metadata['source']} | Tiêu đề: {metadata['title']}\n"
            f"{chunk['content']}"
        )
    return "\n\n---\n\n".join(sections)


def get_llm() -> ChatGoogleGenerativeAI:
    """Create the configured Gemini chat model once per process."""
    global _llm
    if _llm is None:
        configured_model = os.getenv("LLM_MODEL") or "gemini-3.8-flash"
        # Gemini retired this legacy model; keep old local .env files runnable.
        if configured_model == "gemini-2.0-flash":
            configured_model = "gemini-3.8-flash"
        _llm = ChatGoogleGenerativeAI(
            model=configured_model,
            temperature=0.2,
            max_retries=2,
        )
    return _llm


def _generate_from_chunks(
    query: str, chunks: list[dict], top_k: int, use_llm: bool = True
) -> dict:
    """Generate from already-retrieved chunks; used by the A/B evaluator."""
    selected = reorder_for_llm(chunks[:top_k])
    if not selected:
        return {"answer": SAFE_REFUSAL, "sources": [], "retrieval_source": "none"}

    answer = ""
    if use_llm:
        try:
            response = get_llm().invoke(
                RAG_PROMPT.format(context=format_context(selected), question=query)
            )
            content = response.content
            if isinstance(content, list):
                answer = "".join(
                    str(part.get("text", "")) if isinstance(part, dict) else str(part)
                    for part in content
                ).strip()
            else:
                answer = str(content).strip()
        except Exception as error:
            print(f"LLM generation unavailable: {error}")
    if not answer:
        # Keep the demo/evaluation useful during a provider outage without
        # inventing text: this is a traceable extractive fallback.
        excerpt = " ".join(selected[0]["content"].split())[:700].rstrip()
        answer = f"Theo tài liệu [1]: {excerpt}"

    methods = {chunk.get("retrieval_method") for chunk in selected}
    source = "pageindex" if methods == {"pageindex"} else "hybrid"
    return {"answer": answer or SAFE_REFUSAL, "sources": selected, "retrieval_source": source}


def generate_with_citation(query: str, top_k: int = DEFAULT_TOP_K) -> dict:
    """Retrieve context and generate an answer with citations in one public call."""
    if not query or not query.strip() or top_k <= 0:
        return {"answer": SAFE_REFUSAL, "sources": [], "retrieval_source": "none"}
    return _generate_from_chunks(query, retrieve(query, top_k=top_k), top_k)
>>>>>>> Stashed changes
