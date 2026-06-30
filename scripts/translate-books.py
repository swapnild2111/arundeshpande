#!/usr/bin/env python3
"""Translate EN book markdown to DA/DE. Preserves HTML, images, URLs, and carrom terms."""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import requests
from deep_translator import GoogleTranslator

REPO = Path(__file__).resolve().parents[1]
EN_ROOT = REPO / "content" / "en" / "books"

DEEPL_API_KEY = "8c04b212-41b9-44d3-9af9-a0a21ac1a6d6:fx"
DEEPL_URL = "https://api-free.deepl.com/v2/translate"

# Languages that use DeepL for website content (EU languages DeepL supports)
EU_LANGS = {"da", "de", "it", "fr", "pl"}

# DeepL target language codes (differ from Hugo locale codes where needed)
DEEPL_LANG_MAP = {
    "da": "DA",
    "de": "DE",
    "it": "IT",
    "fr": "FR",
    "pl": "PL",
}


class DeepLTranslator:
    """Thin wrapper around DeepL free API using header-based auth."""

    def __init__(self, target: str) -> None:
        self._target = target
        self._headers = {
            "Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}",
            "Content-Type": "application/json",
        }

    def translate(self, text: str) -> str:
        if not text or not text.strip():
            return text
        resp = requests.post(
            DEEPL_URL,
            headers=self._headers,
            json={"text": [text], "target_lang": self._target, "source_lang": "EN"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["translations"][0]["text"]


# Per-language string replacements applied to every translated output.
# Fixes Google Translate quirks that are consistent for a given language.
OUTPUT_FIXES = {
    # Google Translate for Odia outputs ASCII pipe | as sentence-ender instead
    # of the proper Odia/Devanagari Danda ।  (U+0964).
    "or": [(" |", "।"), (" | ", "। ")],
}


class _PostProcessTranslator:
    """Wraps any translator and applies per-language string fixes to output."""
    def __init__(self, inner, fixes):
        self._inner = inner
        self._fixes = fixes

    def translate(self, text: str) -> str:
        result = self._inner.translate(text)
        for old, new in self._fixes:
            result = result.replace(old, new)
        return result


def get_translator(lang: str):
    """Return the right translator for the given Hugo locale."""
    if lang in EU_LANGS:
        t = DeepLTranslator(target=DEEPL_LANG_MAP[lang])
    else:
        gt_target = LANGS.get(lang, {}).get("gt_target", lang)
        t = GoogleTranslator(source="en", target=gt_target)
    fixes = OUTPUT_FIXES.get(lang)
    return _PostProcessTranslator(t, fixes) if fixes else t

BOOKS = [
    "students/carrom-techniques-and-skills",
    "rules/official-carrom-rules",
]

LANGS = {
    "da": {"chapter": "Kapitel", "translated_by": "Oversat fra engelsk (AI-udkast)."},
    "de": {"chapter": "Kapitel", "translated_by": "Aus dem Englischen übersetzt (KI-Entwurf)."},
    "mr": {"chapter": "अध्याय", "translated_by": "इंग्रजीमधून भाषांतर (AI मसुदा)."},
    "it": {"chapter": "Capitolo", "translated_by": "Tradotto dall'inglese (bozza AI)."},
    "fr": {"chapter": "Chapitre", "translated_by": "Traduit de l'anglais (brouillon IA)."},
    "si": {"chapter": "අධ්‍යාය", "translated_by": "ඉංග්‍රීසියෙන් පරිවර්තනය කරන ලදී (AI කෙටුම්පත)."},
    "hi": {"chapter": "अध्याय", "translated_by": "अंग्रेज़ी से अनुवाद (AI मसूदा)."},
    "gu": {"chapter": "પ્રકરણ", "translated_by": "અંગ્રેજીમાંથી અનુવાદિત (AI મુસદ્દો)."},
    "pl": {"chapter": "Rozdział", "translated_by": "Przetłumaczono z angielskiego (wersja robocza AI)."},
    # mni uses Meitei script; Google Translate code is mni-Mtei (not the Hugo locale "mni")
    "mni": {"chapter": "ꯃꯆꯤꯡ", "translated_by": "ꯏꯟꯒ꯭ꯂꯤꯁ ꯇꯥ ꯂꯧꯈꯠꯂꯛꯄ (AI ꯑꯣꯏꯕ ꯐꯥꯎꯕꯤꯁꯤꯡ).", "gt_target": "mni-Mtei"},
    "ta": {"chapter": "அத்தியாயம்", "translated_by": "ஆங்கிலத்திலிருந்து மொழிபெயர்க்கப்பட்டது (AI வரைவு)."},
    "or": {"chapter": "ଅଧ୍ୟାୟ", "translated_by": "ଇଂରାଜୀରୁ ଅନୁବାଦ (AI ଡ୍ରାଫ୍ଟ)."},
}

# International carrom terms — keep as-is during translation.
KEEP_TERMS = [
    "C/m",
    "C/B",
    "Striker",
    "Queen",
    "ICF",
    "MANTRA",
    "YouTube",
    "wikiHow",
    "Cut",
    "Double",
    "Press",
    "Touch",
    "Pair",
    "Canon",
    "Cannon",
    "Glance",
    "Brush",
    "Rebound",
    "Langda",
    "Hook",
    "Slip",
    "Bomb",
    "Force",
    "Doublé",
    "Cross Cut",
    "Minus Cut",
]

SKIP_KEYS = {"date", "weight", "pageCount", "category", "chapters", "cover", "aliases", "author"}


# Sentinels used to protect terms and HTML attributes from Google Translate.
#
# Earlier attempts:
#   - `KEEPTERMnnnn` — French translated the `KEEP` prefix to `GARDER`
#     ("to keep" in French), corrupting every sentinel.
#   - `zQzNNNNzQz` — survived French/Hindi but Marathi and Sinhala
#     translators inserted spaces between the digits, splitting one
#     sentinel into multiple fragments.
#
# Self-closing XML tag style (`<x42/>`) is the most robust pattern: every
# translator we tested (Google's PBMT and NMT models for de, da, mr, it,
# fr, si, hi) preserves tags verbatim because they're recognised as
# untranslatable markup, even when the surrounding language script is
# completely different from Latin.
SENTINEL_RE = re.compile(r"<x(\d{1,4})\s*/>", re.IGNORECASE)


def _make_key(idx: int) -> str:
    return f"<x{idx}/>"


def protect(text: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}
    idx = 0

    def stash(match: re.Match[str]) -> str:
        nonlocal idx
        key = _make_key(idx)
        placeholders[key] = match.group(0)
        idx += 1
        return key

    # URLs, image paths, HTML attributes
    text = re.sub(r"https?://[^\s\"'<>]+", stash, text)
    text = re.sub(r"/images/book/[^\s\"'<>]+", stash, text)
    text = re.sub(r'class="[^"]*"', stash, text)
    text = re.sub(r'href="[^"]*"', stash, text)
    text = re.sub(r'src="[^"]*"', stash, text)
    text = re.sub(r'target="[^"]*"', stash, text)
    text = re.sub(r'rel="[^"]*"', stash, text)
    text = re.sub(r'aria-[^=]+="[^"]*"', stash, text)
    text = re.sub(r'loading="[^"]*"', stash, text)
    text = re.sub(r'decoding="[^"]*"', stash, text)
    text = re.sub(r'alt="[^"]*"', stash, text)

    for term in sorted(KEEP_TERMS, key=len, reverse=True):
        def term_repl(m: re.Match[str], t: str = term) -> str:
            nonlocal idx
            key = _make_key(idx)
            placeholders[key] = m.group(0)
            idx += 1
            return key

        if " " in term or "/" in term:
            pattern = re.compile(re.escape(term), re.IGNORECASE)
        else:
            pattern = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
        text = pattern.sub(term_repl, text)

    return text, placeholders


def restore(text: str, placeholders: dict[str, str]) -> str:
    # Translators sometimes lower-case the entire output (e.g. for some
    # short fragments). Match sentinels case-insensitively, and replace
    # whatever case-variant the translator returned with the original.
    def repl(m: re.Match[str]) -> str:
        n = int(m.group(1))
        key = _make_key(n)
        return placeholders.get(key, m.group(0))
    return SENTINEL_RE.sub(repl, text)


def translate_text(text: str, translator, retries: int = 3) -> str:
    text = text.strip()
    if not text:
        return text
    protected, ph = protect(text)
    if not re.search(r"[A-Za-z]", protected):
        return text
    for attempt in range(retries):
        try:
            # Google limit ~5000 chars
            if len(protected) > 4500:
                parts = re.split(r"(?<=[.!?])\s+", protected)
                chunks: list[str] = []
                buf = ""
                for part in parts:
                    if len(buf) + len(part) + 1 > 4500:
                        if buf:
                            chunks.append(buf)
                        buf = part
                    else:
                        buf = f"{buf} {part}".strip() if buf else part
                if buf:
                    chunks.append(buf)
                out = " ".join(
                    restore(translator.translate(c), ph) for c in chunks if c.strip()
                )
                return out
            result = translator.translate(protected)
            return restore(result, ph)
        except Exception as exc:
            if attempt == retries - 1:
                print(f"  WARN translate failed: {exc}", file=sys.stderr)
                return text
            time.sleep(1.5 * (attempt + 1))
    return text


def translate_inline_html(html: str, translator) -> str:
    def repl(m: re.Match[str]) -> str:
        inner = m.group(1)
        if not inner.strip() or inner.strip().startswith("@@PH"):
            return m.group(0)
        if re.fullmatch(r"[\d\s.,/\-–—%]+", inner):
            return m.group(0)
        translated = translate_text(inner, translator)
        return f">{translated}<"

    return re.sub(r">([^<>]+?)<", repl, html)


def translate_body(body: str, translator) -> str:
    blocks = re.split(r"\n\n+", body.strip())
    out_blocks: list[str] = []
    for block in blocks:
        if not block.strip():
            continue
        if block.strip().startswith("!["):
            m = re.match(r"!\[(.*?)\]\((.*?)\)", block.strip())
            if m:
                alt, url = m.groups()
                alt_t = translate_text(alt, translator) if alt else alt
                out_blocks.append(f"![{alt_t}]({url})")
            else:
                out_blocks.append(block)
            continue
        if "<" in block and ">" in block:
            out_blocks.append(translate_inline_html(block, translator))
        elif block.lstrip().startswith("#"):
            lines = block.split("\n")
            lines[0] = translate_text(lines[0], translator)
            out_blocks.append("\n".join(lines))
        elif block.lstrip().startswith("*") and block.rstrip().endswith("*"):
            out_blocks.append(translate_text(block, translator))
        elif block.lstrip().startswith("—"):
            out_blocks.append(translate_text(block, translator))
        else:
            out_blocks.append(translate_text(block, translator))
        time.sleep(0.05)
    return "\n\n".join(out_blocks) + ("\n" if body.endswith("\n") else "")


def translate_title(title: str, lang: str, translator) -> str:
    chapter_word = LANGS[lang]["chapter"]
    m = re.match(r"^Chapter\s+(\d+)\s*[—-]\s*(.+)$", title)
    if m:
        num, rest = m.groups()
        rest_t = translate_text(rest, translator)
        return f"{chapter_word} {num} — {rest_t}"
    return translate_text(title, translator)


def translate_file(src: Path, dest: Path, lang: str, translator) -> None:
    raw = src.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(raw, encoding="utf-8")
        return

    end = raw.index("---", 3)
    fm = raw[3:end]
    body = raw[end + 3 :].lstrip("\n")

    fm = re.sub(r"\naliases:.*?(?=\n[a-zA-Z]|\Z)", "", fm, flags=re.DOTALL)

    title_m = re.search(r'^title:\s*"(.*)"', fm, re.MULTILINE)
    if title_m:
        new_title = translate_title(title_m.group(1), lang, translator)
        fm = re.sub(
            r'^title:\s*".*"',
            f'title: "{new_title}"',
            fm,
            count=1,
            flags=re.MULTILINE,
        )

    desc_m = re.search(r'^description:\s*"(.*)"', fm, re.MULTILINE)
    if desc_m:
        new_desc = translate_text(desc_m.group(1), translator)
        fm = re.sub(
            r'^description:\s*".*"',
            f'description: "{new_desc}"',
            fm,
            count=1,
            flags=re.MULTILINE,
        )

    tag_m = re.search(r'^tagLabel:\s*"(.*)"', fm, re.MULTILINE)
    if tag_m:
        new_tag = translate_text(tag_m.group(1), translator)
        fm = re.sub(
            r'^tagLabel:\s*".*"',
            f'tagLabel: "{new_tag}"',
            fm,
            count=1,
            flags=re.MULTILINE,
        )

    if src.name.startswith("chapter-") and "translatedBy:" not in fm:
        fm = fm.rstrip() + f'\ntranslatedBy: "{LANGS[lang]["translated_by"]}"\n'

    new_body = translate_body(body, translator) if body.strip() else body
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(f"---\n{fm.strip()}\n---\n{new_body}", encoding="utf-8")
    print(f"  wrote {dest.relative_to(REPO)}")


def main() -> None:
    targets = sys.argv[1:] or ["da", "de"]
    force = "--force" in targets
    if force:
        targets = [t for t in targets if t != "--force"]

    for lang in targets:
        print(f"\n=== {lang.upper()} ({'DeepL' if lang in EU_LANGS else 'Google'}) ===", flush=True)
        translator = get_translator(lang)
        for book in BOOKS:
            en_dir = EN_ROOT / book
            out_dir = REPO / "content" / lang / "books" / book
            print(f"Book: {book}", flush=True)
            for src in sorted(en_dir.glob("*.md")):
                dest = out_dir / src.name
                if dest.exists() and not force:
                    print(f"  skip {dest.relative_to(REPO)}", flush=True)
                    continue
                translate_file(src, dest, lang, translator)


if __name__ == "__main__":
    main()
