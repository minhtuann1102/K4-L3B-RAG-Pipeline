# Kế hoạch làm việc nhóm - RAG Pipeline Lab

**Thời gian:** 3 giờ  
**Nhóm:** 3 người  
**Mục tiêu:** Hoàn thành chatbot RAG với hybrid retrieval, citation, UI và evaluation

---

## Phase 0: Setup môi trường (15 phút) - CẢ NHÓM

Mỗi người tự làm trên máy mình:

```bash
# 1. Clone và vào thư mục
cd K4-L3B-RAG-Pipeline-NguyenMinhTuan-2A202602420

# 2. Tạo virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Cài đặt dependencies
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
python -m playwright install chromium

# 4. Config API keys
copy .env.example .env
# Mở .env và điền API keys (OpenAI hoặc model khác)
```

**Checkpoint:** Mọi người chạy `python --version` và `pip list` để confirm setup thành công.

---

## Phase 1: Parallel Work (60 phút)

### 👤 NGƯỜI 1: Data Collection Lead

**Nhiệm vụ:** Thu thập và chuẩn hóa dữ liệu

#### Bước 1.1: Chọn chủ đề (5 phút)
- Thống nhất với nhóm về domain (ví dụ: luật lao động, chính sách giáo dục, quy định giao thông, etc.)
- Xem gợi ý tại `docs/SUGGESTED_TOPICS.md`

#### Bước 1.2: Thu thập legal docs (15 phút)
```bash
python -m src.task1_collect_legal_docs
```
- Tối thiểu 3 tài liệu chính sách/pháp luật
- Lưu vào thư mục `data/legal/` (PDF hoặc format gốc)
- Nguồn gợi ý: vanban.chinhphu.vn, thuvienphapluat.vn, website bộ ngành

#### Bước 1.3: Crawl news/articles (15 phút)
```bash
python -m src.task2_crawl_news
```
- Tối thiểu 5 bài viết liên quan chủ đề
- Lưu vào `data/news/`
- Nguồn: báo điện tử, blog chuyên ngành

#### Bước 1.4: Convert sang Markdown (15 phút)
```bash
python -m src.task3_convert_markdown
```
- Chuyển tất cả docs sang `.md` format
- Làm sạch: xóa header/footer thừa, format lại table
- Output: `data/processed/*.md`

#### Bước 1.5: Commit và push (10 phút)
```bash
git add data/
git commit -m "Add legal docs and news articles"
git push origin main
```
- Thông báo nhóm để pull về

**Deliverable:** ≥3 legal docs + ≥5 news articles ở dạng Markdown sạch

---

### 👤 NGƯỜI 2: Pipeline & Search Lead

**Nhiệm vụ:** Xây dựng chunking, indexing và retrieval

#### Bước 2.1: Đọc contracts (10 phút)
- Đọc `docs/MODULE_CONTRACTS.md`
- Hiểu rõ schema `SearchResult` và interfaces cần implement

#### Bước 2.2: Implement chunking (15 phút)
Trong `src/task4_chunking_indexing.py`:
- Function `chunk_documents()`: split text thành chunks (~500 tokens, overlap 50)
- Input: list of markdown files
- Output: list of `Chunk` objects với metadata (source, page, etc.)

#### Bước 2.3: Setup ChromaDB và dense search (20 phút)
- Initialize ChromaDB collection
- Chọn embedding model (ví dụ: `sentence-transformers/all-MiniLM-L6-v2`)
- Function `dense_search(query, top_k)` → trả về `List[SearchResult]`
- Mỗi result phải có: `doc_id`, `chunk_text`, `score`, `metadata`

#### Bước 2.4: Implement BM25 search (15 phút)
- Install `rank-bm25` nếu cần: `pip install rank-bm25`
- Function `bm25_search(query, top_k)` → trả về `List[SearchResult]`
- **Quan trọng:** Cùng schema với dense search

#### Bước 2.5: Test và commit
```bash
pytest tests/test_contracts.py -k search -v
git add src/
git commit -m "Implement chunking and hybrid search"
git push
```

**Deliverable:** Module search hoạt động, pass contract tests

---

### 👤 NGƯỜI 3: Evaluation & Integration Prep

**Nhiệm vụ:** Chuẩn bị đánh giá và môi trường tích hợp

#### Bước 3.1: Nghiên cứu metrics (10 phút)
Đọc về 4 metrics cần đánh giá:
- **Retrieval metrics:** Precision@K, Recall@K, MRR
- **Generation metrics:** Faithfulness, Answer Relevance
- Ghi chú cách tính từng metric

#### Bước 3.2: Tạo golden dataset (30 phút)
Tạo file `group_project/evaluation/golden_dataset.json`:
```json
[
  {
    "question": "Câu hỏi 1 trong domain",
    "ground_truth_answer": "Câu trả lời đúng",
    "relevant_doc_ids": ["doc1.md", "doc2.md"]
  },
  ...
]
```
- Tối thiểu 15 câu hỏi
- Mix: 10-12 in-domain, 3-5 out-of-domain (để test fallback)
- Chú ý: câu hỏi phải liên quan dữ liệu thực tế nhóm thu thập

#### Bước 3.3: Setup evaluation framework (20 phút)
Tạo `src/evaluation.py`:
```python
def evaluate_retrieval(queries, results, ground_truth):
    # Tính precision, recall, MRR
    pass

def evaluate_generation(questions, generated_answers, ground_truth):
    # Tính faithfulness, relevance
    pass
```

**Deliverable:** Golden dataset 15+ câu, skeleton code cho evaluation

---

## SYNC POINT 1 (sau 1h15): Check-in toàn nhóm (5 phút)

- Người 1: Data đã push chưa? → Người 2, 3 pull về
- Người 2: Search functions chạy được chưa?
- Người 3: Golden dataset có bao nhiêu câu rồi?
- Ai bị block? Cần support gì?

---

## Phase 2: Integration (50 phút)

### 👤 NGƯỜI 1: Generation & UI

#### Bước 1.6: Implement RRF fusion (15 phút)
Trong `src/retrieval.py`:
```python
def reciprocal_rank_fusion(dense_results, bm25_results, k=60):
    # Gộp rankings theo công thức RRF
    # Return: List[SearchResult] đã rerank
    pass
```

#### Bước 1.7: Implement fallback logic (10 phút)
```python
def fallback_filter(fused_results, threshold=0.5):
    # Nếu top result score < threshold → trả về "Không tìm thấy"
    # Else: return filtered results
    pass
```

#### Bước 1.8: Generation với citation (15 phút)
```python
def generate_answer(query, retrieved_chunks):
    # Call LLM API với prompt:
    # "Dựa trên context sau, trả lời câu hỏi và trích dẫn nguồn..."
    # Return: answer với [1], [2] citations
    pass
```

#### Bước 1.9: Streamlit UI (10 phút)
Trong `app.py`:
```python
import streamlit as st

st.title("RAG Chatbot")
query = st.text_input("Câu hỏi của bạn:")
if st.button("Gửi"):
    # Pipeline: search → RRF → fallback → generate
    answer, sources = pipeline(query)
    st.write(answer)
    st.write("**Nguồn:**")
    for src in sources:
        st.write(f"- {src}")
```

Test:
```bash
streamlit run app.py
```

---

### 👤 NGƯỜI 2: Testing & Quality Assurance

#### Bước 2.6: Viết unit tests (20 phút)
Trong `tests/`:
- Test chunking: chunk size, overlap đúng spec
- Test search: return đúng schema
- Test RRF: ranking logic đúng
- Test fallback: threshold hoạt động

#### Bước 2.7: Chạy toàn bộ tests (10 phút)
```bash
pytest tests/test_contracts.py -v
pytest tests/test_acceptance.py -v
pytest -v
```
- Fix tất cả failures
- Đảm bảo coverage ≥80%

#### Bước 2.8: Code review và refactor (20 phút)
- Check code style: consistent naming, comments
- Refactor: extract magic numbers thành constants
- Verify: threshold được tune trên data thật
- Update docstrings

---

### 👤 NGƯỜI 3: Evaluation Execution

#### Bước 3.4: Chạy evaluation trên golden set (20 phút)
```python
# Trong src/run_evaluation.py
results_baseline = evaluate_pipeline(
    queries=golden_questions,
    use_hybrid=False  # Chỉ dense
)

results_hybrid = evaluate_pipeline(
    queries=golden_questions,
    use_hybrid=True   # Dense + BM25 + RRF
)
```

#### Bước 3.5: Tính metrics và so sánh A/B (15 phút)
| Metric            | Baseline (Dense only) | Hybrid (Dense+BM25+RRF) |
|-------------------|-----------------------|-------------------------|
| Precision@5       |                       |                         |
| Recall@5          |                       |                         |
| MRR               |                       |                         |
| Answer Relevance  |                       |                         |

#### Bước 3.6: Viết RESULT.md (15 phút)
Trong `group_project/evaluation/RESULT.md`:
```markdown
# Evaluation Results

## Dataset
- 15 câu hỏi (12 in-domain, 3 out-of-domain)

## Metrics
...

## Findings
- Hybrid search cải thiện X% so với baseline
- Fallback hoạt động tốt với threshold = Y
...
```

---

## SYNC POINT 2 (sau 2h): Integration check (5 phút)

- Demo chatbot có chạy không?
- Tests có pass không?
- Evaluation có kết quả chưa?

---

## Phase 3: Finalization (30 phút)

### 👤 CẢ NHÓM

#### Task chung 1: Demo và test end-to-end (10 phút)
- Mỗi người test chatbot với 3-5 câu hỏi
- Verify: citations hiển thị đúng, fallback hoạt động
- Screenshot kết quả tốt nhất

#### Task chung 2: Viết báo cáo cá nhân (15 phút)
Mỗi người điền `group_project/individual/INDIVIDUAL_REPORT.md`:
```markdown
# Báo cáo cá nhân - [Tên]

## Công việc đã làm
- Task 1: ...
- Task 2: ...

## Khó khăn và cách giải quyết
...

## Đóng góp vào nhóm
...

## Bài học
...
```

#### Task chung 3: Final review và push (5 phút)
```bash
git status
git add .
git commit -m "Complete RAG pipeline lab"
git push origin main
```

**Checklist cuối cùng:**
- [ ] ≥3 legal docs + ≥5 news articles
- [ ] ChromaDB index hoạt động
- [ ] Dense + BM25 + RRF + fallback
- [ ] Streamlit chatbot chạy được
- [ ] 15+ golden questions
- [ ] 4 metrics evaluated
- [ ] RESULT.md hoàn chỉnh
- [ ] 3 individual reports
- [ ] Repository pushed

---

## Communication Protocol

**Tools:**
- Git để sync code (push/pull thường xuyên)
- Group chat để update tiến độ
- Họp ngắn 15h00 và 16h00

**Khi bị block:**
1. Thử Google/debug 5 phút
2. Hỏi nhóm ngay, đừng chờ lâu
3. Pivot sang task khác nếu blocked >10 phút

**Conflict resolution:**
- Merge conflict: người sau merge chịu trách nhiệm resolve
- Design disagreement: vote nhanh, đa số thắng

---

## Notes quan trọng

1. **Không hardcode threshold:** Tune trên data thật, ghi lại lý do chọn giá trị đó
2. **SearchResult schema phải nhất quán:** Dense và BM25 cùng format
3. **RRF chỉ chạy 1 lần:** Không rerank nhiều lần
4. **Fallback dùng cosine score gốc:** Không phải RRF score
5. **Citation format:** [1], [2], ... và list nguồn ở cuối

---

**Bắt đầu:** 10:15  
**Kết thúc dự kiến:** 13:15  
**Good luck! 🚀**
