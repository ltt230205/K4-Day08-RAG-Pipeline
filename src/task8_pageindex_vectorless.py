"""
Task 8 — PageIndex Vectorless RAG.

Đăng ký tài khoản tại: https://pageindex.ai/
SDK & sample code: https://github.com/VectifyAI/PageIndex

PageIndex cho phép RAG mà không cần vector store — sử dụng structural understanding
của document thay vì embedding.

⚠️ Repo này hiện KHÔNG cấu hình PAGEINDEX_API_KEY trong .env (chỉ có GEMINI_API_KEY).
Vì vậy pageindex_search() dùng Gemini làm bộ máy suy luận cấu trúc thay thế: đọc toàn
bộ nội dung các file trong data/standardized/ (không chunk, không embedding) và yêu cầu
Gemini xác định + trích nguyên văn các đoạn liên quan nhất — đúng tinh thần "vectorless"
của PageIndex (đọc hiểu theo cấu trúc chương/mục thay vì tìm theo vector similarity),
chỉ khác ở chỗ bộ máy suy luận là Gemini thay vì dịch vụ pageindex.ai.

Nếu sau này có PAGEINDEX_API_KEY thật, hãy cắm dịch vụ pageindex.ai vào theo hướng dẫn
ở https://github.com/VectifyAI/PageIndex. Lưu ý: API `/retrieval` của PageIndex hiện đã
deprecated (vẫn hoạt động, nhưng response có field "deprecation" cảnh báo) và trả kết
quả trong "retrieved_nodes" — mỗi node có "relevant_contents": list[list[{section_title,
relevant_content}]]. In response thật ra (json.dumps(...)) trước khi viết logic parse,
đừng đoán schema từ ví dụ code cũ.
"""

import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-flash-latest"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


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


def _load_document_tree() -> list[dict]:
    """
    Đọc toàn bộ markdown trong data/standardized/ thành cấu trúc "tree" đơn giản
    (tiêu đề các mục + nội dung đầy đủ) — không chunk, không embedding.
    """
    documents = []
    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if md_file.name.startswith("."):
            continue

        content = md_file.read_text(encoding="utf-8").strip()
        if not content:
            continue

        headings = [
            line.strip("# ").strip()
            for line in content.splitlines()
            if line.strip().startswith("#")
        ]

        documents.append(
            {
                "source": md_file.name,
                "path": str(md_file.relative_to(STANDARDIZED_DIR)).replace("\\", "/"),
                "headings": headings,
                "content": content,
            }
        )

    return documents


def upload_documents():
    """
    Chuẩn bị tài liệu cho truy vấn cấu trúc (vectorless).

    Vì .env hiện KHÔNG có PAGEINDEX_API_KEY, hàm này không upload lên dịch vụ
    pageindex.ai — nó chỉ build một "document tree" cục bộ (tiêu đề mục + nội dung
    đầy đủ từng file). pageindex_search() sẽ dùng Gemini để suy luận trực tiếp trên
    tree này khi có truy vấn.
    """
    documents = _load_document_tree()
    if not documents:
        print("  ⚠ Không tìm thấy tài liệu nào trong data/standardized/")
        return

    if PAGEINDEX_API_KEY:
        print(
            "  ℹ Phát hiện PAGEINDEX_API_KEY nhưng tích hợp API thật của pageindex.ai "
            "chưa được implement ở đây (xem note ở đầu file — cần in response thật để "
            "xác nhận schema trước khi parse). Đang dùng chế độ Gemini local bên dưới."
        )

    print(f"  ✓ Đã chuẩn bị {len(documents)} tài liệu cho truy vấn cấu trúc (chế độ Gemini):")
    for doc in documents:
        print(f"    - {doc['source']} ({len(doc['headings'])} mục lục)")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval — đọc hiểu tài liệu theo cấu trúc chương/mục qua Gemini
    thay vì gọi dịch vụ pageindex.ai (repo không có PAGEINDEX_API_KEY).
    Dùng làm fallback khi hybrid search không có kết quả tốt.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,
            'score': float,
            'metadata': dict,
            'source': 'pageindex'   # Đánh dấu nguồn retrieval
        }
    """
    documents = _load_document_tree()
    if not documents:
        return []

    doc_blocks = [f"### TÀI LIỆU: {doc['source']}\n{doc['content']}" for doc in documents]
    corpus = "\n\n---\n\n".join(doc_blocks)

    prompt = (
        "Bạn là một công cụ truy xuất tài liệu KHÔNG dùng vector embedding (vectorless "
        "retrieval) — đọc hiểu toàn bộ tài liệu theo cấu trúc chương/mục để tìm thông tin, "
        "thay vì so khớp vector.\n\n"
        f"Dưới đây là toàn bộ các tài liệu nguồn:\n\n{corpus}\n\n---\n\n"
        f'Câu hỏi: "{query}"\n\n'
        f"Hãy xác định tối đa {top_k} đoạn/mục liên quan nhất TRỰC TIẾP giúp trả lời câu "
        "hỏi. Với mỗi đoạn, trích dẫn NGUYÊN VĂN (không diễn giải lại) từ đúng tài liệu "
        "nguồn. Nếu không có đoạn nào liên quan, trả về mảng rỗng [].\n"
        "Trả lời DUY NHẤT bằng JSON array, không kèm giải thích, đúng format:\n"
        '[{"source": "<tên file tài liệu>", "section_title": "<tiêu đề mục>", '
        '"content": "<đoạn trích nguyên văn>"}]'
    )

    raw = _call_gemini(prompt)
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    items = json.loads(match.group(0)) if match else json.loads(raw)

    results = []
    for i, item in enumerate(items[:top_k]):
        content = item.get("content", "")
        if not content:
            continue
        results.append(
            {
                "content": content,
                "score": round(max(0.0, 1.0 - i * 0.15), 2),
                "metadata": {
                    "section": item.get("section_title", ""),
                    "source": item.get("source", ""),
                },
                "source": "pageindex",
            }
        )

    return results[:top_k]


if __name__ == "__main__":
    if not GEMINI_API_KEY and not PAGEINDEX_API_KEY:
        print("⚠ Hãy set GEMINI_API_KEY (hoặc PAGEINDEX_API_KEY) trong file .env")
    else:
        print("Chuẩn bị tài liệu...")
        upload_documents()

        print("\nTest query:")
        results = pageindex_search("hồ sơ đăng ký hộ kinh doanh cá thể gồm những gì", top_k=3)
        for r in results:
            print(f"[{r['score']:.3f}] {r['content'][:100]}...")
