"""Kiểm tra nội dung SQLite của ChromaDB."""
import sqlite3

conn = sqlite3.connect('chroma_db/chroma.sqlite3')
cursor = conn.cursor()

# Liệt kê các bảng
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [row[0] for row in cursor.fetchall()]
print(f"Tables: {tables}")

# Kiểm tra collections
if 'collections' in tables:
    cursor.execute('SELECT * FROM collections')
    collections = cursor.fetchall()
    print(f"\nCollections ({len(collections)}):")
    for col in collections:
        print(f"  {col}")

# Kiểm tra segments
if 'segments' in tables:
    cursor.execute('SELECT COUNT(*) FROM segments')
    count = cursor.fetchone()[0]
    print(f"\nSegments count: {count}")

# Kiểm tra embeddings
if 'embeddings' in tables:
    cursor.execute('SELECT COUNT(*) FROM embeddings')
    count = cursor.fetchone()[0]
    print(f"Embeddings count: {count}")
    
if 'embedding_fulltext_search' in tables:
    cursor.execute('SELECT COUNT(*) FROM embedding_fulltext_search')
    count = cursor.fetchone()[0]
    print(f"Fulltext search count: {count}")

conn.close()
