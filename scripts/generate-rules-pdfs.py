#!/usr/bin/env python3
"""
Build official carrom rules PDFs from Hugo markdown chapters.

Reads:  content/{lang}/books/rules/official-carrom-rules/*.md
Writes: static/downloads/carrom-official-rules-{lang}.pdf
Cache:  .cache/book-html/carrom-official-rules-{lang}.html

Requires: markdown, LibreOffice (soffice on PATH).

Usage:
  python3 scripts/generate-rules-pdfs.py           # all 8 languages
  python3 scripts/generate-rules-pdfs.py da de     # specific languages
  python3 scripts/generate-rules-pdfs.py --html-only en
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from html import escape
from pathlib import Path

import markdown

REPO = Path(__file__).resolve().parents[1]
BOOK_DIR = "books/rules/official-carrom-rules"
CACHE_DIR = REPO / ".cache" / "book-html"
OUTPUT_DIR = REPO / "static" / "downloads"
BOOK_SLUG = "carrom-official-rules"

ALL_LANGS = ["en", "da", "de", "mr", "it", "fr", "si", "hi", "gu", "pl", "mni", "ta", "or"]

PRINT_CSS = """
@page { margin: 2cm; }
body {
  font-family: "Liberation Serif", "Noto Serif", Georgia, serif;
  font-size: 11pt;
  line-height: 1.45;
  color: #1a1a1a;
}
h1 { font-size: 20pt; margin: 0 0 0.5em; page-break-after: avoid; }
h2 { font-size: 14pt; margin: 1.2em 0 0.4em; page-break-after: avoid; }
h3 { font-size: 12pt; margin: 1em 0 0.3em; page-break-after: avoid; }
.chapter { page-break-before: always; }
.chapter:first-of-type { page-break-before: auto; }
.meta { color: #555; font-size: 9pt; margin-bottom: 1.5em; }
.callout {
  border: 1px solid #c4b5fd;
  background: #f5f3ff;
  padding: 0.6em 0.9em;
  margin: 1em 0;
  border-radius: 4px;
}
.callout-title { font-weight: bold; margin-bottom: 0.3em; }
.definition-grid {
  display: table;
  width: 100%;
  border-collapse: separate;
  border-spacing: 0.4em;
  margin: 0.8em 0;
}
.definition-card {
  display: table-cell;
  border: 1px solid #ddd;
  padding: 0.5em 0.7em;
  vertical-align: top;
  width: 25%;
}
.definition-card .term { font-weight: bold; display: block; margin-bottom: 0.2em; }
.definition-card .def { margin: 0; font-size: 10pt; }
ul { margin: 0.5em 0; padding-left: 1.4em; }
p { margin: 0.5em 0; }
em { color: #444; }
"""


def find_soffice() -> str:
    for candidate in (
        shutil.which("soffice"),
        "/opt/homebrew/bin/soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ):
        if candidate and Path(candidate).exists():
            return candidate
    raise RuntimeError(
        "LibreOffice not found. Install with: brew install --cask libreoffice"
    )


def split_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    if not raw.startswith("---"):
        return {}, raw
    end = raw.index("---", 3)
    fm_block = raw[3:end]
    body = raw[end + 3 :].lstrip("\n")
    fm: dict[str, str] = {}
    for line in fm_block.splitlines():
        m = re.match(r'^(\w+):\s*"(.*)"\s*$', line)
        if m:
            fm[m.group(1)] = m.group(2)
        else:
            m2 = re.match(r"^(\w+):\s*(\d+)\s*$", line)
            if m2:
                fm[m2.group(1)] = m2.group(2)
    return fm, body


def md_to_html(body: str) -> str:
    return markdown.markdown(
        body,
        extensions=["extra", "nl2br", "sane_lists"],
        output_format="html5",
    )


def chapter_weight(path: Path) -> int:
    fm, _ = split_frontmatter(path.read_text(encoding="utf-8"))
    return int(fm.get("weight", "999"))


def book_content_dir(lang: str) -> Path:
    return REPO / "content" / lang / BOOK_DIR


def html_path(lang: str) -> Path:
    return CACHE_DIR / f"{BOOK_SLUG}-{lang}.html"


def pdf_path(lang: str) -> Path:
    return OUTPUT_DIR / f"{BOOK_SLUG}-{lang}.pdf"


def build_html(lang: str) -> Path:
    book_dir = book_content_dir(lang)
    if not book_dir.is_dir():
        raise FileNotFoundError(f"Missing book content: {book_dir}")

    index_path = book_dir / "_index.md"
    if not index_path.exists():
        raise FileNotFoundError(f"Missing {index_path}")

    index_fm, index_body = split_frontmatter(index_path.read_text(encoding="utf-8"))
    title = index_fm.get("title", "Official Carrom Rules")
    author = index_fm.get("author", "International Carrom Federation")

    chapters = sorted(
        book_dir.glob("chapter-*.md"),
        key=chapter_weight,
    )
    if not chapters:
        raise FileNotFoundError(f"No chapters in {book_dir}")

    parts: list[str] = [
        "<!DOCTYPE html>",
        '<html lang="' + escape(lang) + '">',
        "<head>",
        '<meta charset="utf-8">',
        f"<title>{escape(title)}</title>",
        f"<style>{PRINT_CSS}</style>",
        "</head>",
        "<body>",
        f"<h1>{escape(title)}</h1>",
        f'<p class="meta">{escape(author)}</p>',
        md_to_html(index_body),
    ]

    for ch_path in chapters:
        ch_fm, ch_body = split_frontmatter(ch_path.read_text(encoding="utf-8"))
        ch_title = ch_fm.get("title", ch_path.stem)
        translated_by = ch_fm.get("translatedBy", "")
        parts.append('<div class="chapter">')
        parts.append(f"<h1>{escape(ch_title)}</h1>")
        if translated_by:
            parts.append(f'<p class="meta">{escape(translated_by)}</p>')
        parts.append(md_to_html(ch_body))
        parts.append("</div>")

    parts.extend(["</body>", "</html>"])
    out = html_path(lang)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"  wrote {out.relative_to(REPO)}", flush=True)
    return out


def convert_to_pdf(html: Path, pdf: Path) -> None:
    soffice = find_soffice()
    pdf.parent.mkdir(parents=True, exist_ok=True)
    outdir = pdf.parent
    cmd = [
        soffice,
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(outdir),
        str(html),
    ]
    print("  converting PDF …", flush=True)
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    generated = outdir / f"{html.stem}.pdf"
    if not generated.exists():
        raise RuntimeError(f"LibreOffice did not produce {generated}")
    if generated != pdf:
        generated.replace(pdf)
    size_kb = pdf.stat().st_size / 1024
    print(f"  wrote {pdf.relative_to(REPO)} ({size_kb:.0f} KB)", flush=True)


def process_lang(lang: str, *, html_only: bool, force: bool) -> None:
    print(f"\n=== {lang.upper()} ===", flush=True)
    cached = html_path(lang)
    if force or not cached.exists():
        build_html(lang)

    if html_only:
        return

    convert_to_pdf(cached, pdf_path(lang))


def main() -> None:
    args = [a for a in sys.argv[1:] if a.startswith("-")]
    langs = [a for a in sys.argv[1:] if not a.startswith("-")]
    html_only = "--html-only" in args
    force = "--force" in args

    targets = langs or ALL_LANGS
    for lang in targets:
        if lang not in ALL_LANGS:
            print(f"Unknown language: {lang}", file=sys.stderr)
            sys.exit(1)

    for lang in targets:
        process_lang(lang, html_only=html_only, force=force)

    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
