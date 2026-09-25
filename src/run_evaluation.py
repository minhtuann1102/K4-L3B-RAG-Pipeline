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
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation import evaluate_pipeline
from src.task5_semantic_search import semantic_search
from src.task6_lexical_search import lexical_search
from src.task7_reranking import rerank_rrf
from src.task8_pageindex_vectorless import pageindex_search
from src.contracts import SearchResult, GenerationResult

SCORE_THRESHOLD = 0.3


def load_golden_dataset(path: str = "group_project/evaluation/golden_dataset.json") -> list[dict]:
    """Load golden dataset from JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_pipeline(query: str, top_k: int = 5) -> GenerationResult:
    """Baseline: Dense search only."""
    try:
        dense_results = semantic_search(query, top_k=top_k)
        sources = dense_results[:top_k]
        return {
            "answer": f"[BASELINE] Dense search results for: {query}",
            "sources": sources,
            "retrieval_source": "hybrid" if sources else "none",
        }
    except Exception as e:
        print(f"  Warning: Baseline failed for '{query[:50]}...': {e}")
        return {
            "answer": "",
            "sources": [],
            "retrieval_source": "none",
        }


def run_hybrid_pipeline(query: str, top_k: int = 5) -> GenerationResult:
    """Hybrid: Dense + BM25 + RRF + PageIndex fallback."""
    try:
        dense_results = semantic_search(query, top_k=top_k * 2)
        sparse_results = lexical_search(query, top_k=top_k * 2)
        hybrid_results = rerank_rrf([dense_results, sparse_results], top_k=top_k)

        # Check fallback threshold
        best_dense_score = dense_results[0]["score"] if dense_results else 0.0
        if best_dense_score < SCORE_THRESHOLD:
            try:
                fallback = pageindex_search(query, top_k=top_k)
                if fallback:
                    return {
                        "answer": f"[HYBRID+PageIndex] Results for: {query}",
                        "sources": fallback[:top_k],
                        "retrieval_source": "pageindex",
                    }
            except Exception:
                pass

        return {
            "answer": f"[HYBRID] Dense+BM25+RRF results for: {query}",
            "sources": hybrid_results[:top_k],
            "retrieval_source": "hybrid" if hybrid_results else "none",
        }
    except Exception as e:
        print(f"  Warning: Hybrid failed for '{query[:50]}...': {e}")
        return {
            "answer": "",
            "sources": [],
            "retrieval_source": "none",
        }


def run_dense_only_pipeline(query: str, top_k: int = 5) -> GenerationResult:
    """Pure dense only for comparison."""
    try:
        dense_results = semantic_search(query, top_k=top_k)
        return {
            "answer": f"[DENSE ONLY] Results for: {query}",
            "sources": dense_results[:top_k],
            "retrieval_source": "hybrid" if dense_results else "none",
        }
    except Exception as e:
        return {
            "answer": "",
            "sources": [],
            "retrieval_source": "none",
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

    # Run dense-only evaluation (baseline for comparison)
    print("\n" + "-" * 60)
    print("Running DENSE-ONLY evaluation...")
    print("-" * 60)
    try:
        dense_only_metrics = evaluate_pipeline(queries, run_dense_only_pipeline)
        print("\nDense-Only Results:")
        for metric, value in dense_only_metrics.items():
            print(f"  {metric}: {value:.4f}")
    except Exception as e:
        print(f"Dense-only evaluation failed: {e}")
        dense_only_metrics = {}

    # Run hybrid evaluation
    print("\n" + "-" * 60)
    print("Running HYBRID evaluation (Dense + BM25 + RRF + PageIndex)...")
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
    print(f"{'Metric':<20} {'Dense Only':>15} {'Hybrid':>15} {'Diff':>15}")
    print("-" * 60)
    for metric in dense_only_metrics:
        dense_val = dense_only_metrics.get(metric, 0)
        hybrid_val = hybrid_metrics.get(metric, 0)
        diff = hybrid_val - dense_val
        sign = "+" if diff >= 0 else ""
        print(f"{metric:<20} {dense_val:>15.4f} {hybrid_val:>15.4f} {sign}{diff:>14.4f}")

    # Calculate improvements
    improvements = {}
    for metric in dense_only_metrics:
        dense_val = dense_only_metrics.get(metric, 0)
        hybrid_val = hybrid_metrics.get(metric, 0)
        if dense_val > 0:
            pct_change = ((hybrid_val - dense_val) / dense_val) * 100
            improvements[metric] = pct_change

    print("\n" + "=" * 60)
    print("IMPROVEMENT SUMMARY")
    print("=" * 60)
    for metric, pct in improvements.items():
        sign = "+" if pct >= 0 else ""
        print(f"  {metric}: {sign}{pct:.2f}%")

    # Save results for later use
    results = {
        "dense_only": dense_only_metrics,
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
