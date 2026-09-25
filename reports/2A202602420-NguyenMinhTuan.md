# Individual contribution report

## Thông tin

- Họ và tên: Nguyễn Minh Tuấn
- Mã học viên: 2A202602420
- Nhóm: K4-L3B (Role: Người 2 — Pipeline & Search Lead)
- Repository/branch: main

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Chunking & Indexing (Task 4) | Thiết kế chia văn bản theo `RecursiveCharacterTextSplitter` (chunk_size=500, overlap=50); chuẩn hóa metadata và trích xuất title H1, URL nguồn; nhúng vector batch bằng `BAAI/bge-m3` và upsert vào ChromaDB | `src/task4_chunking_indexing.py` / commit `26d22a2` | Done |
| Dense Search (Task 5) | Truy vấn cosine similarity từ ChromaDB bằng chính vectorizer của Task 4; xử lý chuyển đổi distance sang similarity score; chuẩn hóa metadata đầu ra về `ChunkMetadata` | `src/task5_semantic_search.py` / commit `26d22a2` | Done |
| Lexical BM25 Search (Task 6) | Xây dựng bộ tách từ tiếng Việt giữ nguyên dấu; tạo chỉ mục `BM25Okapi` trên cùng corpus chunks; giải quyết trường hợp IDF âm/bằng 0 và tie-breaking | `src/task6_lexical_search.py` / commit `26d22a2` | Done |
| QA & Unit Testing | Viết bộ 29 unit/integration tests cho module tìm kiếm, mock ChromaDB/BM25, đo coverage đạt 96% | `tests/test_pipeline_search.py` / commit `26d22a2` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Chuẩn hóa cơ chế lưu và đọc metadata trong ChromaDB (`sanitize_metadata_for_chroma` và `normalize_chroma_metadata`).  
   **Lý do/evidence:** Thư viện `chromadb` 1.5.9 tự động loại bỏ các trường có giá trị `None` (ví dụ `url: None`), dẫn đến việc khi query ra metadata bị thiếu trường và vi phạm contract `validate_document(require_chunk=True)`. Tôi đã xử lý ép `None` thành `""` khi upsert và khôi phục ngược lại thành `None` khi đọc ra.  
   **Trade-off:** Tăng một bước duyệt qua dict metadata trước và sau khi truy vấn, nhưng đảm bảo tuyệt đối tính toàn vẹn dữ liệu và pass 100% test contract.

2. **Quyết định:** Không lọc kết quả BM25 bằng điều kiện `score > 0` và sort ổn định theo `(-score, vị trí corpus)`.  
   **Lý do/evidence:** Với tập dữ liệu đặc thù hoặc nhỏ, các từ khóa xuất hiện ở đa số chunk sẽ có IDF bằng 0 hoặc thậm chí mang giá trị âm trong công thức `BM25Okapi`. Nếu lọc `score > 0` thì query khớp chính xác từ khóa vẫn bị trả về rỗng. Thay vào đó, tôi chỉ lọc các chunk có tập token giao nhau với query (`query_token_set & tokens`).  
   **Trade-off:** Cần lưu thêm tập `token_sets` cho từng chunk trong bộ nhớ cache để kiểm tra giao tập từ, bù lại kết quả tìm kiếm chính xác và ổn định giữa các lần chạy.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng:
  - `pytest tests/test_contracts.py -k "chunk or search" -v`: kiểm tra 4 contract tests gốc.
  - `pytest tests/test_pipeline_search.py --cov=src.task4_chunking_indexing --cov=src.task5_semantic_search --cov=src.task6_lexical_search`: kiểm tra 29 unit tests mở rộng.
- Kết quả trước/sau nếu có:
  - Trước: Module ném `NotImplementedError`, test contract fail 100%.
  - Sau: 27/27 tests passed, 2 tests skipped (dành cho integration RRF/fallback khi nhóm ghép nối), test coverage cho 3 module search đạt 96% (vượt mục tiêu ≥80%).
- Lỗi đã phát hiện và cách xử lý:
  - Lỗi `test_search_result_validator_checks_order_method_and_uniqueness` fail khi có duplicate ID: đã thêm `seen_ids` filter cho cả semantic search và lexical search.
  - Lỗi `np.argsort` gây xáo trộn thứ tự khi nhiều chunk có cùng điểm số BM25: đã chuyển sang sort theo tuple `(-score, index)`.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Model embedding `BAAI/bge-m3` có chất lượng biểu diễn tiếng Việt rất tốt nhưng kích thước lớn (~2.2GB), khi nạp lần đầu trên máy tính cá nhân tốn khoảng 5–8 giây.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Triển khai thêm cơ chế quantization (ONNX runtime hoặc int8) cho embedding model để giảm tiêu hao RAM và tăng tốc độ truy vấn dense search gấp 2–3 lần.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Nguyễn Minh Tuấn
