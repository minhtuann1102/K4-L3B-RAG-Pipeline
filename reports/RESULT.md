# RAG evaluation results

## Run information

| Field | Value |
| --- | --- |
| Evaluation date | 2026-09-25 |
| Framework and version | Custom Python evaluator in `src/evaluation.py`; Python project test suite |
| Evaluator model | Deterministic lexical-overlap proxy for faithfulness and relevance |
| Generator model | Gemini `gemini-3.8-flash`; extractive cited fallback used for this A/B run when the endpoint was unavailable |
| Embedding model | Gemini `gemini-embedding-2-preview` with FAISS |
| Corpus version/commit | Repository commit `0d1a323`; 9 documents, 74 indexed chunks |
| Golden dataset size | 19 questions: 16 in-domain, 3 out-of-domain |
| `top_k` | 5 final results; 10 dense/BM25 candidates |
| Fallback threshold and calibration | Dense `0.55`, keyword fallback `0.60`; in-domain fee query `0.6849`, unrelated pho query `0.5143` |

## Configurations

- **Config A — dense-only:** Gemini embeddings → FAISS dense retrieval → cited extractive answer from top 5 chunks.
- **Config B — hybrid + RRF:** Gemini embeddings → FAISS dense + BM25 → RRF (`k=60`) → cited extractive answer from top 5 chunks.

Hai config dùng cùng golden dataset, answer formatter, metric implementation và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric | Config A | Config B | Delta B−A |
| --- | ---: | ---: | ---: |
| Faithfulness | 0.9672 | 0.9680 | +0.0008 |
| Answer relevance | 0.5370 | 0.5370 | +0.0000 |
| Context recall | 0.8158 | 0.7632 | -0.0526 |
| Context precision | 0.1684 | 0.1579 | -0.0105 |
| **Average** | **0.6221** | **0.6065** | **-0.0156** |

MRR (bổ sung): Dense `0.6798`, Hybrid `0.6842` (delta `+0.0044`). Recall/precision được tính ở cấp document, nên nhiều chunks cùng một nguồn chỉ được tính một hit.

## A/B comparison

- Cấu hình tốt hơn: Dense-only xét theo average, context recall và context precision; Hybrid tốt hơn nhẹ ở MRR và faithfulness.
- Evidence: Hybrid giảm Recall@5 6.45% và Precision@5 6.25%, nhưng nâng MRR 0.65%, nghĩa là có xu hướng đưa nguồn liên quan đầu tiên lên cao hơn nhưng thêm nguồn không thuộc golden context vào top 5.
- Trade-off về latency/cost: Hybrid chạy thêm BM25 cục bộ và RRF nên chi phí API embedding không đổi trong lượt query, nhưng CPU/độ trễ retrieval cao hơn dense-only một chút.

## Worst performers

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| --: | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| 1 | Công thức nấu phở bò Hà Nội ngon? | Hybrid | 0.0000 | 0.0000 | 1.0000 | 0.0000 | retrieval | Token tiếng Việt phổ biến tạo keyword overlap; threshold đã chặn nguồn yếu và trả safe refusal. |
| 2 | Kinh phí bảo trì 2% được quy định ra sao trong Luật Nhà ở? | Hybrid | 0.9680 | 0.5370 | 0.5000 | 0.2000 | retrieval | Câu hỏi cần hai nguồn; RRF ưu tiên một số chunks news cùng chủ đề thay vì đủ legal context. |
| 3 | Giá điện sinh hoạt năm 2026 được tính theo bậc nào? | Hybrid | 0.9680 | 0.5370 | 1.0000 | 0.2000 | data/retrieval | Nguồn `article_01.md` có nhiều chunks, làm top 5 kém đa dạng ở cấp document. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| ---: | --- | --- | --- | --- |
| 1 | Tune dense threshold trên validation split và bổ sung OOD examples. | Điểm 0.6849 in-domain và 0.5143 OOD mới là hai điểm calibration. | Giảm citation sai cho câu ngoài domain. | Đo OOD refusal precision/recall trên tập OOD mở rộng. |
| 2 | Diversify results theo source và thêm BM25 stop-word handling. | Top 5 lặp chunks của `article_01.md`, precision thấp. | Tăng document precision và context coverage. | So sánh P@5/R@5 document-level trước và sau. |
| 3 | Retry Gemini với exponential backoff, sau đó dùng LLM-as-judge/human review. | Endpoint Gemini trả HTTP 503 ở interactive check; metric hiện là proxy lexical. | Đánh giá generation đáng tin cậy hơn. | Lưu availability, latency và judge scores cho cùng golden set. |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| --- | --- | ---: | ---: | --- |
| Dense + BM25 + RRF (`k=60`) | Dense-only | MRR `+0.0044`; average `-0.0156` | BM25/RRF thêm CPU nhỏ, không thêm embedding API call | Giữ hybrid như lựa chọn demo, nhưng cần source diversity và tuning trước khi chọn làm default. |
