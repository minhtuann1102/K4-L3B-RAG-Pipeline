# Báo cáo cá nhân - Nguyễn Minh Tuấn (Mã SV: 2A202602420)

**Vai trò trong nhóm:** NGƯỜI 1 — Data Collection Lead & Generation / UI  
**Chủ đề dự án:** Trợ lý AI Tư vấn Nội quy Quản lý & Sử dụng Nhà Chung cư (Condominium Management RAG Assistant)  
**Khóa học / Lab:** VINUNI AI - DAY 8: Advanced RAG Pipeline  

---

## 1. Công việc đã thực hiện

### 1.1. Phase 1: Data Collection & Standardization (Data Lead)
- **Bước 1.1 (Chọn chủ đề):** Thống nhất với nhóm chọn domain mang tính thực tế cao: *"Nội quy Quản lý, Sử dụng Nhà Chung cư"* (quy chế pháp lý, quyền và nghĩa vụ cư dân, ban quản trị, chi phí vận hành, an toàn PCCC, giờ giấc thi công cải tạo, tiện ích nội khu).
- **Bước 1.2 (Thu thập tài liệu pháp lý):** Viết script [src/task1_collect_legal_docs.py](file:///d:/Download/VINUNI%20AI/DAY8/K4-L3B-RAG-Pipeline-NguyenMinhTuan-2A202602420/src/task1_collect_legal_docs.py), thu thập 4 tài liệu pháp lý và quy chuẩn gồm:
  1. `01_thong_tu_02_2016_tt_bxd_quy_che_nha_chung_cu`: Quy chế quản lý, sử dụng nhà chung cư (Bộ Xây dựng).
  2. `02_luat_nha_o_2023_quy_dinh_quan_ly_chung_cu`: Luật Nhà ở 2023 (Chương IX về nhà chung cư).
  3. `03_nghi_dinh_95_2024_nd_cp_quan_ly_su_dung_chung_cu`: Nghị định 95/2024/NĐ-CP (Kinh phí bảo trì 2%, hồ sơ bàn giao, đơn vị vận hành).
  4. `04_mau_noi_quy_quan_ly_su_dung_nha_chung_cu_chuan`: Bản nội quy mẫu tiêu chuẩn tòa nhà căn hộ chung cư.
- **Bước 1.3 (Crawl tin tức & quy định thực tế):** Viết script [src/task2_crawl_news.py](file:///d:/Download/VINUNI%20AI/DAY8/K4-L3B-RAG-Pipeline-NguyenMinhTuan-2A202602420/src/task2_crawl_news.py) crawl và lưu trữ 5 bài viết JSON đầy đủ metadata (`url`, `title`, `date_crawled`, `content_markdown`):
  1. `article_01.json`: Chi phí ở chung cư mỗi tháng bao gồm những gì?
  2. `article_02.json`: Thẻ cư dân Vinhomes - Hướng dẫn đăng ký và quyền lợi.
  3. `article_03.json`: Nội quy quản lý sử dụng tòa nhà căn hộ chung cư Vinhomes.
  4. `article_04.json`: Quy định thi công cải tạo nội thất căn hộ tòa nhà Vinhomes.
  5. `article_05.json`: Quy định đặt chỗ và nội quy sử dụng vườn nướng BBQ Vinhomes Grand Park.
- **Bước 1.4 (Chuẩn hóa Markdown sạch):** Viết script [src/task3_convert_markdown.py](file:///d:/Download/VINUNI%20AI/DAY8/K4-L3B-RAG-Pipeline-NguyenMinhTuan-2A202602420/src/task3_convert_markdown.py) chuyển đổi toàn bộ tài liệu sang định dạng Markdown chuẩn hóa tại `data/standardized/` và `data/processed/`, có header metadata rõ ràng và loại bỏ ký tự/tiêu đề thừa.
- **Bước 1.5 (Sync Git):** Commit và push toàn bộ dữ liệu sạch lên nhánh `main` để Người 2 và Người 3 pull về làm indexing và đánh giá dataset.

### 1.2. Phase 2: Integration, Generation & UI
- **Bước 1.6 (RRF Fusion):** Triển khai hàm `reciprocal_rank_fusion` trong [src/retrieval.py](file:///d:/Download/VINUNI%20AI/DAY8/K4-L3B-RAG-Pipeline-NguyenMinhTuan-2A202602420/src/retrieval.py) và `rerank_rrf` trong [src/task7_reranking.py](file:///d:/Download/VINUNI%20AI/DAY8/K4-L3B-RAG-Pipeline-NguyenMinhTuan-2A202602420/src/task7_reranking.py) áp dụng công thức RRF $1/(k+rank)$ để kết hợp ưu thế của Semantic Search (Dense) và Lexical Search (BM25).
- **Bước 1.7 (Fallback Logic):** Triển khai hàm `fallback_filter` và cơ chế fallback tự động theo ngưỡng tin cậy trong [src/task9_retrieval_pipeline.py](file:///d:/Download/VINUNI%20AI/DAY8/K4-L3B-RAG-Pipeline-NguyenMinhTuan-2A202602420/src/task9_retrieval_pipeline.py), tránh crash khi gặp câu hỏi ngoài phạm vi tri thức.
- **Bước 1.8 (Generation có Citation):** Xây dựng module sinh câu trả lời trong [src/task10_generation.py](file:///d:/Download/VINUNI%20AI/DAY8/K4-L3B-RAG-Pipeline-NguyenMinhTuan-2A202602420/src/task10_generation.py):
  - Áp dụng thuật toán `reorder_for_llm` đảo thứ tự chunks để giảm thiểu hiện tượng *Lost in the Middle*.
  - Định dạng context rõ ràng kèm nhãn `[1]`, `[2]`, tiêu đề và file nguồn.
  - Hỗ trợ đa dạng LLM Provider (`gemini`, `openai`, `anthropic`) và có fallback thông minh khi chạy offline.
- **Bước 1.9 (Giao diện Streamlit UI):** Xây dựng ứng dụng hoàn chỉnh trong [app.py](file:///d:/Download/VINUNI%20AI/DAY8/K4-L3B-RAG-Pipeline-NguyenMinhTuan-2A202602420/app.py):
  - Giao diện chat trực quan, hiện đại, hiển thị câu trả lời với trích dẫn `[1]`, `[2]`.
  - Hộp mở rộng (Expander) hiển thị chi tiết nguồn trích dẫn, điểm số retrieval score và trích đoạn minh chứng.
  - 4 nút bấm gợi ý câu hỏi phổ biến để demo nhanh.
  - Sidebar cho phép người dùng tùy chỉnh tham số Top-K, bật/tắt Hybrid RRF và điều chỉnh ngưỡng lọc.

---

## 2. Khó khăn gặp phải và Cách giải quyết

1. **Lỗi mã hóa font chữ tiếng Việt (charmap codec / cp1252) trên terminal Windows:**
   - *Khó khăn:* Khi in log tiêu đề bài viết tiếng Việt có dấu, console Windows bị lỗi `UnicodeEncodeError`.
   - *Giải pháp:* Chuẩn hóa log in ra terminal dưới dạng an toàn, sử dụng UTF-8 encoding khi ghi và đọc toàn bộ file dữ liệu Markdown/JSON.

2. **Xung đột môi trường giữa TensorFlow/Keras và SentenceTransformers:**
   - *Khó khăn:* Thư viện Transformers cảnh báo xung đột phiên bản Keras 3 khi nạp model embedding `bge-m3`.
   - *Giải pháp:* Thiết lập các biến môi trường `USE_TF=0` và `TRANSFORMERS_NO_TF=1` ngay từ đầu chương trình để ưu tiên sử dụng PyTorch thuần túy, giúp tốc độ nạp model nhanh và ổn định 100%.

3. **Hiện tượng Lost in the Middle khi đưa nhiều chunks vào LLM Context:**
   - *Khó khăn:* Khi đưa 5-8 chunks vào context, LLM thường chú ý nhiều vào đoạn đầu và đoạn cuối mà bỏ quên các đoạn ở giữa.
   - *Giải pháp:* Triển khai hàm `reorder_for_llm` phân bổ xen kẽ các chunk có độ liên quan cao nhất ra hai đầu (đầu và cuối) danh sách context.

---

## 3. Đóng góp vào nhóm

- Cung cấp toàn bộ bộ dữ liệu tri thức chuẩn mực (4 tài liệu pháp lý + 5 cẩm nang thực tế) đúng chuẩn Markdown cho toàn đội ngũ.
- Hoàn thiện luồng kết nối từ Retrieval (Semantic + BM25 + RRF) đến Generation (LLM với citations).
- Thiết kế giao diện demo tương tác Streamlit chuyên nghiệp, mượt mà, giúp nhóm sẵn sàng thuyết trình và nghiệm thu kết quả.
- Đảm bảo 100% các bài kiểm thử hợp đồng dữ liệu và pipeline search (`test_contracts.py`, `test_pipeline_search.py`) đều pass (44/44 tests).

---

## 4. Bài học kinh nghiệm

- Hiểu sâu sắc cơ chế hoạt động của **Hybrid Search kết hợp RRF (Reciprocal Rank Fusion)**: sự phối hợp giữa dense vector (bắt ngữ nghĩa trừu tượng) và sparse BM25 (bắt chính xác từ khóa, số điều luật) giúp tăng vượt bậc độ chính xác so với việc chỉ dùng đơn lẻ một phương pháp.
- Nắm vững quy trình chuẩn hóa dữ liệu (ETL pipeline) cho hệ thống RAG: dữ liệu đầu vào càng sạch, có cấu trúc heading rõ ràng và đầy đủ metadata thì chất lượng trích xuất và câu trả lời sinh ra càng chính xác và ít bị ảo giác (hallucination).
- Tầm quan trọng của việc thiết lập Contract và kiểm thử tự động (Unit Tests) trong làm việc nhóm để các thành viên phối hợp nhịp nhàng mà không bị xung đột mã nguồn.
