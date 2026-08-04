"""
Task 7 — Reranking Module.

Triển khai cả 3 phương pháp:
    - RRF (Reciprocal Rank Fusion): tự implement, không cần API key — dùng mặc định
      trong pipeline (Task 9, RERANK_METHOD="rrf").
    - MMR (Maximal Marginal Relevance): tự implement, dùng embedding có sẵn của
      candidates (hoặc tự embed qua pipeline Task 4/5 nếu candidate chưa có).
    - Cross-encoder: repo này không có JINA_API_KEY, chỉ có GEMINI_API_KEY đã cấu hình
      trong .env, nên dùng Gemini làm "LLM-as-cross-encoder" — chấm điểm liên quan
      0.0-1.0 cho từng candidate thay vì gọi Jina Reranker API.

Lưu ý quan trọng về RRF (sẽ dùng lại ở Task 9): điểm RRF fused CHỈ phụ thuộc thứ hạng,
không phải độ tương đồng thật. Top-1 sau khi fuse luôn xấp xỉ 1/(k+1) ≈ 0.0164 (k=60),
bất kể nội dung đó có thật sự liên quan đến câu hỏi hay không. Đừng dùng điểm RRF để
quyết định fallback ở Task 9 — xem ghi chú ở đó.
"""

import json
import math
import os
import re

import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_Key") or os.getenv("GEMINI_KEY", "")
GEMINI_MODEL = "gemini-flash-latest"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def _call_gemini(prompt: str, temperature: float = 0.0) -> str:
    """Gọi Gemini REST API, trả về text của response đầu tiên."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY chưa được cấu hình trong .env")

    response = requests.post(
        GEMINI_URL,
        params={"key": GEMINI_API_KEY},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature},
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def rerank_cross_encoder(
    query: str, candidates: list[dict], top_k: int = 5
) -> list[dict]:
    """
    Rerank candidates dùng Gemini làm LLM-as-cross-encoder (thay Jina/Qwen vì
    repo chỉ cấu hình GEMINI_API_KEY).

    Args:
        query: Câu truy vấn
        candidates: List of {'content': str, 'score': float, 'metadata': dict}
        top_k: Số lượng kết quả sau rerank

    Returns:
        List of top_k candidates, re-scored (0.0-1.0) và sorted by score descending.
    """
    if not candidates:
        return []

    listing = "\n".join(f"{i}: {c['content'][:500]}" for i, c in enumerate(candidates))
    prompt = (
        "Bạn là một mô hình cross-encoder rerank cho hệ thống RAG.\n"
        f'Câu truy vấn: "{query}"\n\n'
        f"Danh sách đoạn văn (đánh số từ 0):\n{listing}\n\n"
        "Chấm điểm mức độ liên quan của MỖI đoạn văn với câu truy vấn theo thang 0.0 (không "
        "liên quan) đến 1.0 (rất liên quan).\n"
        "Trả lời DUY NHẤT bằng JSON array các số thực, đúng thứ tự index, không kèm giải "
        'thích. Ví dụ: [0.92, 0.15, 0.6]'
    )

    try:
        raw = _call_gemini(prompt)
        match = re.search(r"\[[\d.,\s]+\]", raw)
        scores = json.loads(match.group(0)) if match else json.loads(raw)
        if len(scores) != len(candidates):
            raise ValueError(f"Gemini trả về {len(scores)} điểm cho {len(candidates)} candidates")
    except Exception as exc:
        print(f"  ⚠ Gemini cross-encoder rerank thất bại ({exc}), giữ nguyên thứ hạng gốc.")
        scores = [c.get("score", 0.0) for c in candidates]

    scored = []
    for candidate, score in zip(candidates, scores):
        item = candidate.copy()
        item["score"] = float(score)
        scored.append(item)

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def rerank_mmr(
    query_embedding: list[float],
    candidates: list[dict],
    top_k: int = 5,
    lambda_param: float = 0.7,
) -> list[dict]:
    """
    Maximal Marginal Relevance — chọn candidates vừa relevant vừa diverse.

    MMR = λ * sim(query, doc) - (1-λ) * max(sim(doc, selected_docs))

    Args:
        query_embedding: Vector embedding của query
        candidates: List of {'content': str, 'score': float, 'embedding': list, 'metadata': dict}
        top_k: Số lượng kết quả
        lambda_param: Trade-off giữa relevance (1.0) và diversity (0.0)

    Returns:
        List of top_k candidates selected by MMR.
    """
    if not candidates:
        return []

    selected: list[int] = []
    remaining = list(range(len(candidates)))

    for _ in range(min(top_k, len(candidates))):
        best_idx = None
        best_score = float("-inf")

        for idx in remaining:
            relevance = _cosine_similarity(query_embedding, candidates[idx]["embedding"])

            max_sim_to_selected = 0.0
            for sel_idx in selected:
                sim = _cosine_similarity(
                    candidates[idx]["embedding"], candidates[sel_idx]["embedding"]
                )
                max_sim_to_selected = max(max_sim_to_selected, sim)

            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim_to_selected

            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = idx

        selected.append(best_idx)
        remaining.remove(best_idx)

    results = []
    for idx in selected:
        item = candidates[idx].copy()
        item["score"] = round(
            _cosine_similarity(query_embedding, candidates[idx]["embedding"]), 4
        )
        results.append(item)
    return results


def rerank_rrf(
    ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60
) -> list[dict]:
    """
    Reciprocal Rank Fusion — gộp kết quả từ nhiều ranker.

    RRF(d) = Σ 1 / (k + rank_r(d))

    Args:
        ranked_lists: List of ranked result lists (mỗi list từ 1 ranker)
        top_k: Số lượng kết quả cuối cùng
        k: Smoothing constant (default=60, từ paper Cormack et al. 2009)

    Returns:
        List of top_k candidates sorted by RRF score descending.
    """
    rrf_scores: dict[str, float] = {}
    content_map: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            key = item["content"]
            rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (k + rank)
            content_map[key] = item

    sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    results = []
    for content, score in sorted_items[:top_k]:
        item = content_map[content].copy()
        item["score"] = score
        results.append(item)

    return results


# =============================================================================
# Main rerank interface
# =============================================================================

def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
    method: str = "rrf",  # "cross_encoder" | "mmr" | "rrf"
) -> list[dict]:
    """
    Unified reranking interface.

    Args:
        query: Câu truy vấn
        candidates: Danh sách candidates từ retrieval (một list duy nhất — nếu cần
            gộp nhiều ranked lists trước, gọi rerank_rrf(ranked_lists, ...) riêng,
            như Task 9 làm ở bước merge dense + sparse)
        top_k: Số lượng kết quả sau rerank
        method: Phương pháp reranking

    Returns:
        List of top_k reranked candidates.
    """
    if not candidates:
        return []

    if method == "cross_encoder":
        return rerank_cross_encoder(query, candidates, top_k)
    elif method == "mmr":
        from .task5_semantic_search import _embed_query

        query_embedding = _embed_query(query)
        for candidate in candidates:
            if "embedding" not in candidate:
                candidate["embedding"] = _embed_query(candidate["content"])
        return rerank_mmr(query_embedding, candidates, top_k)
    elif method == "rrf":
        # Một candidates list duy nhất -> RRF suy biến thành gán điểm theo thứ hạng
        # hiện có (vẫn hữu ích khi merge nhiều nguồn trước đó, xem Task 9).
        return rerank_rrf([candidates], top_k=top_k)
    else:
        raise ValueError(f"Unknown rerank method: {method}")


if __name__ == "__main__":
    # Test with dummy data
    dummy_candidates = [
        {"content": "Chính sách trả hàng và hoàn tiền Shopee trong 15 ngày", "score": 0.8, "metadata": {}},
        {"content": "Các phương thức thanh toán hỗ trợ trên Shopee Vietnam", "score": 0.6, "metadata": {}},
        {"content": "Quy định đăng bán sản phẩm dành cho người bán", "score": 0.5, "metadata": {}},
    ]
    results = rerank("chính sách trả hàng shopee", dummy_candidates, top_k=2)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content']}")
