"""
Streamlit Application — RAG Chatbot: Quản lý & Sử dụng Nhà Chung Cư.
Phụ trách: NGƯỜI 1 (Generation & UI)
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Set env flags before imports
os.environ["USE_TF"] = "0"
os.environ["TRANSFORMERS_NO_TF"] = "1"

from src.retrieval import pipeline, reciprocal_rank_fusion, fallback_filter, generate_answer
from src.task5_semantic_search import semantic_search
from src.task6_lexical_search import lexical_search

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Trợ Lý AI Chung Cư | Condominium RAG Assistant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern premium UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .source-box {
        background-color: #F3F4F6;
        border-left: 4px solid #3B82F6;
        padding: 10px 14px;
        margin-top: 8px;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .citation-badge {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Cấu hình Hệ thống")
    st.markdown("---")
    
    st.subheader("📚 Bộ dữ liệu tri thức")
    st.info("""
    **Domain:** Nội quy quản lý, sử dụng nhà chung cư
    -  **4 Văn bản pháp luật:** Luật Nhà ở 2023, Nghị định 95/2024, Thông tư 02/2016 (TT-BXD), Mẫu nội quy chung cư.
    - 📰 **5 Cẩm nang & Quy định:** Chi phí quản lý, thẻ cư dân, PCCC, thi công nội thất, tiện ích BBQ.
    """)
    
    st.subheader("🔍 Tham số Retrieval")
    top_k = st.slider("Số lượng Chunks trích xuất (Top-K):", min_value=1, max_value=8, value=4)
    use_rrf = st.checkbox("Sử dụng Hybrid RRF (Dense + BM25)", value=True)
    score_threshold = st.slider("Ngưỡng tin cậy (Threshold):", min_value=0.0, max_value=0.8, value=0.0, step=0.05)
    
    st.markdown("---")
    if st.button("🗑️ Xóa lịch sử hội thoại"):
        st.session_state.messages = []
        st.rerun()

# Main Content
st.markdown('<div class="main-header">🏢 Trợ Lý AI: Tư Vấn Nội Quy & Quản Lý Nhà Chung Cư</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Hệ thống RAG tra cứu chính xác quyền lợi, nghĩa vụ, quy định an toàn PCCC, thi công nội thất, phí dịch vụ và tiện ích cư dân.</div>', unsafe_allow_html=True)

# Quick Suggestion Prompts
st.markdown("**💡 Gợi ý câu hỏi nhanh:**")
col1, col2, col3, col4 = st.columns(4)

suggested_query = None
with col1:
    if st.button("🐶 Nuôi chó mèo chung cư?"):
        suggested_query = "Chung cư có cho phép nuôi chó mèo không và cần tuân thủ quy định gì?"
with col2:
    if st.button("🔨 Giờ giấc khoan đục sửa nhà?"):
        suggested_query = "Khung giờ được phép thi công gây tiếng ồn, cải tạo căn hộ chung cư?"
with col3:
    if st.button("💰 Phí quản lý hàng tháng?"):
        suggested_query = "Chi phí ở chung cư mỗi tháng gồm những khoản phí nào và cách tính ra sao?"
with col4:
    if st.button("🍖 Đặt chòi nướng BBQ?"):
        suggested_query = "Quy định đặt chỗ và mức phí sử dụng vườn nướng BBQ ngoài trời?"

# Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander(f"📌 Nguồn trích dẫn ({len(message['sources'])} tài liệu)", expanded=False):
                for src in message["sources"]:
                    st.markdown(f"- {src}")

# Handle Input
query_input = st.chat_input("Nhập câu hỏi về nội quy hoặc quản lý chung cư...")
active_query = suggested_query if suggested_query else query_input

if active_query:
    st.session_state.messages.append({"role": "user", "content": active_query})
    with st.chat_message("user"):
        st.markdown(active_query)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Đang tra cứu quy chế, điều lệ và tổng hợp câu trả lời..."):
            try:
                if use_rrf:
                    # Hybrid retrieval with RRF
                    dense = semantic_search(active_query, top_k=top_k * 2)
                    bm25 = lexical_search(active_query, top_k=top_k * 2)
                    fused = reciprocal_rank_fusion(dense, bm25, k=60, top_k=top_k)
                    filtered = fallback_filter(fused, threshold=score_threshold)
                    answer, raw_sources = generate_answer(active_query, filtered)
                else:
                    dense = semantic_search(active_query, top_k=top_k)
                    answer, raw_sources = generate_answer(active_query, dense)
                
                # Format sources list
                source_strings = []
                seen = set()
                for idx, chunk in enumerate(raw_sources, 1):
                    meta = chunk.get("metadata", {})
                    title = meta.get("title", "Tài liệu")
                    source_file = meta.get("source", "")
                    url = meta.get("url")
                    method = chunk.get("retrieval_method", "hybrid")
                    key = (title, source_file)
                    if key not in seen:
                        seen.add(key)
                        url_part = f" — [Xem link]({url})" if url else ""
                        source_strings.append(f"**[{idx}] {title}** (`{source_file}`) [{method}]{url_part}")

                # Display answer
                st.markdown(answer)

                # Display sources
                if source_strings:
                    with st.expander(f"📌 Nguồn trích dẫn ({len(source_strings)} tài liệu)", expanded=True):
                        for s in source_strings:
                            st.markdown(f"- {s}")
                            
                        # Show raw chunk preview
                        st.markdown("---")
                        st.markdown("**Trích đoạn nội dung liên quan:**")
                        for idx, chunk in enumerate(raw_sources[:top_k], 1):
                            m = chunk.get("metadata", {})
                            st.caption(f"**[{idx}] {m.get('title')} (score: {chunk.get('score', 0):.4f}):**")
                            st.text(chunk.get("content", "")[:300] + "...")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": source_strings,
                })

            except Exception as e:
                err_msg = f" Đã xảy ra lỗi trong quá trình xử lý: {e}"
                st.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})
