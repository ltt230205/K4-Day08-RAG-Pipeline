"""
Task 6 - Lexical Search Module.

Default method: BM25. If rank-bm25 is not installed, this module uses a small
standard-library BM25 implementation with the same k1/b intuition.
"""

import json
import math
import re
from collections import Counter
from pathlib import Path

from src.task4_chunking_indexing import CHROMA_DIR, STANDARDIZED_DIR, chunk_documents, load_documents

FALLBACK_INDEX = CHROMA_DIR / "fallback_index.json"
TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)


def _tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def _load_corpus() -> list[dict]:
    if FALLBACK_INDEX.exists():
        records = json.loads(FALLBACK_INDEX.read_text(encoding="utf-8"))
        return [
            {
                "content": record.get("content", ""),
                "metadata": record.get("metadata", {}),
            }
            for record in records
            if record.get("content")
        ]

    if STANDARDIZED_DIR.exists():
        return chunk_documents(load_documents())

    return []


CORPUS: list[dict] = _load_corpus()


class SimpleBM25:
    """Small BM25Okapi-compatible fallback."""

    def __init__(self, tokenized_corpus: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.tokenized_corpus = tokenized_corpus
        self.k1 = k1
        self.b = b
        self.doc_lengths = [len(doc) for doc in tokenized_corpus]
        self.avgdl = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0.0
        self.term_freqs = [Counter(doc) for doc in tokenized_corpus]
        self.idf = self._calculate_idf()

    def _calculate_idf(self) -> dict[str, float]:
        doc_count = len(self.tokenized_corpus)
        document_frequency: Counter[str] = Counter()
        for doc in self.tokenized_corpus:
            document_frequency.update(set(doc))

        return {
            term: math.log(1 + (doc_count - freq + 0.5) / (freq + 0.5))
            for term, freq in document_frequency.items()
        }

    def get_scores(self, query_tokens: list[str]) -> list[float]:
        scores = []
        for index, term_freq in enumerate(self.term_freqs):
            doc_len = self.doc_lengths[index]
            score = 0.0
            for token in query_tokens:
                tf = term_freq.get(token, 0)
                if tf == 0:
                    continue

                denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
                score += self.idf.get(token, 0.0) * (tf * (self.k1 + 1)) / denominator
            scores.append(score)
        return scores


def build_bm25_index(corpus: list[dict]):
    """
    Build a BM25 index from corpus.

    Args:
        corpus: List of {"content": str, "metadata": dict}
    """
    tokenized_corpus = [_tokenize(doc["content"]) for doc in corpus]

    try:
        from rank_bm25 import BM25Okapi

        return BM25Okapi(tokenized_corpus)
    except ImportError:
        return SimpleBM25(tokenized_corpus)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Search chunks by keyword relevance using BM25.

    Returns:
        List of {"content": str, "score": float, "metadata": dict}, sorted
        by score descending.
    """
    if not query or top_k <= 0 or not CORPUS:
        return []

    bm25 = build_bm25_index(CORPUS)
    query_tokens = _tokenize(query)
    scores = bm25.get_scores(query_tokens)

    ranked_indices = sorted(range(len(scores)), key=lambda idx: scores[idx], reverse=True)
    results = []
    for index in ranked_indices[:top_k]:
        score = float(scores[index])
        results.append(
            {
                "content": CORPUS[index]["content"],
                "score": round(score, 4),
                "metadata": CORPUS[index].get("metadata", {}),
            }
        )

    return results[:top_k]


if __name__ == "__main__":
    results = lexical_search("phuong thuc thanh toan shopee", top_k=5)
    for result in results:
        print(f"[{result['score']:.3f}] {result['content'][:100]}...")
