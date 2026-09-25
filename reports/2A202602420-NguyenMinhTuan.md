# Individual contribution report

## Thông tin

- Họ và tên: Nguyễn Minh Tuấn
- Mã học viên: 2A202602420
- Nhóm: K4-L3B — vai trò **NGƯỜI 2: Pipeline & Search Lead**
- Repository/branch: `feature/2A202602420-pipeline-search` (đã merge vào `main` bằng merge commit `acf0855`)

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 4 — Chunking & Indexing | Thiết kế `chunk_documents()` dùng `RecursiveCharacterTextSplitter` (chunk_size=500, overlap=50); chuẩn hóa metadata chunk (`source`, `page`, `title` H1, `url`); nhúng vector theo batch bằng `BAAI/bge-m3` và upsert vào ChromaDB | `src/task4_chunking_indexing.py` / commit `26d22a2`, bổ sung phần kiểm chứng ChromaDB + Gemini tại commit `32f5103` | Done |
| Task 5 — Dense semantic search | `dense_search(query, top_k)` truy vấn cosine từ ChromaDB bằng đúng vectorizer của Task 4; chuyển `distance` sang similarity score; chuẩn hóa metadata trả về thành `ChunkMetadata`; loại trùng `doc_id` | `src/task5_semantic_search.py` / commit `26d22a2` | Done |
| Task 6 — Lexical BM25 search | Tokenizer tiếng Việt giữ dấu; dựng chỉ mục `BM25Okapi` trên đúng corpus chunks; xử lý trường hợp IDF ≤ 0 và tie-breaking | `src/task6_lexical_search.py` / commit `26d22a2` | Done |
| QA & unit test cho tầng search | 29 test unit/integration cho chunking + dense + BM25 (mock ChromaDB/BM25) và đo coverage cho 3 module | `tests/test_pipeline_search.py` / commit `26d22a2` | Done |

Tôi không phụ trách Task 1/2/3 (thu thập – chuẩn hóa dữ liệu) và không phụ trách phần RRF/fallback/generation/Streamlit UI; các phần đó do thành viên khác thực hiện ở commit `2cbecc4` và `258808e`.

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Chuẩn hóa cơ chế lưu/đọc metadata trong ChromaDB bằng `sanitize_metadata_for_chroma()` và `normalize_chroma_metadata()`.  
   **Lý do/evidence:** `chromadb` 1.5.9 tự loại bỏ các trường metadata có giá trị `None` (ví dụ `url: None`) khi upsert, nên khi query ra metadata bị thiếu trường và vi phạm `validate_document(require_chunk=True)` trong `src/contracts.py`. Tôi ép `None` → `""` khi upsert và khôi phục `""` → `None` khi đọc.  
   **Trade-off:** Thêm một lượt duyệt dict metadata trước/sau truy vấn, bù lại dữ liệu luôn đúng contract.

2. **Quyết định:** Không lọc kết quả BM25 bằng điều kiện `score > 0`, thay vào đó lọc theo giao tập token và sort ổn định theo `(-score, vị trí corpus)`.  
   **Lý do/evidence:** Với corpus nhỏ, từ khóa xuất hiện ở đa số chunk khiến IDF = 0 hoặc mang giá trị âm trong `BM25Okapi`; nếu lọc `score > 0` thì query khớp chính xác (ví dụ truy vấn số điều luật) vẫn bị trả về rỗng.  
   **Trade-off:** Phải lưu thêm `token_sets` cho từng chunk trong bộ nhớ cache để kiểm tra giao tập token, bù lại kết quả search chính xác và ổn định giữa các lần chạy.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng:
  - `.venv\Scripts\python.exe -m pytest tests/test_pipeline_search.py tests/test_contracts.py -q` → **44 passed** (29 test của tôi + 15 contract test).
  - `.venv\Scripts\python.exe -m pytest tests/test_pipeline_search.py --cov=src.task4_chunking_indexing --cov=src.task5_semantic_search --cov=src.task6_lexical_search --cov-report=term -q` → **29 passed**, coverage **91%** (220 statements, 19 miss).
- Kết quả trước/sau nếu có:
  - Trước: Task 4/5/6 còn `NotImplementedError`, contract test của tầng search fail.
  - Sau: 44 test của tầng search + contract pass; coverage 3 module search đạt 91% (mục tiêu ≥80%).
- Lỗi đã phát hiện và cách xử lý:
  - `test_search_result_validator_checks_order_method_and_uniqueness` fail khi kết quả có duplicate ID → thêm bộ lọc `seen_ids` cho cả dense search và BM25 search.
  - `np.argsort` làm xáo trộn thứ tự khi nhiều chunk cùng điểm BM25 → chuyển sang sort theo tuple `(-score, index)`.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: model embedding `BAAI/bge-m3` cho chất lượng tiếng Việt tốt nhưng nặng (~2.2GB), lần nạp đầu tốn khoảng 5–8 giây; coverage tầng search hiện là 91%, phần chưa phủ chủ yếu là nhánh lỗi khi thiếu model/DB.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: lượng tử hoá embedding model (ONNX runtime hoặc int8) để giảm RAM và tăng tốc truy vấn dense search.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Nguyễn Minh Tuấn

