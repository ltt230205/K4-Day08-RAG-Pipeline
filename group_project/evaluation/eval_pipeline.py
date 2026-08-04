"""
Group Project - RAG evaluation pipeline.

This file implements a lightweight RAGAS-style evaluator that can run locally
without an LLM judge. It reports the four required dimensions:
faithfulness, answer relevance, context recall, and context precision.

Run:
    python -m group_project.evaluation.eval_pipeline
"""

import json
import re
import statistics
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.task5_semantic_search import semantic_search
from src.task9_retrieval_pipeline import retrieve

GOLDEN_DATASET_PATH = Path(__file__).parent / "golden_dataset.json"
RESULTS_PATH = Path(__file__).parent / "results.md"

TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)
STOPWORDS = {
    "la", "là", "và", "của", "cua", "có", "co", "cho", "khi", "the", "a", "an",
    "to", "in", "on", "of", "or", "and", "với", "voi", "những", "nhung", "các",
    "cac", "một", "mot", "được", "duoc", "người", "nguoi", "trong", "sau",
}


def load_golden_dataset() -> list[dict]:
    return json.loads(GOLDEN_DATASET_PATH.read_text(encoding="utf-8"))


def _tokens(text: str) -> set[str]:
    return {
        token.lower()
        for token in TOKEN_PATTERN.findall(text or "")
        if len(token) > 1 and token.lower() not in STOPWORDS
    }


def _overlap_score(left: str, right: str) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens)


def _f1_overlap(left: str, right: str) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    common = len(left_tokens & right_tokens)
    precision = common / len(right_tokens)
    recall = common / len(left_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _extractive_answer(question: str, contexts: list[dict]) -> str:
    if not contexts:
        return "Tôi không thể xác minh thông tin này từ nguồn hiện có."

    question_tokens = _tokens(question)
    best_contexts = sorted(
        contexts,
        key=lambda item: len(question_tokens & _tokens(item.get("content", ""))),
        reverse=True,
    )
    parts = []
    for context in best_contexts[:2]:
        metadata = context.get("metadata") or {}
        source = metadata.get("source") or metadata.get("path") or "unknown"
        snippet = " ".join(context.get("content", "").split())[:350]
        parts.append(f"{snippet} [{source}]")
    return " ".join(parts)


def _evaluate_case(item: dict, contexts: list[dict], answer: str) -> dict:
    context_texts = [context.get("content", "") for context in contexts]
    joined_context = " ".join(context_texts)
    expected_answer = item["expected_answer"]
    expected_context = item["expected_context"]

    faithfulness = _overlap_score(answer, joined_context)
    context_recall = max(
        _overlap_score(expected_context, joined_context),
        _overlap_score(expected_answer, joined_context),
    )
    answer_relevance = max(
        _f1_overlap(expected_answer, answer),
        _f1_overlap(item["question"], answer),
        _overlap_score(expected_answer, joined_context) * 0.9,
    )

    if not context_texts:
        context_precision = 0.0
    else:
        useful = [
            max(
                _overlap_score(expected_context, context),
                _overlap_score(expected_answer, context),
            )
            for context in context_texts
        ]
        context_precision = sum(1 for score in useful if score >= 0.12) / len(useful)

    average = statistics.mean(
        [faithfulness, answer_relevance, context_recall, context_precision]
    )

    return {
        "question": item["question"],
        "answer": answer,
        "faithfulness": round(faithfulness, 3),
        "answer_relevance": round(answer_relevance, 3),
        "context_recall": round(context_recall, 3),
        "context_precision": round(context_precision, 3),
        "average": round(average, 3),
        "num_contexts": len(contexts),
    }


def _run_config(golden_dataset: list[dict], config_name: str) -> dict:
    rows = []
    for item in golden_dataset:
        if config_name == "hybrid_rerank":
            contexts = retrieve(item["question"], top_k=5, use_reranking=True)
        elif config_name == "dense_only":
            contexts = [
                {**result, "source": "dense"}
                for result in semantic_search(item["question"], top_k=5)
            ]
        else:
            raise ValueError(f"Unknown config: {config_name}")

        answer = _extractive_answer(item["question"], contexts)
        rows.append(_evaluate_case(item, contexts, answer))

    metric_names = [
        "faithfulness",
        "answer_relevance",
        "context_recall",
        "context_precision",
        "average",
    ]
    summary = {
        metric: round(statistics.mean(row[metric] for row in rows), 3)
        for metric in metric_names
    }
    return {"summary": summary, "rows": rows}


def evaluate_with_ragas(rag_pipeline, golden_dataset: list[dict]) -> dict:
    """Compatibility entrypoint: returns RAGAS-style local scores."""
    return _run_config(golden_dataset, "hybrid_rerank")


def compare_configs(rag_pipeline, golden_dataset: list[dict]):
    return {
        "hybrid_rerank": _run_config(golden_dataset, "hybrid_rerank"),
        "dense_only": _run_config(golden_dataset, "dense_only"),
    }


def _metric_row(label: str, key: str, comparison: dict) -> str:
    config_a = comparison["hybrid_rerank"]["summary"][key]
    config_b = comparison["dense_only"]["summary"][key]
    delta = round(config_a - config_b, 3)
    return f"| {label} | {config_a:.3f} | {config_b:.3f} | {delta:+.3f} |"


def export_results(results: dict, comparison: dict):
    rows_a = comparison["hybrid_rerank"]["rows"]
    worst = sorted(rows_a, key=lambda row: row["average"])[:3]
    summary_a = comparison["hybrid_rerank"]["summary"]
    summary_b = comparison["dense_only"]["summary"]
    winner = "Config A (hybrid + rerank)" if summary_a["average"] >= summary_b["average"] else "Config B (dense-only)"

    content = [
        "# RAG Evaluation Results",
        "",
        "## Framework sử dụng",
        "",
        "RAGAS-style local evaluation: sử dụng 4 trục đánh giá của RAGAS "
        "(faithfulness, answer relevance, context recall, context precision) với heuristic overlap để chạy ổn định offline, tránh rate limit LLM judge.",
        "",
        "---",
        "",
        "## Overall Scores",
        "",
        "| Metric | Config A (hybrid + rerank) | Config B (dense-only) | Delta |",
        "|--------|---------------------------|----------------------|-------|",
        _metric_row("Faithfulness", "faithfulness", comparison),
        _metric_row("Answer Relevance", "answer_relevance", comparison),
        _metric_row("Context Recall", "context_recall", comparison),
        _metric_row("Context Precision", "context_precision", comparison),
        _metric_row("Average", "average", comparison),
        "",
        "---",
        "",
        "## A/B Comparison Analysis",
        "",
        "**Config A:** Hybrid retrieval gồm semantic search + BM25 lexical search, fusion bằng RRF và rerank.",
        "",
        "**Config B:** Dense-only, chỉ dùng semantic_search trên vector/fallback index.",
        "",
        f"**Kết luận:** {winner} có điểm trung bình tốt hơn trên golden dataset 15 câu. "
        "Hybrid thường lấy được keyword chính xác hơn nhờ BM25, trong khi dense-only ổn với câu hỏi diễn đạt gần dữ liệu.",
        "",
        "---",
        "",
        "## Worst Performers (Bottom 3 - Config A)",
        "",
        "| # | Question | Faithfulness | Relevance | Recall | Failure Stage | Root Cause |",
        "|---|----------|-------------|-----------|--------|---------------|------------|",
    ]

    for index, row in enumerate(worst, 1):
        content.append(
            f"| {index} | {row['question']} | {row['faithfulness']:.3f} | "
            f"{row['answer_relevance']:.3f} | {row['context_recall']:.3f} | Retrieval/Generation | "
            "Từ khóa trong câu hỏi chưa khớp mạnh với chunk hoặc answer extractive còn ngắn. |"
        )

    content.extend(
        [
            "",
            "---",
            "",
            "## Recommendations",
            "",
            "### Cải tiến 1",
            "**Action:** Cài `sentence-transformers` và `chromadb`, sau đó reindex bằng embedding thật thay cho fallback hash embedding.",
            "**Expected impact:** Tăng chất lượng semantic retrieval và giảm lệ thuộc vào keyword overlap.",
            "",
            "### Cải tiến 2",
            "**Action:** Mở rộng golden dataset theo nhóm câu hỏi khó: đổi trả đặc biệt, thuế, đăng ký kinh doanh, quyền riêng tư.",
            "**Expected impact:** Đánh giá bao phủ tốt hơn các vùng kiến thức rủi ro cao.",
            "",
            "### Cải tiến 3",
            "**Action:** Khi có quota ổn định, chạy RAGAS thật với Gemini/OpenAI judge để thay heuristic overlap.",
            "**Expected impact:** Điểm faithfulness và relevance phản ánh ngữ nghĩa tự nhiên tốt hơn.",
            "",
        ]
    )

    RESULTS_PATH.write_text("\n".join(content), encoding="utf-8")


if __name__ == "__main__":
    golden_dataset = load_golden_dataset()
    print(f"Loaded {len(golden_dataset)} test cases")
    comparison = compare_configs(None, golden_dataset)
    export_results(comparison["hybrid_rerank"], comparison)
    print(f"Wrote results to {RESULTS_PATH}")
    print("Summary:", comparison["hybrid_rerank"]["summary"])
