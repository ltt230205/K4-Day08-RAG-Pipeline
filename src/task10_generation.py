"""
Task 10 - Generation with Citation.

Uses Gemini REST API via GEMINI_API_KEY/GEMINI_Key from .env. If the API call is
unavailable during local testing, the function returns a conservative extractive
answer from retrieved context with source labels.
"""

import os
from pathlib import Path

import requests

from src.task9_retrieval_pipeline import retrieve

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3
LLM_MODEL = "gemini-flash-latest"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{LLM_MODEL}:generateContent"

SYSTEM_PROMPT = """Bạn là trợ lý trả lời câu hỏi về chính sách thương mại điện tử và hỗ trợ khách hàng.

Quy tắc bắt buộc:
1. Chỉ sử dụng thông tin từ context được cung cấp.
2. Mỗi khẳng định quan trọng phải có citation theo dạng [tên nguồn].
3. Nếu context không đủ thông tin, nói: "Tôi không thể xác minh thông tin này từ nguồn hiện có".
4. Trả lời bằng tiếng Việt, ngắn gọn, rõ ràng.
5. Không suy luận ngoài context."""


def _load_env_file():
    try:
        from dotenv import load_dotenv

        load_dotenv()
        return
    except ImportError:
        pass

    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _gemini_api_key() -> str:
    _load_env_file()
    return os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_Key") or os.getenv("GEMINI_KEY", "")


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """
    Reorder chunks to reduce lost-in-the-middle effects.

    Keeps the best chunk first and places the second-best near the end:
        [1, 2, 3, 4, 5] -> [1, 3, 5, 4, 2]
    """
    if len(chunks) <= 2:
        return chunks

    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks with stable labels for citation."""
    context_parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata") or {}
        source = metadata.get("source") or metadata.get("path") or f"Source {index}"
        doc_type = metadata.get("type", "unknown")
        retrieval_source = chunk.get("source", "hybrid")
        score = float(chunk.get("score", 0.0))

        context_parts.append(
            f"[Document {index} | Source: {source} | Type: {doc_type} | "
            f"Retrieval: {retrieval_source} | Score: {score:.4f}]\n"
            f"{chunk.get('content', '').strip()}"
        )

    return "\n\n---\n\n".join(context_parts)


def _call_gemini(prompt: str) -> str:
    api_key = _gemini_api_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY/GEMINI_Key is not configured in .env")

    response = requests.post(
        GEMINI_URL,
        params={"key": api_key},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": TEMPERATURE,
                "topP": TOP_P,
            },
        },
        timeout=45,
    )
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def _extractive_fallback_answer(query: str, chunks: list[dict]) -> str:
    if not chunks:
        return "Tôi không thể xác minh thông tin này từ nguồn hiện có."

    lines = ["Tôi tìm thấy các thông tin liên quan trong nguồn hiện có:"]
    for chunk in chunks[:3]:
        metadata = chunk.get("metadata") or {}
        source = metadata.get("source") or metadata.get("path") or "nguồn không rõ"
        snippet = " ".join(chunk.get("content", "").split())[:450]
        lines.append(f"- {snippet} [{source}]")
    return "\n".join(lines)


def _format_chat_history(chat_history: list[dict] | None, max_turns: int = 6) -> str:
    if not chat_history:
        return ""

    recent = chat_history[-max_turns:]
    lines = []
    for message in recent:
        role = message.get("role", "user")
        content = " ".join(str(message.get("content", "")).split())
        if content:
            lines.append(f"{role}: {content[:500]}")
    return "\n".join(lines)


def generate_with_citation(
    query: str,
    top_k: int = TOP_K,
    chat_history: list[dict] | None = None,
) -> dict:
    """
    End-to-end RAG generation with citation.

    Returns:
        {"answer": str, "sources": list[dict], "retrieval_source": str}
    """
    history_text = _format_chat_history(chat_history)
    retrieval_query = f"{history_text}\nCurrent question: {query}" if history_text else query
    chunks = retrieve(retrieval_query, top_k=top_k)
    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)

    conversation_block = f"Conversation history:\n{history_text}\n\n" if history_text else ""
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"{conversation_block}"
        f"Context:\n{context}\n\n"
        "---\n\n"
        f"Question: {query}\n\n"
        "Hãy trả lời bằng tiếng Việt và ghi citation sau từng ý chính."
    )

    try:
        answer = _call_gemini(prompt)
    except Exception as exc:
        answer = _extractive_fallback_answer(query, reordered)
        answer += f"\n\n(Ghi chú kỹ thuật: chưa gọi được Gemini trong lần chạy này: {exc})"

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": chunks[0].get("source", "none") if chunks else "none",
    }


if __name__ == "__main__":
    for q in [
        "Shopee hỗ trợ những phương thức thanh toán nào?",
        "Làm sao để yêu cầu đổi trả hay hoàn tiền?",
        "Cần chuẩn bị bằng chứng gì khi yêu cầu hoàn tiền?",
    ]:
        print(f"\nQ: {q}")
        result = generate_with_citation(q)
        print(result["answer"])
        print(f"[Sources: {len(result['sources'])} | via {result['retrieval_source']}]")
