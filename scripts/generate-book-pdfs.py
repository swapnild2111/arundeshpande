#!/usr/bin/env python3
"""
Translate CarromTechniqandSkills.docx to all site languages and export PDFs.

Reads:  static/downloads/CarromTechniqandSkills.docx
Writes: static/downloads/carrom-techniques-and-skills-{lang}.pdf
Cache:  .cache/book-docx/carrom-techniques-and-skills-{lang}.docx

Requires: python-docx, deep-translator, LibreOffice (soffice on PATH).

Usage:
  python3 scripts/generate-book-pdfs.py              # all 8 languages
  python3 scripts/generate-book-pdfs.py da de        # specific languages
  python3 scripts/generate-book-pdfs.py --force da   # re-translate even if cached
  python3 scripts/generate-book-pdfs.py --pdf-only   # convert cached docx only
"""

from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from docx import Document
from deep_translator import GoogleTranslator

REPO = Path(__file__).resolve().parents[1]
SOURCE_DOCX = REPO / "static" / "downloads" / "CarromTechniqandSkills.docx"
CACHE_DIR = REPO / ".cache" / "book-docx"
OUTPUT_DIR = REPO / "static" / "downloads"
BOOK_SLUG = "carrom-techniques-and-skills"

ALL_LANGS = ["en", "da", "de", "mr", "it", "fr", "si", "hi", "gu", "pl", "mni", "ta", "te", "or"]

# Reuse translation helpers from translate-books.py
_spec = importlib.util.spec_from_file_location(
    "translate_books", REPO / "scripts" / "translate-books.py"
)
_tb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_tb)
translate_text = _tb.translate_text
get_translator = _tb.get_translator


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


def docx_path(lang: str) -> Path:
    return CACHE_DIR / f"{BOOK_SLUG}-{lang}.docx"


def pdf_path(lang: str) -> Path:
    return OUTPUT_DIR / f"{BOOK_SLUG}-{lang}.pdf"


def iter_paragraphs(doc: Document):
    for para in doc.paragraphs:
        yield para
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    yield para
    for section in doc.sections:
        for part in (section.header, section.footer):
            if part is None:
                continue
            for para in part.paragraphs:
                yield para
            for table in part.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for para in cell.paragraphs:
                            yield para


def should_translate(text: str) -> bool:
    text = text.strip()
    if not text:
        return False
    if re.fullmatch(r"[\d\s.,/\-–—%:;]+", text):
        return False
    return bool(re.search(r"[A-Za-z]", text))


def set_paragraph_text(para, text: str) -> None:
    if para.runs:
        para.runs[0].text = text
        for run in para.runs[1:]:
            run.text = ""
    else:
        para.add_run(text)


# Font overrides for scripts whose characters Calibri can't render.
SCRIPT_FONTS = {
    "mni": "Noto Sans Meetei Mayek",
}


def apply_script_font(doc: Document, font_name: str) -> None:
    """Set every run that contains non-ASCII text to the given font.

    Sets all four font slots (ascii, hAnsi, cs, eastAsia) so Word/LibreOffice
    uses the override regardless of which script slot it considers a glyph
    to belong to.
    """
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    for para in iter_paragraphs(doc):
        for run in para.runs:
            if not run.text or not any(ord(c) > 127 for c in run.text):
                continue
            rPr = run._element.get_or_add_rPr()
            # Remove any existing rFonts
            for existing in rPr.findall(qn("w:rFonts")):
                rPr.remove(existing)
            rFonts = OxmlElement("w:rFonts")
            for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
                rFonts.set(qn(attr), font_name)
            rPr.insert(0, rFonts)


def translate_docx(src: Path, dest: Path, lang: str) -> None:
    print(f"  translating docx → {lang} …", flush=True)
    doc = Document(str(src))
    translator = get_translator(lang)
    total = sum(1 for _ in iter_paragraphs(doc))
    done = 0

    for para in iter_paragraphs(doc):
        done += 1
        raw = para.text
        if not should_translate(raw):
            continue
        translated = translate_text(raw, translator)
        if translated != raw:
            set_paragraph_text(para, translated)
        if done % 40 == 0:
            print(f"    … {done}/{total} paragraphs", flush=True)
        time.sleep(0.05)

    if lang in SCRIPT_FONTS:
        print(f"  applying font override: {SCRIPT_FONTS[lang]}", flush=True)
        apply_script_font(doc, SCRIPT_FONTS[lang])

    dest.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(dest))
    print(f"  wrote {dest.relative_to(REPO)}", flush=True)


def copy_en_docx(dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE_DOCX, dest)
    print(f"  copied EN source → {dest.relative_to(REPO)}", flush=True)


def convert_to_pdf(docx: Path, pdf: Path) -> None:
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
        str(docx),
    ]
    print(f"  converting PDF …", flush=True)
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    generated = outdir / f"{docx.stem}.pdf"
    if not generated.exists():
        raise RuntimeError(f"LibreOffice did not produce {generated}")
    if generated != pdf:
        generated.replace(pdf)
    size_mb = pdf.stat().st_size / (1024 * 1024)
    print(f"  wrote {pdf.relative_to(REPO)} ({size_mb:.1f} MB)", flush=True)


def process_lang(lang: str, *, force: bool, pdf_only: bool) -> None:
    print(f"\n=== {lang.upper()} ===", flush=True)
    if not SOURCE_DOCX.exists():
        raise FileNotFoundError(f"Source docx missing: {SOURCE_DOCX}")

    cached = docx_path(lang)
    out_pdf = pdf_path(lang)

    if not pdf_only:
        if lang == "en":
            if force or not cached.exists():
                copy_en_docx(cached)
        elif force or not cached.exists():
            translate_docx(SOURCE_DOCX, cached, lang)
        elif not cached.exists():
            raise FileNotFoundError(f"No cached docx for {lang}; run without --pdf-only")

    if not cached.exists():
        raise FileNotFoundError(f"Missing docx for {lang}: {cached}")

    convert_to_pdf(cached, out_pdf)


def main() -> None:
    args = [a for a in sys.argv[1:] if a.startswith("-")]
    langs = [a for a in sys.argv[1:] if not a.startswith("-")]
    force = "--force" in args
    pdf_only = "--pdf-only" in args

    targets = langs or ALL_LANGS
    for lang in targets:
        if lang not in ALL_LANGS:
            print(f"Unknown language: {lang}", file=sys.stderr)
            sys.exit(1)

    for lang in targets:
        process_lang(lang, force=force, pdf_only=pdf_only)

    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
