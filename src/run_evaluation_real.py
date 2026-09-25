"""
Run evaluation thực sự với Gemini + FAISS.
Chạy: python -m src.run_evaluation_real
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.task5_gemini import semantic_search
from src.task6_gemini import lexical_search
from src.task7_reranking import rerank_rrf
from src.task10_generation import _generate_from_chunks
from src.evaluation import evaluate_pipeline

DENSE_CACHE: dict[str, list[dict]] = {}


def cached_dense_search(query: str) -> list[dict]:
    """Avoid embedding each golden question twice in the A/B run."""
    if query not in DENSE_CACHE:
        DENSE_CACHE[query] = semantic_search(query, top_k=10)
    return DENSE_CACHE[query]


def load_golden_dataset(path: str = "group_project/evaluation/golden_dataset.json") -> list[dict]:
    """Load golden dataset."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_pipeline(query: str, top_k: int = 5) -> dict:
    """Baseline: Dense search only."""
    try:
        dense_results = cached_dense_search(query)
        result = _generate_from_chunks(query, dense_results[:top_k], top_k=top_k, use_llm=False)
        return result
    except Exception as e:
        print(f"  Warning: Baseline failed: {e}")
        return {"answer": "", "sources": [], "retrieval_source": "none"}


def run_hybrid_pipeline(query: str, top_k: int = 5) -> dict:
    """Hybrid: Dense + BM25 + RRF."""
    try:
        dense_results = cached_dense_search(query)
        sparse_results = lexical_search(query, top_k=top_k * 2)
        hybrid_results = rerank_rrf([dense_results, sparse_results], top_k=top_k)
        result = _generate_from_chunks(query, hybrid_results[:top_k], top_k=top_k, use_llm=False)
        return result
    except Exception as e:
        print(f"  Warning: Hybrid failed: {e}")
        return {"answer": "", "sources": [], "retrieval_source": "none"}


def main():
    print("=" * 60)
    print("RAG Pipeline Evaluation - Real Run")
    print("=" * 60)

    # Load golden dataset
    dataset_path = "group_project/evaluation/golden_dataset.json"
    try:
        queries = load_golden_dataset(dataset_path)
        print(f"\nLoaded {len(queries)} questions")
    except FileNotFoundError:
        print(f"ERROR: Golden dataset not found at {dataset_path}")
        return

    # Count in-domain vs out-of-domain
    in_domain = [q for q in queries if ".md" in q.get("expected_context", "")]
    out_domain = [q for q in queries if ".md" not in q.get("expected_context", "")]
    print(f"  - In-domain: {len(in_domain)}")
    print(f"  - Out-of-domain: {len(out_domain)}")

    # Run dense-only evaluation
    print("\n" + "-" * 60)
    print("Running DENSE-ONLY evaluation...")
    print("-" * 60)
    try:
        dense_metrics = evaluate_pipeline(queries, run_baseline_pipeline)
        print("\nDense-Only Results:")
        for metric, value in dense_metrics.items():
            print(f"  {metric}: {value:.4f}")
    except Exception as e:
        print(f"Dense-only failed: {e}")
        dense_metrics = {}

    # Run hybrid evaluation
    print("\n" + "-" * 60)
    print("Running HYBRID evaluation (Dense + BM25 + RRF)...")
    print("-" * 60)
    try:
        hybrid_metrics = evaluate_pipeline(queries, run_hybrid_pipeline)
        print("\nHybrid Results:")
        for metric, value in hybrid_metrics.items():
            print(f"  {metric}: {value:.4f}")
    except Exception as e:
        print(f"Hybrid failed: {e}")
        hybrid_metrics = {}

    # Comparison table
    print("\n" + "=" * 60)
    print("COMPARISON TABLE")
    print("=" * 60)
    print(f"{'Metric':<20} {'Dense Only':>15} {'Hybrid':>15} {'Diff':>15}")
    print("-" * 60)
    for metric in dense_metrics:
        d_val = dense_metrics.get(metric, 0)
        h_val = hybrid_metrics.get(metric, 0)
        diff = h_val - d_val
        sign = "+" if diff >= 0 else ""
        print(f"{metric:<20} {d_val:>15.4f} {h_val:>15.4f} {sign}{diff:>14.4f}")

    # Calculate improvements
    improvements = {}
    for metric in dense_metrics:
        d_val = dense_metrics.get(metric, 0)
        h_val = hybrid_metrics.get(metric, 0)
        if d_val > 0:
            pct_change = ((h_val - d_val) / d_val) * 100
            improvements[metric] = pct_change

    print("\n" + "=" * 60)
    print("IMPROVEMENT SUMMARY")
    print("=" * 60)
    for metric, pct in improvements.items():
        sign = "+" if pct >= 0 else ""
        print(f"  {metric}: {sign}{pct:.2f}%")

    # Save results
    results = {
        "dense_only": dense_metrics,
        "hybrid": hybrid_metrics,
        "improvements": improvements,
    }

    results_path = "group_project/evaluation/results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {results_path}")

    print("\n" + "=" * 60)
    print("Evaluation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
