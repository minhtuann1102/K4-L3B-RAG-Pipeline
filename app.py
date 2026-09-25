"""Streamlit UI for the condominium RAG chatbot."""

import os
import ssl

import streamlit as st
from dotenv import load_dotenv

ssl._create_default_https_context = ssl._create_unverified_context
os.environ["PYTHONHTTPSVERIFY"] = "0"
load_dotenv()

from src.task10_generation import generate_with_citation

st.set_page_config(page_title="RAG Chatbot - Vinhomes", page_icon="🏢", layout="wide")
st.title("🏢 RAG Chatbot - Vinhomes")
st.caption("Hỏi đáp về chi phí, quy định và dịch vụ chung cư; câu trả lời luôn kèm nguồn.")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Cấu hình")
    top_k = st.slider("Số chunks tìm kiếm", min_value=3, max_value=10, value=5)
    st.caption("Hybrid retrieval: Dense + BM25 + RRF")
    st.caption("Nguồn: Luật Nhà ở, Nghị định 95/2024, Thông tư 02/2016 và bài viết cư dân.")
    if st.button("Xóa lịch sử"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("📚 Nguồn tham khảo"):
                for number, source in enumerate(message["sources"], start=1):
                    meta = source["metadata"]
                    st.markdown(f"**[{number}] {meta['source']}** — {meta['title']}")
                    st.caption(f"{source['retrieval_method']} | score {source['score']:.4f}")
                    st.write(source["content"][:300] + "...")

query = st.chat_input("Nhập câu hỏi của bạn...")
if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
    with st.chat_message("assistant"), st.spinner("🔍 Đang tìm kiếm và trả lời..."):
        result = generate_with_citation(query, top_k=top_k)
        st.markdown(result["answer"])
        if result["sources"]:
            with st.expander("📚 Nguồn tham khảo", expanded=True):
                for number, source in enumerate(result["sources"], start=1):
                    meta = source["metadata"]
                    st.markdown(f"**[{number}] {meta['source']}** — {meta['title']}")
                    st.caption(f"{source['retrieval_method']} | score {source['score']:.4f}")
                    st.write(source["content"][:300] + "...")
        st.caption(f"Retrieval source: `{result['retrieval_source']}`")
    st.session_state.messages.append({"role": "assistant", "content": result["answer"], "sources": result["sources"]})
