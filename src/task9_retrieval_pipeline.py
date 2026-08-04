"""
Task 9 - Complete Retrieval Pipeline.

Pipeline:
    semantic_search + lexical_search -> RRF fusion -> optional rerank
    -> fallback to PageIndex/Gemini when dense confidence is too low.
"""

from src.task5_semantic_search import semantic_search
from src.task6_lexical_search import lexical_search
from src.task7_reranking import rerank, rerank_rrf
from src.task8_pageindex_vectorless import pageindex_search

SCORE_THRESHOLD = 0.3
DEFAULT_TOP_K = 5
RERANK_METHOD = "rrf"


def _normalize_result(item: dict, source: str) -> dict:
    metadata = item.get("metadata") or {}
    return {
        "content": item.get("content", ""),
        "score": float(item.get("score", 0.0)),
        "metadata": metadata,
        "source": source,
    }


def _dedupe_by_content(results: list[dict]) -> list[dict]:
    seen = set()
    deduped = []
    for result in results:
        key = result.get("content", "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(result)
    return deduped


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """
    Return top_k retrieval results from hybrid search, with PageIndex fallback.

    The fallback decision uses the original semantic score, not the RRF score.
    """
    if not query or top_k <= 0:
        return []

    dense_results = semantic_search(query, top_k=top_k * 2)
    sparse_results = lexical_search(query, top_k=top_k * 2)

    best_dense_score = dense_results[0]["score"] if dense_results else 0.0
    if best_dense_score < score_threshold:
        try:
            fallback = pageindex_search(query, top_k=top_k)
        except Exception:
            fallback = []
        if fallback:
            return [_normalize_result(item, "pageindex") for item in fallback[:top_k]]

    dense_ranked = [_normalize_result(item, "hybrid") for item in dense_results]
    sparse_ranked = [_normalize_result(item, "hybrid") for item in sparse_results]

    if dense_ranked and sparse_ranked:
        merged = rerank_rrf([dense_ranked, sparse_ranked], top_k=top_k * 2)
    else:
        merged = _dedupe_by_content(dense_ranked + sparse_ranked)[: top_k * 2]

    merged = [_normalize_result(item, "hybrid") for item in merged]

    if use_reranking and merged:
        final_results = rerank(query, merged, top_k=top_k, method=RERANK_METHOD)
        final_results = [_normalize_result(item, "hybrid") for item in final_results]
    else:
        final_results = merged[:top_k]

    return final_results[:top_k]


if __name__ == "__main__":
    test_queries = [
        "What payment methods does Shopee support?",
        "How do I request a return or refund?",
        "What evidence do I need for a refund request?",
        "xyzabc123nonsense",
    ]

    for q in test_queries:
        print(f"\nQuery: {q}")
        print("-" * 60)
        for i, r in enumerate(retrieve(q, top_k=3), 1):
            print(f"  {i}. [{r['score']:.3f}] [{r['source']}] {r['content'][:80]}...")
