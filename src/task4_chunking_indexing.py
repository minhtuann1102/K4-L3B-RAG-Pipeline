"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn.
    3. Embed chunks bằng một provider duy nhất.
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk phải theo docs/MODULE_CONTRACTS.md. ID cần ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 phải dùng chung embed_texts().

Quyết định đã kiểm chứng với chromadb 1.5.9:
    - ChromaDB bỏ qua giá trị ``None`` trong metadata, nên ``url=None`` phải ghi
      thành ``""`` khi upsert (``sanitize_metadata_for_chroma``) và đổi ngược lại
      thành ``None`` khi đọc (``normalize_chroma_metadata``) để SearchResult vẫn
      khớp contract.
    - ``metadata={"hnsw:space": "cosine"}`` vẫn được áp dụng, nên
      ``distance = 1 - cosine_similarity`` dùng ở Task 5 là hợp lệ.
"""

import os
import re
from pathlib import Path

from dotenv import load_dotenv

from .contracts import validate_document

load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Giải thích lựa chọn tham số trong báo cáo nhóm.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

#: Số chunk mỗi lần upsert để tránh request quá lớn.
UPSERT_BATCH_SIZE = 256

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
#: Dimension kỳ vọng của EMBEDDING_MODEL; đổi model thì phải re-index.
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1024"))
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
#: bge-m3 huấn luyện với cosine nên vector được normalize trước khi index.
NORMALIZE_EMBEDDINGS = True
SUPPORTED_EMBEDDING_PROVIDERS = ("sentence_transformers", "gemini")

COLLECTION_NAME = "rag_documents"

TITLE_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)
URL_PATTERN = re.compile(r"https?://[^\s)\]>\"]+")
#: Chỉ tìm URL nguồn trong phần đầu file để tránh bắt link trong nội dung.
URL_SEARCH_CHARS = 500

_embedding_model = None
_chroma_client = None
_chroma_client_path: str | None = None


def get_embedding_model():
    """Tải và cache SentenceTransformer model."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model


def _extract_title(content: str, fallback: str) -> str:
    """Lấy heading H1 đầu tiên của Markdown, fallback về tên file."""
    match = TITLE_PATTERN.search(content)
    if match and match.group(1).strip():
        return match.group(1).strip()
    return fallback


def _extract_url(content: str) -> str | None:
    """Lấy URL nguồn trong header Markdown (nếu có) để citation kiểm chứng được."""
    match = URL_PATTERN.search(content[:URL_SEARCH_CHARS])
    return match.group(0) if match else None


def sanitize_metadata_for_chroma(metadata: dict) -> dict:
    """Chuẩn hóa metadata trước khi ghi vào ChromaDB (``None`` -> ``""``)."""
    return {
        key: "" if value is None else value
        for key, value in metadata.items()
    }


def normalize_chroma_metadata(metadata: dict) -> dict:
    """Đưa metadata đọc từ ChromaDB về đúng ``ChunkMetadata`` của contract."""
    return {
        "source": str(metadata.get("source", "")),
        "title": str(metadata.get("title", "")),
        "doc_type": str(metadata.get("doc_type", "")),
        "url": metadata.get("url") or None,
        # index cũ có thể thiếu chunk_index; mặc định 0 để không vỡ contract.
        "chunk_index": int(metadata.get("chunk_index") or 0),
    }


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts theo EMBEDDING_PROVIDER trong .env.

    Task 5 import lại chính hàm này nên query và corpus luôn dùng chung model,
    dimension và cách normalize.
    """
    if not texts:
        return []
    provider = os.getenv("EMBEDDING_PROVIDER", EMBEDDING_PROVIDER)
    if provider not in SUPPORTED_EMBEDDING_PROVIDERS:
        raise ValueError(
            f"EMBEDDING_PROVIDER={provider!r} chưa được implement; "
            f"chọn một trong {SUPPORTED_EMBEDDING_PROVIDERS}."
        )
    
    if provider == "gemini":
        from google import genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")
        
        client = genai.Client(api_key=api_key)
        model_name = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-2")
        
        vectors = []
        # Process each text individually as API returns single embedding for batch
        for text in texts:
            response = client.models.embed_content(
                model=model_name,
                contents=[text]
            )
            # Extract the embedding values
            vectors.append(response.embeddings[0].values)
        
        return [[float(value) for value in vector] for vector in vectors]
    else:
        # sentence_transformers
        model = get_embedding_model()
        vectors = model.encode(
            texts,
            batch_size=EMBEDDING_BATCH_SIZE,
            normalize_embeddings=NORMALIZE_EMBEDDINGS,
        )
        return [[float(value) for value in vector] for vector in vectors]


def get_client():
    """Tạo và cache PersistentClient cho CHROMA_DIR (tránh mở client trùng)."""
    global _chroma_client, _chroma_client_path
    path = str(CHROMA_DIR)
    if _chroma_client is None or _chroma_client_path != path:
        import chromadb
        Path(path).mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=path)
        _chroma_client_path = path
    return _chroma_client


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    return get_client().get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document hợp lệ theo contract."""
    documents = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if path.name.startswith("."):
            continue
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        doc_type = "legal" if "legal" in path.parts else "news"
        document = {
            "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
            "content": content,
            "metadata": {
                "source": path.name,
                "title": _extract_title(
                    content,
                    path.stem.replace("-", " ").replace("_", " ").title(),
                ),
                "doc_type": doc_type,
                "url": _extract_url(content),
            },
        }
        # Fail fast nếu dữ liệu chuẩn hóa không khớp contract.
        validate_document(document)
        documents.append(document)
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có ``id`` ổn định và ``chunk_index`` liên tục.

    ``chunk_index`` được đánh lại từ 0 cho từng document nên chạy lại pipeline
    luôn sinh ra đúng bộ ``id`` cũ (upsert không tạo dữ liệu trùng).
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for document in documents:
        for chunk_index, text in enumerate(splitter.split_text(document["content"])):
            chunks.append({
                "id": f"{document['id']}::chunk-{chunk_index}",
                "content": text.strip(),
                "metadata": {
                    **document["metadata"],
                    "chunk_index": chunk_index,
                },
            })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm ``embedding`` vào từng chunk qua ``embed_texts`` (một provider duy nhất)."""
    if not chunks:
        return []
    vectors = embed_texts([chunk["content"] for chunk in chunks])
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB theo batch; chạy lại không tạo dữ liệu trùng."""
    if not chunks:
        return
    collection = get_collection()
    for start in range(0, len(chunks), UPSERT_BATCH_SIZE):
        batch = chunks[start:start + UPSERT_BATCH_SIZE]
        collection.upsert(
            ids=[chunk["id"] for chunk in batch],
            documents=[chunk["content"] for chunk in batch],
            embeddings=[chunk["embedding"] for chunk in batch],
            metadatas=[
                sanitize_metadata_for_chroma(chunk["metadata"]) for chunk in batch
            ],
        )


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index (validate contract trước khi ghi)."""
    documents = load_documents()
    if not documents:
        print(f"No documents found in {STANDARDIZED_DIR}")
        return

    chunks = chunk_documents(documents)
    for chunk in chunks:
        validate_document(chunk, require_chunk=True)

    embedded_chunks = embed_chunks(chunks)
    dimension = len(embedded_chunks[0]["embedding"]) if embedded_chunks else 0
    if dimension and dimension != EMBEDDING_DIM:
        print(
            f"Warning: embedding dimension {dimension} != EMBEDDING_DIM "
            f"{EMBEDDING_DIM}; set EMBEDDING_DIM and re-index before querying."
        )

    index_to_vectorstore(embedded_chunks)
    print(
        f"Indexed {len(embedded_chunks)} chunks from {len(documents)} documents "
        f"(embedding dim {dimension}, model {EMBEDDING_MODEL})"
    )


if __name__ == "__main__":
    run_pipeline()
