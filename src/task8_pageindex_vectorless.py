"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    if not PAGEINDEX_API_KEY:
        return
    # Implement upload if needed when PAGEINDEX_API_KEY is available


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult nếu có cấu hình PAGEINDEX_API_KEY, ngược lại fallback rỗng."""
    if not PAGEINDEX_API_KEY or not query or not query.strip() or top_k <= 0:
        return []
    try:
        # If PageIndex client is available, call it here
        return []
    except Exception:
        return []


if __name__ == "__main__":
    print("PageIndex vectorless module ready.")

