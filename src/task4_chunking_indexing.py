"""
Task 4 - Chunk Markdown documents and index them into ChromaDB.

Run:
    python -m src.task4_chunking_indexing
"""

import hashlib
import json
import math
import os
from pathlib import Path

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Recursive character splitting is a conservative choice for mixed Markdown:
# it prefers paragraph/header boundaries, then falls back to exact character cuts.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

# BAAI/bge-m3 is multilingual and works well for Vietnamese + English support docs.
# If sentence-transformers is not available, embed_chunks falls back to a deterministic
# 1024-dim hashing embedding so the local lab pipeline can still be exercised.
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

# ChromaDB is local, persistent, and does not require Docker.
VECTOR_STORE = "chromadb"
COLLECTION_NAME = "ecommerce_support_docs"


def load_documents() -> list[dict]:
    """
    Read all Markdown files from data/standardized/.

    Returns:
        List of {"content": str, "metadata": {"source": str, "type": str, "path": str}}
    """
    documents = []

    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if md_file.name.startswith("."):
            continue

        content = md_file.read_text(encoding="utf-8").strip()
        if not content:
            continue

        relative_path = md_file.relative_to(STANDARDIZED_DIR)
        doc_type = relative_path.parts[0] if len(relative_path.parts) > 1 else "unknown"
        documents.append(
            {
                "content": content,
                "metadata": {
                    "source": md_file.name,
                    "type": doc_type,
                    "path": str(relative_path).replace("\\", "/"),
                },
            }
        )

    return documents


def _fallback_split_text(text: str) -> list[str]:
    """Simple splitter used when langchain-text-splitters is not installed."""
    chunks = []
    start = 0
    step = CHUNK_SIZE - CHUNK_OVERLAP

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start += step

    return [chunk for chunk in chunks if chunk]


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Split documents into chunks.

    Returns:
        List of {"content": str, "metadata": dict}
    """
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        split_text = splitter.split_text
    except ImportError:
        split_text = _fallback_split_text

    chunks = []
    for doc in documents:
        for index, chunk_text in enumerate(split_text(doc["content"])):
            clean_text = chunk_text.strip()
            if not clean_text:
                continue

            chunks.append(
                {
                    "content": clean_text,
                    "metadata": {
                        **doc["metadata"],
                        "chunk_index": index,
                        "chunk_id": f"{doc['metadata']['source']}::{index}",
                    },
                }
            )

    return chunks


def _hash_embedding(text: str, dim: int = EMBEDDING_DIM) -> list[float]:
    """
    Deterministic fallback embedding.

    This is not as semantically strong as bge-m3, but it keeps the lab runnable
    when torch/sentence-transformers cannot be installed yet.
    """
    vector = [0.0] * dim
    tokens = text.lower().split()

    for token in tokens:
        digest = hashlib.md5(token.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:4], "little") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def _embed_with_sentence_transformers(texts: list[str]) -> list[list[float]]:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    return [embedding.tolist() for embedding in embeddings]


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Embed chunks with the configured model.

    Adds:
        chunk["embedding"] = list[float]
    """
    texts = [chunk["content"] for chunk in chunks]
    provider = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers").strip().lower()

    if provider == "hash":
        embeddings = [_hash_embedding(text) for text in texts]
    else:
        try:
            embeddings = _embed_with_sentence_transformers(texts)
        except Exception as exc:
            print(f"Warning: sentence-transformers embedding failed: {exc}")
            print("Falling back to deterministic hash embeddings.")
            embeddings = [_hash_embedding(text) for text in texts]

    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding

    return chunks


def _make_chroma_id(chunk: dict) -> str:
    raw_id = f"{chunk['metadata']['path']}::{chunk['metadata']['chunk_index']}"
    return hashlib.md5(raw_id.encode("utf-8")).hexdigest()


def index_to_vectorstore(chunks: list[dict]):
    """Store chunks in ChromaDB."""
    if VECTOR_STORE != "chromadb":
        raise ValueError(f"Unsupported vector store: {VECTOR_STORE}")

    try:
        import chromadb
    except ImportError as exc:
        print(f"Warning: chromadb is not installed: {exc}")
        print("Writing fallback local index to chroma_db/fallback_index.json.")
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        fallback_path = CHROMA_DIR / "fallback_index.json"
        fallback_path.write_text(
            json.dumps(
                [
                    {
                        "id": _make_chroma_id(chunk),
                        "content": chunk["content"],
                        "metadata": chunk["metadata"],
                        "embedding": chunk["embedding"],
                    }
                    for chunk in chunks
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.upsert(
        ids=[_make_chroma_id(chunk) for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=[chunk["metadata"] for chunk in chunks],
    )


def run_pipeline():
    """Run Task 4: load -> chunk -> embed -> index."""
    print("=" * 50)
    print("Task 4: Chunking & Indexing")
    print(f"  Chunking: {CHUNKING_METHOD} (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    print(f"  Embedding: {EMBEDDING_MODEL} (dim={EMBEDDING_DIM})")
    print(f"  Vector Store: {VECTOR_STORE}")
    print("=" * 50)

    docs = load_documents()
    print(f"\nLoaded {len(docs)} documents")

    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks")

    chunks = embed_chunks(chunks)
    print(f"Embedded {len(chunks)} chunks")

    index_to_vectorstore(chunks)
    print("Indexed to vector store")


if __name__ == "__main__":
    run_pipeline()
