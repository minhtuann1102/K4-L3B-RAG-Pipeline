"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.
Chủ đề: NỘI QUY QUẢN LÝ, SỬ DỤNG NHÀ CHUNG CƯ
"""

import json
from pathlib import Path
import docx

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"


def docx_to_markdown(docx_path: Path) -> str:
    """Chuyển đổi file docx sang Markdown sạch có cấu trúc."""
    doc = docx.Document(str(docx_path))
    lines = []
    
    for p in doc.paragraphs:
        style_name = p.style.name.lower()
        text = p.text.strip()
        if not text:
            continue
            
        if "heading 1" in style_name or "tiêu đề 1" in style_name:
            lines.append(f"# {text}\n")
        elif "heading 2" in style_name or "tiêu đề 2" in style_name:
            lines.append(f"## {text}\n")
        elif "heading 3" in style_name or "tiêu đề 3" in style_name:
            lines.append(f"### {text}\n")
        elif "heading 4" in style_name or "tiêu đề 4" in style_name:
            lines.append(f"#### {text}\n")
        else:
            # Check if it starts with list bullet or number
            lines.append(f"{text}\n")
            
    return "\n".join(lines)


def convert_legal_docs() -> None:
    """Convert tài liệu legal DOCX/PDF sang Markdown."""
    legal_landing = LANDING_DIR / "legal"
    legal_std = STANDARDIZED_DIR / "legal"
    legal_proc = PROCESSED_DIR / "legal"
    
    legal_std.mkdir(parents=True, exist_ok=True)
    legal_proc.mkdir(parents=True, exist_ok=True)
    
    converted_count = 0
    for path in legal_landing.iterdir():
        if path.suffix.lower() in {".docx", ".doc"}:
            md_content = docx_to_markdown(path)
            if not md_content.strip():
                continue
                
            out_name = f"{path.stem}.md"
            (legal_std / out_name).write_text(md_content, encoding="utf-8")
            (legal_proc / out_name).write_text(md_content, encoding="utf-8")
            (PROCESSED_DIR / out_name).write_text(md_content, encoding="utf-8")
            converted_count += 1
            print(f"[Legal] Converted: {path.name} -> {out_name}")
            
    print(f"Total legal docs converted: {converted_count}")


def convert_news_articles() -> None:
    """Convert các file JSON news sang Markdown sạch có metadata."""
    news_landing = LANDING_DIR / "news"
    news_std = STANDARDIZED_DIR / "news"
    news_proc = PROCESSED_DIR / "news"
    
    news_std.mkdir(parents=True, exist_ok=True)
    news_proc.mkdir(parents=True, exist_ok=True)
    
    converted_count = 0
    for path in sorted(news_landing.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            title = data.get("title", path.stem)
            url = data.get("url", "")
            date_crawled = data.get("date_crawled", "")
            content_md = data.get("content_markdown", "")
            
            # Format header with metadata
            header = (
                f"# {title}\n\n"
                f"- **Source URL:** {url}\n"
                f"- **Date Crawled:** {date_crawled}\n"
                f"- **Domain:** NỘI QUY QUẢN LÝ, SỬ DỤNG NHÀ CHUNG CƯ\n\n"
                f"---\n\n"
            )
            
            # Clean redundant repeated title if markdown body starts with it
            body = content_md.strip()
            if body.startswith(f"# {title}"):
                body = body[len(f"# {title}"):].strip()
                
            full_md = header + body + "\n"
            
            out_name = f"{path.stem}.md"
            (news_std / out_name).write_text(full_md, encoding="utf-8")
            (news_proc / out_name).write_text(full_md, encoding="utf-8")
            (PROCESSED_DIR / out_name).write_text(full_md, encoding="utf-8")
            converted_count += 1
            print(f"[News] Converted: {path.name} -> {out_name}")
        except Exception as e:
            print(f"[News] Failed to convert {path.name}: {e}")
            
    print(f"Total news articles converted: {converted_count}")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing sang Markdown sạch."""
    STANDARDIZED_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    convert_legal_docs()
    convert_news_articles()
    print(f"\nAll documents converted and saved to:")
    print(f" - {STANDARDIZED_DIR}")
    print(f" - {PROCESSED_DIR}")


if __name__ == "__main__":
    convert_all()

