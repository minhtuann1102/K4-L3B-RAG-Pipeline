"""
Run evaluation với mock data khi không index được (SSL issues).
Script này tạo mock results để test evaluation framework.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation import (
    precision_at_k,
    recall_at_k,
    mean_reciprocal_rank,
    evaluate_retrieval,
)


# Mock search results để simulate
MOCK_RESULTS = {
    "Phí quản lý chung cư được tính như thế nào?": [
        {"id": "article_01.md::chunk-0", "score": 0.85, "retrieval_method": "dense"},
        {"id": "article_01.md::chunk-1", "score": 0.72, "retrieval_method": "dense"},
        {"id": "article_01.md::chunk-2", "score": 0.65, "retrieval_method": "bm25"},
        {"id": "article_02.md::chunk-0", "score": 0.58, "retrieval_method": "bm25"},
        {"id": "article_03.md::chunk-0", "score": 0.45, "retrieval_method": "dense"},
    ],
    "Kinh phí bảo trì 2% được quy định ra sao trong Luật Nhà ở?": [
        {"id": "article_01.md::chunk-5", "score": 0.88, "retrieval_method": "dense"},
        {"id": "02_luat_nha_o_2023_quy_dinh_quan_ly_chung_cu.md::chunk-3", "score": 0.75, "retrieval_method": "dense"},
        {"id": "03_nghi_dinh_95_2024_nd_cp_quan_ly_su_dung_chung_cu.md::chunk-2", "score": 0.68, "retrieval_method": "bm25"},
    ],
    "Hội nghị nhà chung cư lần đầu được tổ chức khi nào?": [
        {"id": "01_thong_tu_02_2016_tt_bxd_quy_che_nha_chung_cu.md::chunk-2", "score": 0.82, "retrieval_method": "dense"},
        {"id": "01_thong_tu_02_2016_tt_bxd_quy_che_nha_chung_cu.md::chunk-3", "score": 0.71, "retrieval_method": "dense"},
        {"id": "04_mau_noi_quy_quan_ly_su_dung_nha_chung_cu_chuan.md::chunk-1", "score": 0.63, "retrieval_method": "bm25"},
    ],
    # Out-of-domain queries - low scores
    "Cách làm bài phỏng vấn xin việc hiệu quả?": [
        {"id": "random_1", "score": 0.25, "retrieval_method": "dense"},
        {"id": "random_2", "score": 0.22, "retrieval_method": "bm25"},
    ],
    "Công thức nấu phở bò Hà Nội ngon?": [
        {"id": "random_3", "score": 0.18, "retrieval_method": "dense"},
    ],
    "AI (Trí tuệ nhân tạo) là gì và hoạt động như thế nào?": [
        {"id": "random_4", "score": 0.15, "retrieval_method": "dense"},
    ],
}


def run_mock_evaluation():
    """Chạy evaluation với mock data."""
    print("=" * 60)
    print("Mock Evaluation (SSL workaround)")
    print("=" * 60)

    # Load golden dataset
    dataset_path = "group_project/evaluation/golden_dataset.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        queries = json.load(f)

    print(f"\nLoaded {len(queries)} questions")

    # Simulate dense-only results
    print("\n" + "-" * 60)
    print("Simulating DENSE-ONLY results...")
    print("-" * 60)

    dense_results = {}
    for query in queries:
        question = query["question"]
        if question in MOCK_RESULTS:
            # Lọc chỉ lấy dense results
            dense_only = [r for r in MOCK_RESULTS[question] if r["retrieval_method"] == "dense"]
            dense_results[question] = dense_only
        else:
            dense_results[question] = []

    dense_metrics = evaluate_retrieval(queries, dense_results, k=5)
    print("\nDense-Only Metrics:")
    for metric, value in dense_metrics.items():
        print(f"  {metric}: {value:.4f}")

    # Simulate hybrid results (bao gồm cả dense và bm25)
    print("\n" + "-" * 60)
    print("Simulating HYBRID results (Dense + BM25 + RRF)...")
    print("-" * 60)

    hybrid_results = {}
    for query in queries:
        question = query["question"]
        if question in MOCK_RESULTS:
            hybrid_results[question] = MOCK_RESULTS[question][:5]
        else:
            hybrid_results[question] = []

    hybrid_metrics = evaluate_retrieval(queries, hybrid_results, k=5)
    print("\nHybrid Metrics:")
    for metric, value in hybrid_metrics.items():
        print(f"  {metric}: {value:.4f}")

    # Comparison
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)
    print(f"{'Metric':<20} {'Dense Only':>12} {'Hybrid':>12} {'Diff':>12}")
    print("-" * 60)

    improvements = {}
    for metric in dense_metrics:
        d_val = dense_metrics.get(metric, 0)
        h_val = hybrid_metrics.get(metric, 0)
        diff = h_val - d_val
        improvements[metric] = diff
        sign = "+" if diff >= 0 else ""
        print(f"{metric:<20} {d_val:>12.4f} {h_val:>12.4f} {sign}{diff:>11.4f}")

    # Save results
    results = {
        "mode": "mock",
        "dense_only": dense_metrics,
        "hybrid": hybrid_metrics,
        "improvements": improvements,
        "note": "Kết quả này là mock data do không thể index do lỗi SSL. "
                "Cần chạy indexing thực sự để có kết quả đúng."
    }

    with open("group_project/evaluation/results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nResults saved to group_project/evaluation/results.json")
    print("\n" + "=" * 60)
    print("NOTE: Đây là mock results. Để có kết quả thực:")
    print("1. Fix SSL certificate trên máy")
    print("2. Chạy: python -m src.force_index")
    print("3. Chạy: python -m src.run_evaluation")
    print("=" * 60)

    return results


if __name__ == "__main__":
    run_mock_evaluation()
