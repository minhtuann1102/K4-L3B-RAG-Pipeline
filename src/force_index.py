"""
Force indexing script với SSL fix.
Chạy: python -m src.force_index
"""
import os
import ssl

# 1. Bỏ qua xác thực SSL
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["PYTHONHTTPSVERIFY"] = "0"
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""

# Dùng mirror nếu HF bị chặn
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import chromadb
from src.task4_chunking_indexing import (
    load_documents,
    chunk_documents,
    embed_chunks,
    index_to_vectorstore,
    get_collection,
)

def main():
    print("=" * 60)
    print("Force Index Script")
    print("=" * 60)

    # Check current state
    collection = get_collection()
    print(f"\nCollection count trước khi index: {collection.count()}")

    # Load documents
    print("\n1. Loading documents...")
    documents = load_documents()
    print(f"   Loaded {len(documents)} documents")
    if not documents:
        print("   ERROR: No documents found in data/standardized/")
        return

    # Chunk documents
    print("\n2. Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"   Created {len(chunks)} chunks")

    # Embed chunks
    print("\n3. Embedding chunks...")
    print("   (This may take a while for the first run)")
    embedded_chunks = embed_chunks(chunks)
    print(f"   Embedded {len(embedded_chunks)} chunks")

    # Index to vectorstore
    print("\n4. Indexing to ChromaDB...")
    index_to_vectorstore(embedded_chunks)

    # Verify
    print("\n5. Verifying...")
    collection = get_collection()
    print(f"   Collection count sau khi index: {collection.count()}")

    print("\n" + "=" * 60)
    print("Indexing complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
