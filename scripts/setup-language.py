#!/usr/bin/env python3
"""Set up a new site language: i18n, about bio, and non-book content pages."""

from __future__ import annotations

import importlib.util
import re
import sys
import time
from pathlib import Path

import yaml
from deep_translator import GoogleTranslator

REPO = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location(
    "translate_books", REPO / "scripts" / "translate-books.py"
)
_tb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_tb)
translate_body = _tb.translate_body
translate_text = _tb.translate_text

SKIP_BOOK_PREFIXES = (
    "books/students/carrom-techniques-and-skills",
    "books/rules/official-carrom-rules",
)


def translate_i18n(lang: str, translator: GoogleTranslator) -> None:
    src = REPO / "i18n" / "en.toml"
    dest = REPO / "i18n" / f"{lang}.toml"
    text = src.read_text(encoding="utf-8")
    out: list[str] = []

    for m in re.finditer(r"\[(\w+)\]\s*\nother\s*=\s*\"((?:[^\"\\]|\\.)*)\"", text):
        key, val = m.group(1), m.group(2)
        translated = translate_text(val, translator)
        out.append(f"[{key}]")
        out.append(f'other = "{translated}"')
        out.append("")

    dest.write_text("\n".join(out).strip() + "\n", encoding="utf-8")
    print(f"wrote {dest.relative_to(REPO)}")


def translate_markdown_page(src: Path, dest: Path, translator: GoogleTranslator) -> None:
    raw = src.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(raw, encoding="utf-8")
        return

    end = raw.index("---", 3)
    fm = raw[3:end]
    body = raw[end + 3 :].lstrip("\n")

    for field in ("title", "description"):
        m = re.search(rf'^{field}:\s*"(.*)"', fm, re.MULTILINE)
        if m:
            val = translate_text(m.group(1), translator)
            fm = re.sub(
                rf'^{field}:\s*".*"',
                f'{field}: "{val}"',
                fm,
                count=1,
                flags=re.MULTILINE,
            )

    fm = re.sub(
        r'^(\s+-\s+)label:\s*"([^"]+)"',
        lambda m: f'{m.group(1)}label: "{translate_text(m.group(2), translator)}"',
        fm,
        flags=re.MULTILINE,
    )
    fm = re.sub(
        r'^(\s+)label:\s*"([^"]+)"',
        lambda m: f'{m.group(1)}label: "{translate_text(m.group(2), translator)}"',
        fm,
        flags=re.MULTILINE,
    )
    fm = re.sub(
        r'^(\s+)title:\s*"([^"]+)"',
        lambda m: f'{m.group(1)}title: "{translate_text(m.group(2), translator)}"',
        fm,
        flags=re.MULTILINE,
    )
    fm = re.sub(
        r'^(\s+)alt:\s*"([^"]+)"',
        lambda m: f'{m.group(1)}alt: "{translate_text(m.group(2), translator)}"',
        fm,
        flags=re.MULTILINE,
    )

    new_body = translate_body(body, translator) if body.strip() else body
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(f"---\n{fm.strip()}\n---\n{new_body}", encoding="utf-8")
    print(f"  wrote {dest.relative_to(REPO)}")


def translate_about(lang: str, translator: GoogleTranslator) -> None:
    path = REPO / "data" / "about.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data[lang] = translate_body(data["en"].strip(), translator)
    path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"updated {path.relative_to(REPO)} ({lang})")


# Some Hugo locale codes don't match Google Translate codes directly.
GT_OVERRIDES = {
    "mni": "mni-Mtei",  # Meitei script; Hugo locale is "mni"
}


def setup_language(lang: str) -> None:
    gt_target = GT_OVERRIDES.get(lang, lang)
    translator = GoogleTranslator(source="en", target=gt_target)
    print(f"\n=== {lang.upper()} site shell ===")
    print("=== i18n ===")
    translate_i18n(lang, translator)
    print("\n=== about.yaml ===")
    translate_about(lang, translator)

    print("\n=== content pages ===")
    en_root = REPO / "content" / "en"
    out_root = REPO / "content" / lang

    for src in sorted(en_root.rglob("*.md")):
        rel = src.relative_to(en_root)
        if any(str(rel).startswith(p) for p in SKIP_BOOK_PREFIXES):
            continue
        translate_markdown_page(src, out_root / rel, translator)
        time.sleep(0.05)


def main() -> None:
    langs = sys.argv[1:] or ["it"]
    for lang in langs:
        setup_language(lang)


if __name__ == "__main__":
    main()
