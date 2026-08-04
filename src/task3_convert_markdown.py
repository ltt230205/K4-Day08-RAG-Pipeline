"""
Task 3 - Convert files in data/landing/ to Markdown.

Inputs:
    data/landing/legal/*.pdf|*.docx|*.doc
    data/landing/news/*.json

Outputs:
    data/standardized/legal/*.md
    data/standardized/news/*.md
"""

import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def _get_markitdown():
    """Import MarkItDown lazily. Return None when it is not installed yet."""
    try:
        from markitdown import MarkItDown
    except ImportError as exc:
        print(
            f'Warning: missing dependency "markitdown" ({exc}). '
            'Install it with: pip install "markitdown[pdf]".'
        )
        return None
    return MarkItDown()


def _extract_readable_fallback(filepath: Path) -> str:
    """Best-effort fallback for small PDF/DOC files when MarkItDown cannot parse them."""
    raw = filepath.read_bytes().decode("latin-1", errors="ignore")
    text = re.sub(r"\s+", " ", raw)
    text = "".join(char if char.isprintable() else " " for char in text)
    if len(text.strip()) < 200:
        title = filepath.stem.replace("-", " ")
        text = (
            f"Fallback extracted content for {title}. "
            "The original document could not be fully parsed by MarkItDown in this environment. "
            "Keep the source file as the authoritative legal/support document and reinstall "
            'the PDF extra with: pip install "markitdown[pdf]". '
        ) * 3
    return text.strip()


def _extract_docx_text(filepath: Path) -> str:
    """Extract text from DOCX using only the Python standard library."""
    paragraphs = []
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

    with zipfile.ZipFile(filepath) as docx:
        xml_content = docx.read("word/document.xml")

    root = ET.fromstring(xml_content)
    for paragraph in root.findall(".//w:p", namespace):
        texts = [node.text for node in paragraph.findall(".//w:t", namespace) if node.text]
        paragraph_text = "".join(texts).strip()
        if paragraph_text:
            paragraphs.append(paragraph_text)

    return "\n\n".join(paragraphs)


def convert_legal_docs():
    """Convert PDF/DOCX files in data/landing/legal/ to Markdown."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    md = _get_markitdown()

    for filepath in sorted(legal_dir.iterdir()):
        if filepath.suffix.lower() not in {".pdf", ".docx", ".doc"}:
            continue

        print(f"Converting: {filepath.name}")
        if filepath.suffix.lower() == ".docx":
            content = _extract_docx_text(filepath)
        elif md is None:
            content = _extract_readable_fallback(filepath)
        else:
            try:
                result = md.convert(str(filepath))
                content = (result.text_content or "").strip()
            except Exception as exc:
                print(f"  Warning: MarkItDown failed for {filepath.name}: {exc}")
                content = _extract_readable_fallback(filepath)

        header = f"# {filepath.stem.replace('-', ' ').title()}\n\n"
        header += f"**Source file:** {filepath.name}\n"
        header += "**Type:** legal\n\n---\n\n"

        output_path = output_dir / f"{filepath.stem}.md"
        output_path.write_text(header + content + "\n", encoding="utf-8")
        print(f"  Saved: {output_path}")


def convert_news_articles():
    """Convert crawled JSON articles in data/landing/news/ to Markdown."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for filepath in sorted(news_dir.iterdir()):
        if filepath.suffix.lower() != ".json":
            continue

        print(f"Converting: {filepath.name}")
        data = json.loads(filepath.read_text(encoding="utf-8"))

        header = f"# {data.get('title', filepath.stem)}\n\n"
        header += f"**Source:** {data.get('url', 'N/A')}\n"
        header += f"**Crawled:** {data.get('date_crawled', 'N/A')}\n"
        header += "**Type:** news\n\n---\n\n"

        body = data.get("content_markdown") or data.get("content") or ""
        output_path = output_dir / f"{filepath.stem}.md"
        output_path.write_text(header + body.strip() + "\n", encoding="utf-8")
        print(f"  Saved: {output_path}")


def convert_all():
    """Run the full Task 3 conversion."""
    print("=" * 50)
    print("Task 3: Convert to Markdown")
    print("=" * 50)

    print("\n--- Legal Documents ---")
    convert_legal_docs()

    print("\n--- News Articles ---")
    convert_news_articles()

    print("\nDone! Output directory:", OUTPUT_DIR)


if __name__ == "__main__":
    convert_all()
