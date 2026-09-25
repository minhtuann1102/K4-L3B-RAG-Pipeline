"""
Evaluation framework for RAG pipeline.

Metrics computed:
- Retrieval: Precision@K, Recall@K, MRR (Mean Reciprocal Rank)
- Generation: Faithfulness, Answer Relevance
"""

from typing import Any

from src.contracts import SearchResult, GenerationResult


def _relevant_document_ids(item: dict[str, Any]) -> set[str]:
    """Read golden-context document names while retaining old dataset support."""
    legacy = item.get("relevant_doc_ids")
    if isinstance(legacy, list):
        return set(legacy)
    context = str(item.get("expected_context", ""))
    return {
        part.strip()
        for part in context.split(";")
        if part.strip().endswith(".md")
    }


def _document_id(result: SearchResult) -> str:
    """Map a chunk ID to the source file used by golden cases."""
    source = result.get("metadata", {}).get("source")
    if source:
        return str(source)
    return str(result.get("id", "")).split("::", 1)[0].replace("\\", "/").split("/")[-1]


# =============================================================================
# Retrieval Metrics
# =============================================================================

def precision_at_k(
    retrieved_ids: list[str],
    relevant_ids: set[str],
    k: int = 5,
) -> float:
    """Calculate Precision@K.

    Precision@K = (# of relevant items in top K) / K
    """
    if k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for doc_id in top_k if doc_id in relevant_ids)
    return hits / k


def recall_at_k(
    retrieved_ids: list[str],
    relevant_ids: set[str],
    k: int = 5,
) -> float:
    """Calculate Recall@K.

    Recall@K = (# of relevant items in top K) / (total # of relevant items)
    """
    if not relevant_ids:
        return 1.0 if not retrieved_ids else 0.0
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for doc_id in top_k if doc_id in relevant_ids)
    return hits / len(relevant_ids)


def mean_reciprocal_rank(
    retrieved_ids: list[str],
    relevant_ids: set[str],
) -> float:
    """Calculate MRR (Mean Reciprocal Rank).

    MRR = 1 / (rank of first relevant document)
    Returns 0 if no relevant document found.
    """
    for i, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant_ids:
            return 1.0 / i
    return 0.0


def evaluate_retrieval(
    queries: list[dict[str, Any]],
    results: dict[str, list[SearchResult]],
    k: int = 5,
) -> dict[str, float]:
    """Evaluate retrieval performance on a set of queries.

    Args:
        queries: List of dicts with 'question', 'relevant_doc_ids'
        results: Dict mapping question -> list of SearchResult
        k: K for Precision@K and Recall@K

    Returns:
        Dict with 'precision_at_k', 'recall_at_k', 'mrr'
    """
    precision_scores = []
    recall_scores = []
    mrr_scores = []

    for query_item in queries:
        question = query_item.get("question", "")
        relevant_ids = _relevant_document_ids(query_item)

        retrieved = results.get(question, [])
        # Metrics are document-level: several chunks from one source are one hit.
        retrieved_ids = list(dict.fromkeys(_document_id(r) for r in retrieved))

        precision_scores.append(precision_at_k(retrieved_ids, relevant_ids, k))
        recall_scores.append(recall_at_k(retrieved_ids, relevant_ids, k))
        mrr_scores.append(mean_reciprocal_rank(retrieved_ids, relevant_ids))

    return {
        "precision_at_k": sum(precision_scores) / len(precision_scores) if precision_scores else 0.0,
        "recall_at_k": sum(recall_scores) / len(recall_scores) if recall_scores else 0.0,
        "mrr": sum(mrr_scores) / len(mrr_scores) if mrr_scores else 0.0,
    }


# =============================================================================
# Generation Metrics
# =============================================================================

def faithfulness_score(
    generated_answer: str,
    retrieved_contexts: list[str],
    llm_client: Any = None,
) -> float:
    """Calculate Faithfulness score.

    Measures how much the generated answer is supported by the retrieved context.

    Note: This is a simplified implementation. Production systems should use
    an LLM-based evaluation with the RAGAS framework.

    Returns:
        Score between 0.0 and 1.0
    """
    # Simplified: check if key phrases from context appear in answer
    # Full implementation would use LLM to verify claims
    if not retrieved_contexts or not generated_answer:
        return 0.0

    context_text = " ".join(retrieved_contexts).lower()
    answer_words = generated_answer.lower().split()

    # Count answer words that appear in context
    hits = sum(1 for word in answer_words if word in context_text and len(word) > 3)
    if not answer_words:
        return 0.0

    return min(hits / len([w for w in answer_words if len(w) > 3]), 1.0) if answer_words else 0.0


def answer_relevance_score(
    generated_answer: str,
    original_question: str,
    llm_client: Any = None,
) -> float:
    """Calculate Answer Relevance score.

    Measures how relevant the generated answer is to the original question.

    Note: This is a simplified implementation. Production systems should use
    an LLM-based evaluation with the RAGAS framework.

    Returns:
        Score between 0.0 and 1.0
    """
    # Simplified: check overlap between question and answer keywords
    if not generated_answer or not original_question:
        return 0.0

    question_words = set(w.lower() for w in original_question.split() if len(w) > 2)
    answer_words = set(w.lower() for w in generated_answer.split() if len(w) > 2)

    if not answer_words:
        return 0.0

    overlap = question_words & answer_words
    # Relevance is based on how many question keywords appear in answer
    return len(overlap) / len(question_words) if question_words else 0.0


def evaluate_generation(
    questions: list[dict[str, Any]],
    generations: dict[str, GenerationResult],
    k: int = 5,
    llm_client: Any = None,
) -> dict[str, float]:
    """Evaluate generation performance on a set of questions.

    Args:
        questions: List of dicts with 'question', 'ground_truth_answer'
        generations: Dict mapping question -> GenerationResult
        k: Number of contexts to consider
        llm_client: Optional LLM client for advanced metrics

    Returns:
        Dict with 'faithfulness', 'answer_relevance'
    """
    faithfulness_scores = []
    relevance_scores = []

    for query_item in questions:
        question = query_item.get("question", "")
        ground_truth = query_item.get("expected_answer", query_item.get("ground_truth_answer", ""))

        gen_result = generations.get(question)
        if not gen_result:
            continue

        answer = gen_result.get("answer", "")
        sources = gen_result.get("sources", [])
        contexts = [s.get("content", "") for s in sources[:k]]

        faithfulness_scores.append(faithfulness_score(answer, contexts, llm_client))
        relevance_scores.append(answer_relevance_score(answer, question, llm_client))

    return {
        "faithfulness": sum(faithfulness_scores) / len(faithfulness_scores) if faithfulness_scores else 0.0,
        "answer_relevance": sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0,
    }


# =============================================================================
# Full Pipeline Evaluation
# =============================================================================

def evaluate_pipeline(
    queries: list[dict[str, Any]],
    pipeline_fn: callable,
    k: int = 5,
    llm_client: Any = None,
) -> dict[str, float]:
    """Run full pipeline evaluation.

    Args:
        queries: List of golden questions with ground truth
        pipeline_fn: Function that takes a query string and returns GenerationResult
        k: K for retrieval metrics
        llm_client: Optional LLM client for generation metrics

    Returns:
        Dict with all metrics
    """
    all_results: dict[str, list[SearchResult]] = {}
    all_generations: dict[str, GenerationResult] = {}

    for query_item in queries:
        question = query_item.get("question", "")
        try:
            result = pipeline_fn(question)
            all_generations[question] = result
            all_results[question] = result.get("sources", [])
        except Exception as e:
            print(f"Error processing question: {question[:50]}... - {e}")
            all_generations[question] = {
                "answer": "",
                "sources": [],
                "retrieval_source": "none",
            }
            all_results[question] = []

    retrieval_metrics = evaluate_retrieval(queries, all_results, k)
    generation_metrics = evaluate_generation(queries, all_generations, k, llm_client)

    return {
        **retrieval_metrics,
        **generation_metrics,
    }
