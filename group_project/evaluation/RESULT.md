# RAG Evaluation Results

## Run information

- Date: 2026-09-25
- Corpus: 9 documents, 74 indexed chunks; golden set: 19 questions (16 in-domain, 3 out-of-domain).
- Embedding: Gemini `gemini-embedding-2-preview` with FAISS; dense/BM25 candidates: 10; final `top_k`: 5.
- Generation evaluation used a grounded extractive fallback because the Gemini endpoint returned HTTP 503 during the interactive check.
- Fallback calibration: an in-domain management-fee query scored 0.6849, while an unrelated pho query scored 0.5143; dense threshold is 0.55 and keyword fallback minimum is 0.60.

## Overall scores

| Metric | Dense only | Hybrid + RRF |
| --- | ---: | ---: |
| Faithfulness | 0.9672 | 0.9680 |
| Answer relevance | 0.5370 | 0.5370 |
| Context recall | 0.8158 | 0.7632 |
| Context precision | 0.1684 | 0.1579 |
| MRR | 0.6798 | 0.6842 |

Retrieval metrics are document-level: duplicate chunks from a source count as one hit.

## A/B comparison

Dense-only has the stronger document recall and precision in this small corpus. Hybrid + RRF improves MRR by 0.0044, so the first relevant source is ranked slightly earlier, but its precision and recall decrease because BM25 introduces generic-token matches. Both configurations use the same dataset, prompt, answer formatter and `top_k`; only retrieval differs.

## Worst performers

| Question | Failure stage | Root cause |
| --- | --- | --- |
| Công thức nấu phở bò Hà Nội ngon? | Retrieval | Generic Vietnamese token overlap; weak fallback is rejected and the application gives a safe refusal. |
| Kinh phí bảo trì 2% được quy định ra sao? | Retrieval | The question needs multiple sources, while RRF may prioritize news chunks over all required legal context. |
| Giá điện sinh hoạt năm 2026 được tính theo bậc nào? | Retrieval | Repeated chunks from one article reduce source diversity in the top five. |

## Recommendations

1. Tune thresholds on a held-out validation set with more out-of-domain cases.
2. Add source diversification and Vietnamese stop-word handling to BM25.
3. Add Gemini retry/backoff and repeat generation evaluation with LLM-as-judge or human review when the provider is stable.

## Bonus experiments

Dense + BM25 + RRF (`k=60`) improved MRR by 0.65% but reduced the four-metric average from 0.6221 to 0.6065. It remains useful for experimentation, not the default until source diversity is improved.
