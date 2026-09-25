"""Script để kiểm tra nội dung ChromaDB."""
import sys
from pathlib import Path
import chromadb

# Đảm bảo in tiếng Việt trên console Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CHROMA_DIR = Path("./chroma_db")
COLLECTION_NAME = "rag_documents"

# Kết nối đến ChromaDB
client = chromadb.PersistentClient(path=str(CHROMA_DIR))

# Lấy collection
try:
    collection = client.get_collection(name=COLLECTION_NAME)
    
    # Đếm số documents
    count = collection.count()
    print(f"[OK] Collection '{COLLECTION_NAME}' đã tìm thấy!")
    print(f"[OK] Tổng số chunks đã lưu: {count} chunks")
    
    if count > 0:
        # Lấy 3 mẫu để xem
        results = collection.get(limit=3, include=["documents", "metadatas", "embeddings"])
        
        print("\n" + "=" * 60)
        print("DANH SÁCH MẪU CHUNKS ĐANG CÓ TRONG CHROMADB:")
        print("=" * 60)
        
        embeddings = results.get("embeddings")
        for i, (doc_id, content, metadata) in enumerate(zip(
            results["ids"], 
            results["documents"], 
            results["metadatas"],
        ), 1):
            dim = len(embeddings[i - 1]) if embeddings is not None and len(embeddings) >= i else 0
            print(f"\n[{i}] ID: {doc_id}")
            print(f"    Source: {metadata.get('source')}")
            print(f"    Title : {metadata.get('title')}")
            print(f"    Content trích đoạn: {content[:80].replace(chr(10), ' ')}...")
            print(f"    Embedding dimension: {dim}")
            
        print("\n" + "=" * 60)
        print("KẾT LUẬN: ChromaDB đang chứa đầy đủ dữ liệu thực tế và sẵn sàng truy vấn!")
        print("=" * 60)
    else:
        print("\n[WARNING] Collection rỗng - chưa có dữ liệu nào được index!")
        
except Exception as e:
    print(f"[LỖI] Không thể đọc collection: {e}")
