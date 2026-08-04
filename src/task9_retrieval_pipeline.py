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
ENABLE_QUERY_EXPANSION = True

QUERY_EXPANSION_TERMS = {
    "thanh toán": ["payment methods", "ShopeePay", "COD", "thẻ tín dụng", "chuyển khoản"],
    "payment": ["phương thức thanh toán", "ShopeePay", "COD", "credit card"],
    "hoàn tiền": ["refund", "return refund policy", "bằng chứng hoàn tiền"],
    "trả hàng": ["return", "returns refund", "đổi trả", "hoàn tiền"],
    "thuế": ["tax", "GTGT", "TNCN", "doanh thu 100 triệu"],
    "hộ kinh doanh": ["đăng ký hộ kinh doanh", "hồ sơ", "UBND quận huyện"],
    "người bán": ["seller", "product listing", "quy định đăng bán"],
    "seller": ["người bán", "listing regulations", "prohibited products"],
    "đơn hàng": ["order tracking", "theo dõi đơn hàng", "vận chuyển"],
    "privacy": ["quyền riêng tư", "dữ liệu cá nhân", "privacy policy"],
}


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


def expand_query(query: str, max_expansions: int = 3) -> list[str]:
    """
    Query Expansion bonus: add bilingual/domain variants for stronger retrieval.

    This is intentionally deterministic so the pipeline can run without spending
    extra LLM calls during tests or demo setup.
    """
    normalized = query.lower()
    expansions = [query]

    for trigger, variants in QUERY_EXPANSION_TERMS.items():
        if trigger in normalized:
            for variant in variants:
                expanded = f"{query} {variant}"
                if expanded not in expansions:
                    expansions.append(expanded)
                if len(expansions) >= max_expansions + 1:
                    return expansions

    return expansions


def generate_hypothetical_document(query: str) -> str:
    """
    HyDE-lite bonus: create a short hypothetical support answer and retrieve with it.

    Real HyDE uses an LLM. This local version keeps the same idea while staying
    deterministic and safe for offline testing.
    """
    return (
        "Tài liệu hỗ trợ khách hàng thương mại điện tử liên quan đến câu hỏi: "
        f"{query}. Nội dung có thể đề cập chính sách thanh toán, đổi trả, hoàn tiền, "
        "quy định người bán, thuế, đăng ký kinh doanh, quyền riêng tư hoặc theo dõi đơn hàng."
    )


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

    search_queries = expand_query(query) if ENABLE_QUERY_EXPANSION else [query]
    hyde_query = generate_hypothetical_document(query)

    dense_pool = []
    sparse_pool = []
    for search_query in [*search_queries, hyde_query]:
        dense_pool.extend(semantic_search(search_query, top_k=top_k * 2))
        sparse_pool.extend(lexical_search(search_query, top_k=top_k * 2))

    dense_results = _dedupe_by_content(dense_pool)[: top_k * 2]
    sparse_results = _dedupe_by_content(sparse_pool)[: top_k * 2]

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
