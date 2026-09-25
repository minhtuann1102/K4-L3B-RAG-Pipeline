# Báo cáo cá nhân - Nguyễn Minh Thắng

## Thông tin

- Họ và tên: Nguyễn Minh Thắng
- Mã sinh viên: 2A202602706
- Nhóm: K4-L3B
- Repository/branch: `K4-L3B-RAG-Pipeline-NguyenMinhTuan-2A202602420` / `main`
- Vai trò: Thành viên 3 — Evaluation & Integration; thực hiện thêm Phase 3 finalization

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Golden dataset | Chuẩn hóa 19 câu hỏi (16 in-domain, 3 out-of-domain) về schema `question`, `expected_answer`, `expected_context`. | `group_project/evaluation/golden_dataset.json`; `pytest tests/test_acceptance.py -q` | Done |
| Evaluation | Chạy A/B Dense-only và Dense+BM25+RRF; sửa metric để một document có nhiều chunk chỉ tính một hit. | `src/evaluation.py`, `src/run_evaluation_real.py`, `group_project/evaluation/results.json` | Done |
| Báo cáo evaluation | Viết bảng A/B, phân tích worst performers, fallback và khuyến nghị. | `group_project/evaluation/RESULT.md` | Done |
| Integration Phase 3 | Hoàn thiện citation context, xử lý Gemini response, extractive fallback khi provider lỗi và ngưỡng out-of-domain. | `src/task10_generation.py`, `src/task9_retrieval_pipeline.py`, `app.py` | Done |
| Final review | Chạy contract, acceptance và toàn bộ test suite. | `pytest -q`: 49 passed | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Đánh giá retrieval ở cấp document source thay vì chunk ID.
   **Lý do/evidence:** Một nguồn có nhiều chunk; cách đếm cũ khiến Recall@5 vượt 1. Sau khử trùng lặp theo source, metric nằm trong khoảng hợp lệ.
   **Trade-off:** Không phản ánh độ bao phủ giữa các đoạn khác nhau trong cùng tài liệu.

2. **Quyết định:** Dùng dense threshold `0.55` và chỉ chấp nhận keyword fallback từ `0.60`.
   **Lý do/evidence:** Query in-domain về phí quản lý đạt score `0.6849`; query ngoài domain về phở đạt `0.5143`.
   **Trade-off:** Một câu hỏi hợp lệ nhưng diễn đạt lạ có thể bị safe refusal; cần tune trên validation set lớn hơn.

## Kiểm thử và kết quả

- `pytest tests/test_contracts.py -q`: 15 passed.
- `pytest tests/test_acceptance.py -q`: 5 passed.
- `pytest -q`: 49 passed.
- A/B: Dense `P@5=0.1684`, `R@5=0.8158`, `MRR=0.6798`; Hybrid `P@5=0.1579`, `R@5=0.7632`, `MRR=0.6842`.
- Demo in-domain: “Phí quản lý chung cư được tính như thế nào?” trả nguồn `article_01.md`.
- Demo out-of-domain: “Công thức nấu phở bò Hà Nội ngon?” không có nguồn phù hợp và nhận safe refusal.
- Lỗi phát hiện: Gemini endpoint trả HTTP 503 khi tải cao; hệ thống dùng extractive fallback có citation, không bịa thông tin.

## Điều còn hạn chế

- Faithfulness và answer relevance hiện là metric proxy lexical, chưa thay thế đánh giá bằng LLM/human.
- Nếu có thêm thời gian, tôi sẽ gán nhãn relevance cho toàn bộ golden set, tune threshold theo validation split và chạy LLM-as-judge khi provider ổn định.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-25
- Tên thành viên: Nguyễn Minh Thắng
