"""
Script to run evaluation on the RAG pipeline.

Usage:
    python -m src.run_evaluation

This will:
1. Load the golden dataset
2. Run both baseline (dense only) and hybrid (dense + BM25 + RRF) pipelines
3. Compare and report metrics
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation import evaluate_pipeline


def load_golden_dataset(path: str = "group_project/evaluation/golden_dataset.json") -> list[dict]:
    """Load golden dataset from JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_pipeline(query: str):
    """Baseline: Dense search only (placeholder)."""
    # TODO: Replace with actual dense search call when task5 is implemented
    return {
        "answer": f"[BASELINE] Answer for: {query}",
        "sources": [],
        "retrieval_source": "none",
    }


def run_hybrid_pipeline(query: str):
    """Hybrid: Dense + BM25 + RRF (placeholder)."""
    # TODO: Replace with actual hybrid pipeline when tasks are implemented
    return {
        "answer": f"[HYBRID] Answer for: {query}",
        "sources": [],
        "retrieval_source": "hybrid",
    }


def main():
    print("=" * 60)
    print("RAG Pipeline Evaluation")
    print("=" * 60)

    # Load golden dataset
    dataset_path = "group_project/evaluation/golden_dataset.json"
    try:
        queries = load_golden_dataset(dataset_path)
        print(f"\nLoaded {len(queries)} questions from {dataset_path}")
    except FileNotFoundError:
        print(f"ERROR: Golden dataset not found at {dataset_path}")
        print("Please create the dataset first.")
        return

    # Count in-domain vs out-of-domain
    in_domain = [q for q in queries if q.get("relevant_doc_ids")]
    out_domain = [q for q in queries if not q.get("relevant_doc_ids")]
    print(f"  - In-domain questions: {len(in_domain)}")
    print(f"  - Out-of-domain questions: {len(out_domain)}")

    # Run baseline evaluation
    print("\n" + "-" * 60)
    print("Running BASELINE evaluation (Dense only)...")
    print("-" * 60)
    try:
        baseline_metrics = evaluate_pipeline(queries, run_baseline_pipeline)
        print("\nBaseline Results:")
        for metric, value in baseline_metrics.items():
            print(f"  {metric}: {value:.4f}")
    except Exception as e:
        print(f"Baseline evaluation failed: {e}")
        baseline_metrics = {}

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
        print(f"Hybrid evaluation failed: {e}")
        hybrid_metrics = {}

    # Comparison table
    print("\n" + "=" * 60)
    print("COMPARISON TABLE")
    print("=" * 60)
    print(f"{'Metric':<20} {'Baseline':>15} {'Hybrid':>15} {'Diff':>15}")
    print("-" * 60)
    for metric in baseline_metrics:
        baseline_val = baseline_metrics.get(metric, 0)
        hybrid_val = hybrid_metrics.get(metric, 0)
        diff = hybrid_val - baseline_val
        sign = "+" if diff >= 0 else ""
        print(f"{metric:<20} {baseline_val:>15.4f} {hybrid_val:>15.4f} {sign}{diff:>14.4f}")

    print("\n" + "=" * 60)
    print("Evaluation complete!")
    print("=" * 60)
    print("\nNOTE: These are placeholder results. Update the pipeline functions")
    print("      (run_baseline_pipeline, run_hybrid_pipeline) with actual implementations.")


if __name__ == "__main__":
    main()
