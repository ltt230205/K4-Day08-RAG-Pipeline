"""
Task 5 - Semantic Search Module.

This module uses the same embedding logic as Task 4. It queries ChromaDB when it
is installed and available; otherwise it searches the fallback JSON index written
by Task 4.
"""

import json
import math
from pathlib import Path

from src.task4_chunking_indexing import (
    CHROMA_DIR,
    COLLECTION_NAME,
    _hash_embedding,
    _embed_with_sentence_transformers,
)

FALLBACK_INDEX = CHROMA_DIR / "fallback_index.json"


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _embed_query(query: str) -> list[float]:
    try:
        return _embed_with_sentence_transformers([query])[0]
    except Exception:
        return _hash_embedding(query)


def _search_fallback_index(query: str, top_k: int) -> list[dict]:
    if not FALLBACK_INDEX.exists():
        return []

    query_embedding = _embed_query(query)
    records = json.loads(FALLBACK_INDEX.read_text(encoding="utf-8"))

    results = []
    for record in records:
        score = _cosine_similarity(query_embedding, record.get("embedding", []))
        results.append(
            {
                "content": record.get("content", ""),
                "score": round(float(score), 4),
                "metadata": record.get("metadata", {}),
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


def _search_chromadb(query: str, top_k: int) -> list[dict]:
    import chromadb

    query_embedding = _embed_query(query)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection(name=COLLECTION_NAME)
    raw_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    documents = raw_results.get("documents", [[]])[0]
    metadatas = raw_results.get("metadatas", [[]])[0]
    distances = raw_results.get("distances", [[]])[0]

    for document, metadata, distance in zip(documents, metadatas, distances):
        score = max(0.0, 1.0 - float(distance))
        output.append(
            {
                "content": document,
                "score": round(score, 4),
                "metadata": metadata or {},
            }
        )

    output.sort(key=lambda item: item["score"], reverse=True)
    return output[:top_k]


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Search chunks by vector similarity.

    Returns:
        List of {"content": str, "score": float, "metadata": dict}, sorted
        by score descending.
    """
    if not query or top_k <= 0:
        return []

    try:
        return _search_chromadb(query, top_k)
    except Exception:
        return _search_fallback_index(query, top_k)


if __name__ == "__main__":
    results = semantic_search("quy dinh tra hang hoan tien shopee", top_k=5)
    for result in results:
        print(f"[{result['score']:.3f}] {result['content'][:100]}...")
