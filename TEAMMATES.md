# Thành viên nhóm K4-L3B — Day 8 RAG Pipeline

> Nguồn đối chiếu: [`WORK_PLAN.md`](WORK_PLAN.md), [`README.md`](README.md), lịch sử commit của repo (`git log --all --name-status`) và các báo cáo cá nhân trong [`reports/`](reports/).
> Cập nhật lần cuối: 25/09/2026 — nhánh `main`, HEAD `0a832dc`.

## Thông tin nhóm

| Trường                 | Giá trị                                                               |
| ---------------------- | --------------------------------------------------------------------- |
| Nhóm                   | K4-L3B                                                                |
| Repository             | `K4-L3B-RAG-Pipeline-NguyenMinhTuan-2A202602420` (fork từ `VinUni-AI20k/K4-L3B-RAG-Pipeline`) |
| Học viên đứng tên repo | Nguyễn Minh Tuấn — 2A202602420                                        |
| Chủ đề                 | Trợ lý AI tư vấn nội quy quản lý & sử dụng nhà chung cư               |
| Số thành viên          | 3 (theo `WORK_PLAN.md`: "Nhóm: 3 người")                              |
| Nhánh tích hợp         | `main`                                                                |

## 1. Bảng tổng quan thành viên

| STT | Họ và tên | Mã học viên | GitHub | Vai trò | Nhánh / phần việc |
| --: | --- | --- | --- | --- | --- |
| 1 | Nguyễn Thị Vang | 2A202602897 | `vanganh2301` | **NGƯỜI 1 — Data Collection Lead & Generation/UI** | Làm trực tiếp trên `main` — commit `2cbecc4` (data), `258808e` (RRF/fallback/generation/UI) |
| 2 | Nguyễn Minh Tuấn | 2A202602420 | `minhtuann1102` | **NGƯỜI 2 — Pipeline & Search Lead (kèm unit test/QA)** | Nhánh `feature/2A202602420-pipeline-search` → merge vào `main` bằng `acf0855`; commit `26d22a2`, `245bf63`, `32f5103` |
| 3 | Nguyễn Minh Thắng | *chưa có trong repo — xem mục 5* | `Thang-Nguyen-Minh` | **NGƯỜI 3 — Evaluation & Integration Prep** | Làm trực tiếp trên `main` — commit `66e2c03`, `0e8ab31` |

## 2. Chi tiết từng thành viên

### 👤 1. Nguyễn Thị Vang — 2A202602897 — `vanganh2301`

**Vai trò:** NGƯỜI 1 — Data Collection Lead (Phase 1) & Generation / UI (Phase 2)

| Module/deliverable | Việc đã làm | File | Commit |
| --- | --- | --- | --- |
| Task 1 — Thu thập tài liệu pháp lý | 4 tài liệu (.docx) về quản lý/sử dụng nhà chung cư | `src/task1_collect_legal_docs.py`, `data/legal/`, `data/landing/legal/` | `2cbecc4` |
| Task 2 — Crawl news/articles | 5 bài viết kèm metadata (`url`, `title`, `date_crawled`, `content_markdown`) | `src/task2_crawl_news.py`, `data/news/article_01..05.json` | `2cbecc4` |
| Task 3 — Convert Markdown | Chuẩn hoá toàn bộ docx/JSON sang Markdown sạch | `src/task3_convert_markdown.py`, `data/processed/`, `data/standardized/` | `2cbecc4` |
| Task 7 — RRF reranking | Gộp thứ hạng dense + BM25 theo công thức 1/(k+rank) | `src/retrieval.py` (`reciprocal_rank_fusion`), `src/task7_reranking.py` (`rerank_rrf`) | `258808e` |
| Task 9 — Retrieval pipeline + fallback | Fallback theo cosine score gốc của dense, chỉ fuse RRF một lần | `src/task9_retrieval_pipeline.py` (`fallback_filter`) | `258808e` |
| Task 10 — Generation kèm citation | Sinh câu trả lời có citation `[1]`, `[2]`, … và danh sách nguồn | `src/task10_generation.py` (`generate_answer`) | `258808e` |
| Streamlit UI | Chatbot hiển thị câu trả lời và nguồn đã dùng | `app.py` | `258808e` |

- Báo cáo cá nhân: `group_project/individual/INDIVIDUAL_REPORT_NGUYEN_MINH_TUAN.md` (commit `8c74851`, hiện **đang bị xoá ở working tree** — xem mục 5).

### 👤 2. Nguyễn Minh Tuấn — 2A202602420 — `minhtuann1102`

**Vai trò:** NGƯỜI 2 — Pipeline & Search Lead (Phase 1) & Testing / QA (Phase 2)

| Module/deliverable | Việc đã làm | File | Commit |
| --- | --- | --- | --- |
| Task 4 — Chunking & Indexing | `chunk_documents()` (`RecursiveCharacterTextSplitter`, size 500 / overlap 50), chuẩn hoá metadata chunk, nhúng vector bằng `BAAI/bge-m3` và upsert vào ChromaDB | `src/task4_chunking_indexing.py` | `26d22a2`, `32f5103` |
| Task 5 — Dense semantic search | Truy vấn cosine từ ChromaDB, đổi distance → similarity score, trả về đúng schema `SearchResult` | `src/task5_semantic_search.py` | `26d22a2` |
| Task 6 — Lexical BM25 search | Tokenizer tiếng Việt giữ dấu, chỉ mục `BM25Okapi`, xử lý IDF ≤ 0 và tie-breaking | `src/task6_lexical_search.py` | `26d22a2` |
| Unit test tầng search | 29 test cho chunking + dense + BM25, coverage 91% cho 3 module | `tests/test_pipeline_search.py` | `26d22a2` |
| Kiểm chứng ChromaDB / Gemini | Script kiểm tra DB và embedding model | `check_chroma.py`, `check_sqlite.py`, `list_gemini_models.py`, `test_gemini_embed.py` | `32f5103` |

- Báo cáo cá nhân: [`reports/2A202602420-NguyenMinhTuan.md`](reports/2A202602420-NguyenMinhTuan.md) (commit `245bf63`).

### 👤 3. Nguyễn Minh Thắng — *mã học viên cần xác nhận* — `Thang-Nguyen-Minh`

**Vai trò:** NGƯỜI 3 — Evaluation & Integration Prep

| Module/deliverable | Việc đã làm | File | Commit |
| --- | --- | --- | --- |
| Golden dataset | Golden dataset 19 câu hỏi (in-domain + out-of-domain để test fallback) | `group_project/evaluation/golden_dataset.json` | `66e2c03`, `0e8ab31` |
| Evaluation framework | `evaluate_retrieval()` (Precision@K, Recall@K, MRR) và `evaluate_generation()` (faithfulness, answer relevance) | `src/evaluation.py` | `66e2c03` |
| Script chạy đánh giá A/B | So sánh cấu hình dense-only vs hybrid + RRF | `src/run_evaluation.py` | `66e2c03` |

- Báo cáo cá nhân: **chưa có** trong `reports/` (cần bổ sung theo template `reports/INDIVIDUAL_REPORT.md`).

## 3. Phân chia theo task trong `WORK_PLAN.md`

| Task | Deliverable | Người phụ trách | Trạng thái |
| --- | --- | --- | --- |
| Task 1 | ≥3 tài liệu pháp lý | Nguyễn Thị Vang | Done |
| Task 2 | ≥5 bài viết/news có metadata | Nguyễn Thị Vang | Done |
| Task 3 | Markdown chuẩn hoá trong `data/processed/`, `data/standardized/` | Nguyễn Thị Vang | Done |
| Task 4 | Chunking + index ChromaDB | Nguyễn Minh Tuấn | Done |
| Task 5 | Dense search (schema `SearchResult`) | Nguyễn Minh Tuấn | Done |
| Task 6 | BM25 search (cùng schema với dense) | Nguyễn Minh Tuấn | Done |
| Task 7 | RRF fusion | Nguyễn Thị Vang | Done |
| Task 8 | Vectorless / PageIndex | Nguyễn Thị Vang (stub an toàn) | N/A — `src/task8_pageindex_vectorless.py` chỉ giữ stub trả `[]` khi thiếu `PAGEINDEX_API_KEY`, không dùng trong pipeline chính |
| Task 9 | Retrieval pipeline + fallback theo cosine gốc | Nguyễn Thị Vang | Done |
| Task 10 | Generation có citation | Nguyễn Thị Vang | Done |
| UI | Streamlit chatbot (`app.py`) | Nguyễn Thị Vang | Done |
| Evaluation | Golden dataset + 4 metric + A/B | Nguyễn Minh Thắng | Partial — dataset xong, `group_project/evaluation/RESULT.md` còn `TODO` |

## 4. Nhánh làm việc

| Nhánh | Người dùng | Nội dung | Trạng thái |
| --- | --- | --- | --- |
| `main` | cả nhóm | Nhánh tích hợp, HEAD `0a832dc` | Active |
| `feature/2A202602420-pipeline-search` | Nguyễn Minh Tuấn | Chunking → dense search → BM25 → unit test tầng search | Đã merge vào `main` (`acf0855`), nhánh vẫn còn ở `origin` |
| *(chưa tách riêng)* | Nguyễn Thị Vang | Data collection + RRF/fallback/generation/UI | Commit trực tiếp lên `main` |
| *(chưa tách riêng)* | Nguyễn Minh Thắng | Evaluation + golden dataset + `src/evaluation.py` | Commit trực tiếp lên `main` |

**Quy ước đặt tên nhánh:** `feature/<mã học viên>-<phần việc>`, ví dụ `feature/2A202602897-data-collection` hoặc `feature/<mã học viên>-evaluation`. Hai phần việc đang push trực tiếp lên `main` nên được tách nhánh riêng nếu còn tiếp tục phát triển.

## 5. Việc cần thống nhất / bổ sung

- [ ] **Mã học viên của Nguyễn Minh Thắng** chưa xuất hiện ở bất kỳ file/commit nào trong repo → cần điền vào bảng mục 1.
- [ ] **Báo cáo cá nhân còn thiếu:** README yêu cầu mỗi thành viên nộp một báo cáo `reports/<student-id>-<short-name>.md`; hiện chỉ có `reports/2A202602420-NguyenMinhTuan.md`.
- [ ] **Không nhất quán về vai trò của Nguyễn Minh Tuấn:** `group_project/individual/INDIVIDUAL_REPORT_NGUYEN_MINH_TUAN.md` (thêm ở commit `8c74851`) ghi *"NGƯỜI 1 — Data Collection Lead & Generation/UI"*, trong khi `reports/2A202602420-NguyenMinhTuan.md` (commit `245bf63`) ghi *"NGƯỜI 2 — Pipeline & Search Lead"*. Cần thống nhất lại để tránh trùng ownership khi chấm điểm.
- [ ] `group_project/individual/INDIVIDUAL_REPORT_NGUYEN_MINH_TUAN.md` đang bị xoá ở working tree (trạng thái `D`, chưa commit) → quyết định giữ hay xoá rồi commit cho sạch.
- [ ] `group_project/evaluation/RESULT.md` còn toàn bộ `TODO`, chưa đạt `tests/test_acceptance.py::test_evaluation_report_is_completed`.
