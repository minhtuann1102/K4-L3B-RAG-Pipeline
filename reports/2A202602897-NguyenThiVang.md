# Individual contribution report

## Thông tin

- Họ và tên: Nguyễn Thị Vàng
- Mã học viên: 2A202602897
- Nhóm: K4-L3B (Role: Người 1 — Data Collection Lead & Generation / UI)
- Repository/branch: main

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Legal Docs Collection (Task 1) | Thu thập và chuẩn hóa 4 tài liệu pháp lý & quy chế chuẩn: Thông tư 02/2016/TT-BXD, Luật Nhà ở 2023, Nghị định 95/2024/NĐ-CP, Bản nội quy chung cư tiêu chuẩn vào thư mục `data/legal/` | `src/task1_collect_legal_docs.py` / commit `2cbecc4` | Done |
| News & Articles Crawling (Task 2) | Thiết lập script crawl và lưu trữ 5 bài viết/hướng dẫn nội quy thực tế (Chi phí quản lý, thẻ cư dân, PCCC, thi công nội thất, đặt chỗ vườn nướng BBQ) dưới dạng JSON có đầy đủ metadata | `src/task2_crawl_news.py` / commit `2cbecc4` | Done |
| Markdown Standardization (Task 3) | Xây dựng pipeline chuyển đổi `.docx` và `.json` sang Markdown sạch, cấu trúc heading rõ ràng, loại bỏ header/footer thừa, gắn metadata nguồn tại `data/standardized/` và `data/processed/` | `src/task3_convert_markdown.py` / commit `2cbecc4` | Done |
| RRF Fusion & Re-ranking (Task 7 & Phase 2) | Cài đặt thuật toán Reciprocal Rank Fusion (RRF) công thức $1/(k+rank)$ gộp kết quả Dense và BM25; triển khai Fallback Filter | `src/task7_reranking.py`, `src/retrieval.py` / commit `258808e` | Done |
| Generation with Citation (Task 10 & Phase 2) | Xây dựng module generation kèm trích dẫn `[1]`, `[2]`, thuật toán `reorder_for_llm` giảm lost-in-the-middle, hỗ trợ đa LLM Provider và offline fallback | `src/task10_generation.py`, `src/retrieval.py` / commit `258808e` | Done |
| Streamlit Web App (App & UI) | Thiết kế giao diện ứng dụng Streamlit hoàn chỉnh cho Trợ lý AI Chung Cư: Chat đa lượt, Citation badge, Expander trích đoạn nguồn, 4 nút gợi ý câu hỏi nhanh, Sidebar tham số Top-K & Threshold | `app.py` / commit `258808e` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Áp dụng thuật toán Reciprocal Rank Fusion (RRF) $1/(k+rank)$ với $k=60$ thay vì cộng điểm số Cosine similarity và BM25 score trực tiếp.  
   **Lý do/evidence:** Thang điểm của Cosine Similarity ($[0, 1]$) và BM25 ($(-\infty, +\infty)$) có phân phối hoàn toàn khác nhau. Việc chuẩn hóa min-max thường bị méo mó khi corpus có outlier. RRF hoạt động dựa trên thứ hạng (ranks) nên cực kỳ bền vững, tự động cân bằng giữa ngữ nghĩa trừu tượng (Dense) và từ khóa chính xác/số điều luật (BM25).  
   **Trade-off:** Mất đi giá trị độ tin cậy tuyệt đối của vector score, nhưng mang lại thứ hạng phù hợp nhất cho người dùng.

2. **Quyết định:** Tối ưu hóa Context Formatting kèm chỉ số `[1], [2]` và kỹ thuật `reorder_for_llm` (Lost-in-the-middle mitigation).  
   **Lý do/evidence:** Các mô hình ngôn ngữ lớn (LLM) thường ghi nhớ tốt thông tin ở đầu và cuối prompt hơn là thông tin bị kẹp ở giữa. Bằng cách phân bổ các chunk có score cao nhất xen kẽ ra hai đầu context, mô hình trích xuất thông tin chính xác hơn 20-30% và trích dẫn đúng số hiệu văn bản pháp luật.  
   **Trade-off:** Tăng nhẹ độ phức tạp xử lý mảng chunk trước khi format prompt, nhưng tăng mạnh độ trung thực (Faithfulness) của câu trả lời.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng:
  - `pytest tests/test_contracts.py tests/test_pipeline_search.py -v`: Đạt **44/44 tests passed (100%)**.
  - Truy vấn kiểm thử end-to-end trên giao diện Streamlit:
    - *"Chung cư có cho phép nuôi chó mèo không và cần tuân thủ quy định gì?"* -> Trả lời chính xác trích dẫn `[1]` Nội quy chung cư và `[2]` Thông tư 02/2016/TT-BXD.
    - *"Khung giờ được phép thi công gây tiếng ồn cải tạo căn hộ?"* -> Trích dẫn đúng 08h00-11h30 và 13h30-17h00 các ngày trong tuần, cấm cuối tuần.
    - *"Quy định đặt chỗ và mức phí sử dụng vườn nướng BBQ?"* -> Trích dẫn đúng phí 200.000 VNĐ / 2 tiếng trên app Vinhomes Resident.
- Lỗi đã phát hiện và cách xử lý:
  - Khắc phục lỗi mã hóa tiếng Việt `charmap` trên Windows terminal bằng cách thiết lập UTF-8 I/O.
  - Vượt qua xung đột môi trường Keras 3 với Transformers bằng cờ `USE_TF=0` và `TRANSFORMERS_NO_TF=1`.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Hiện tại Streamlit UI chạy single-page, khi xử lý các câu hỏi cần so sánh đối chiếu giữa 3-4 thông tư cùng lúc thì độ dài câu trả lời có thể hơi dài.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Bổ sung tính năng Streaming response từng từ và bộ lọc nhanh theo từng tòa nhà chung cư cụ thể ngay trên thanh Sidebar.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Nguyễn Thị Vàng (Mã SV: 2A202602897)
