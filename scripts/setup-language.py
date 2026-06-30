#!/usr/bin/env python3
"""Set up a new site language: i18n, about bio, and non-book content pages."""

from __future__ import annotations

import importlib.util
import re
import sys
import time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location(
    "translate_books", REPO / "scripts" / "translate-books.py"
)
_tb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_tb)
translate_body = _tb.translate_body
translate_text = _tb.translate_text
get_translator = _tb.get_translator
EU_LANGS = _tb.EU_LANGS

SKIP_BOOK_PREFIXES = (
    "books/students/carrom-techniques-and-skills",
    "books/rules/official-carrom-rules",
)


def translate_i18n(lang: str, translator) -> None:
    src = REPO / "i18n" / "en.toml"
    dest = REPO / "i18n" / f"{lang}.toml"
    text = src.read_text(encoding="utf-8")
    out: list[str] = []

    for m in re.finditer(r"\[(\w+)\]\s*\nother\s*=\s*\"((?:[^\"\\]|\\.)*)\"", text):
        key, val = m.group(1), m.group(2)
        translated = translate_text(val, translator)
        # If the English string doesn't end with punctuation, strip any
        # trailing sentence-ender the translator added (e.g. Odia danda ।)
        if val and val[-1] not in ".!?":
            translated = translated.rstrip("।.")
        # Escape any unescaped double quotes so the TOML value stays valid
        translated = translated.replace('\\"', '"').replace('"', '\\"')
        out.append(f"[{key}]")
        out.append(f'other = "{translated}"')
        out.append("")

    dest.write_text("\n".join(out).strip() + "\n", encoding="utf-8")
    print(f"wrote {dest.relative_to(REPO)}")


def _tr_quoted(text: str, translator) -> str:
    """Translate then escape inner quotes so the YAML "..."-quoted value stays valid."""
    val = translate_text(text, translator)
    return val.replace('\\"', '"').replace('"', '\\"')


def translate_markdown_page(src: Path, dest: Path, translator) -> None:
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
            val = _tr_quoted(m.group(1), translator)
            fm = re.sub(
                rf'^{field}:\s*".*"',
                f'{field}: "{val}"',
                fm,
                count=1,
                flags=re.MULTILINE,
            )

    fm = re.sub(
        r'^(\s+-\s+)label:\s*"([^"]+)"',
        lambda m: f'{m.group(1)}label: "{_tr_quoted(m.group(2), translator)}"',
        fm,
        flags=re.MULTILINE,
    )
    fm = re.sub(
        r'^(\s+)label:\s*"([^"]+)"',
        lambda m: f'{m.group(1)}label: "{_tr_quoted(m.group(2), translator)}"',
        fm,
        flags=re.MULTILINE,
    )
    fm = re.sub(
        r'^(\s+)title:\s*"([^"]+)"',
        lambda m: f'{m.group(1)}title: "{_tr_quoted(m.group(2), translator)}"',
        fm,
        flags=re.MULTILINE,
    )
    fm = re.sub(
        r'^(\s+)alt:\s*"([^"]+)"',
        lambda m: f'{m.group(1)}alt: "{_tr_quoted(m.group(2), translator)}"',
        fm,
        flags=re.MULTILINE,
    )

    new_body = translate_body(body, translator) if body.strip() else body
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(f"---\n{fm.strip()}\n---\n{new_body}", encoding="utf-8")
    print(f"  wrote {dest.relative_to(REPO)}")


def translate_about(lang: str, translator) -> None:
    path = REPO / "data" / "about.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))

    # Translate each paragraph separately so sentence structure stays coherent,
    # but use XML-style bold tags that survive translation better than **.
    # Pattern: replace **text** with <b>text</b>, translate, restore.
    en_text = data["en"].strip()
    paragraphs = re.split(r"\n\n+", en_text)
    out_paras = []
    for para in paragraphs:
        if not para.strip():
            continue
        # Replace ** markers with XML tags Google preserves
        tagged = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", para)
        translated = translate_text(tagged, translator)
        # Restore <b>...</b> back to **..**  (allow spaces Google adds inside tags)
        restored = re.sub(r"<\s*b\s*>\s*(.*?)\s*<\s*/\s*b\s*>", r"**\1**", translated, flags=re.DOTALL)
        out_paras.append(restored)
    data[lang] = "\n\n".join(out_paras)

    path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"updated {path.relative_to(REPO)} ({lang})")


def setup_language(lang: str) -> None:
    translator = get_translator(lang)
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
