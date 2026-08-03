#!/usr/bin/env python3
"""
Extract PlayersGuideEnglish.docx into Hugo markdown chapters for the
carrom-players-guide book.

Reads:
  static/downloads/PlayersGuideEnglish.docx
    (unzipped on demand to .cache/players-guide-docx/)
Writes:
  content/en/books/students/carrom-players-guide/chapter-NN.md
  static/images/book/players-guide/fig-NN.jpg   (the 41 inline images,
    renamed from image1.jpeg..image41.jpeg by natural order)

Chapter map:
  Boundaries are keyed by paragraph indices from walk_paragraphs() (i.e.,
  paragraphs that actually carry text OR an inline image). The docx has
  explicit "Chapter N" heading markers we can rely on:
    #  9 -> Chapter 1 marker (after the FORWARD)
    # 57 -> Chapter 2
    # 68 -> Chapter 3
    #131 -> Chapter 4
    #153 -> CHAPTER 5
    #220 -> CHAPTER 6
    #252 -> CHAPTER 7
    #298 -> CHAPTER 8
  Chapter 1 folds in the FORWARD (paras 6-8) and the Basics/Grips
  material that sits before the "Chapter 2" marker.

This script is a sibling of scripts/extract-book.py which handles the
techniques book. The two share a very similar shape; kept separate
because per-book normalisation and chapter maps diverge quickly.
"""

import re
import os
import sys
import shutil
import zipfile
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX_PATH = os.path.join(REPO, "static", "downloads", "PlayersGuideEnglish.docx")
DOCX_CACHE = os.path.join(REPO, ".cache", "players-guide-docx")
DOCX_DIR = DOCX_CACHE

EN_OUT = os.path.join(REPO, "content/en/books/students/carrom-players-guide")
IMG_OUT = os.path.join(REPO, "static/images/book/players-guide")

# Hand-maintained chapters — not overwritten by the extractor.
# (Populate as you edit specific chapters by hand.)
SKIP_REGENERATE: set[str] = set()

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


# -- DOCX unzip + rels ------------------------------------------------------

def ensure_docx_extracted() -> str:
    if not os.path.isfile(DOCX_PATH):
        sys.exit(f"Source not found: {DOCX_PATH}")
    marker = os.path.join(DOCX_CACHE, "word", "document.xml")
    docx_mtime = os.path.getmtime(DOCX_PATH)
    cache_mtime = os.path.getmtime(marker) if os.path.isfile(marker) else 0
    if cache_mtime < docx_mtime:
        if os.path.isdir(DOCX_CACHE):
            shutil.rmtree(DOCX_CACHE)
        os.makedirs(DOCX_CACHE, exist_ok=True)
        with zipfile.ZipFile(DOCX_PATH) as zf:
            zf.extractall(DOCX_CACHE)
        print(f"Extracted {DOCX_PATH}", file=sys.stderr)
    return DOCX_CACHE


def load_rels() -> dict[str, str]:
    """rId -> 'image1.jpeg' style filename"""
    tree = ET.parse(f"{DOCX_DIR}/word/_rels/document.xml.rels")
    root = tree.getroot()
    out = {}
    for rel in root:
        rid = rel.get("Id")
        target = rel.get("Target", "")
        if target.startswith("media/image"):
            out[rid] = target.replace("media/", "")
    return out


def image_filename_to_fig(filename: str) -> str | None:
    """image12.jpeg -> fig-12.jpg (natural sort by number)."""
    m = re.match(r"image(\d+)\.(?:jpe?g|png)", filename, re.IGNORECASE)
    if not m:
        return None
    n = int(m.group(1))
    return f"fig-{n:02d}.jpg"


def copy_images_to_static() -> None:
    """Copy DOCX media/*.jpeg to static/images/book/players-guide/fig-NN.jpg."""
    src_dir = os.path.join(DOCX_DIR, "word", "media")
    if not os.path.isdir(src_dir):
        print(f"No media dir at {src_dir}", file=sys.stderr)
        return
    os.makedirs(IMG_OUT, exist_ok=True)
    count = 0
    for name in sorted(os.listdir(src_dir)):
        fig = image_filename_to_fig(name)
        if not fig:
            continue
        src = os.path.join(src_dir, name)
        dst = os.path.join(IMG_OUT, fig)
        shutil.copyfile(src, dst)
        count += 1
    print(f"Copied {count} images to {IMG_OUT}", file=sys.stderr)


# -- Paragraph walk ---------------------------------------------------------

def walk_paragraphs(rels: dict[str, str]):
    """Yield {idx, style, text, images} for paragraphs with text or images."""
    tree = ET.parse(f"{DOCX_DIR}/word/document.xml")
    root = tree.getroot()
    body = root.find(W + "body")
    idx = 0
    for p in body.iter(W + "p"):
        style = ""
        pStyle_el = p.find(f".//{W}pStyle")
        if pStyle_el is not None:
            style = pStyle_el.get(W + "val", "")
        text = "".join(t.text or "" for t in p.iter(W + "t")).strip()
        image_figs = []
        for blip in p.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"):
            rid = blip.get(R + "embed")
            if rid and rid in rels:
                fig = image_filename_to_fig(rels[rid])
                if fig:
                    image_figs.append(fig)
        if text or image_figs:
            yield {"idx": idx, "style": style, "text": text, "images": image_figs}
            idx += 1


# -- Chapter map ------------------------------------------------------------
# (slug, title, description, last_kept_para_idx_inclusive)
#
# Boundaries derived from an offline scan of the docx (see docstring above).
# The next chapter starts at the paragraph AFTER the previous chapter's end.
CHAPTERS = [
    ("chapter-01", "Chapter 1 — Foreword & Basics",
        "Arun's foreword to the guide, the aim of carrom, and the fundamentals — force, sitting position, footwork, height, and the four grips.",
        56),
    ("chapter-02", "Chapter 2 — Physics, Geometry, Mathematics",
        "Why carrom is a game of physics, geometry, and mathematics — how to think about angles, force, and rebounds.",
        67),
    ("chapter-03", "Chapter 3 — Strokes",
        "The main strokes of carrom, walked through one by one with photos.",
        130),
    ("chapter-04", "Chapter 4 — Behaviour",
        "Behaviour with the umpire, spectators, opponents; the role of luck and punctuality at the table.",
        152),
    ("chapter-05", "Chapter 5 — Concentration, Observation, and the Board",
        "Concentration and observation as skills; the factors of the playing surface — board level, smoothness, frame bounce, pocket behaviour, coin properties.",
        219),
    ("chapter-06", "Chapter 6 — Offence, Defence, and Killer's Instinct",
        "When to play offence and when defence; knowing your strong and weak points; the killer's instinct that closes games.",
        251),
    ("chapter-07", "Chapter 7 — Mental Fitness",
        "Sleep, deep breathing, chanting, and mental practice — training the mind alongside the hand.",
        297),
    ("chapter-08", "Chapter 8 — Emotions, Diet, and Attitude",
        "Handling fear and anxiety, controlling emotions, decision making, diet, and the attitudes that separate winners from losers.",
        99999),  # everything remaining
]


# -- Suppression sets -------------------------------------------------------

# Heading text that should NOT appear in the rendered chapter, because the
# chapter page title covers it OR the docx repeats it as a section artifact.
SUPPRESSED_HEADINGS = {
    "written by",
    "players guide",
    "chapter 1",
    "chapter 2",
    "chapter 3",
    "chapter 4",
    "chapter 5",
    "chapter 6",
    "chapter 7",
    "chapter 8",
}

# Body text lines that should be dropped (title-page artifacts, standalone
# attribution lines that appear without context).
SUPPRESSED_BODY = {
    "shri. arun deshpande",
    "arun deshpande",
    "--author",
    "for practical - visit my youtube channel \"arun deshpande carrom\".       please subscribe the channel",
    "for practical - visit my youtube channel \"arun deshpande carrom\". please subscribe the channel",
    # Chapter marker paragraphs sometimes arrive with style="" (default),
    # so the heading suppression above doesn't catch them.
    "chapter 1", "chapter 2", "chapter 3", "chapter 4",
    "chapter 5", "chapter 6", "chapter 7", "chapter 8",
}


# -- Text normalisation -----------------------------------------------------

def normalise_text(t: str) -> str:
    if not t:
        return t
    # Smart quotes -> straight (mirrors extract-book.py)
    t = t.replace("“", '"').replace("”", '"')
    t = t.replace("‘", "'").replace("’", "'")
    # Stray control chars
    t = t.replace("�", "")
    t = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", t)
    # Common typo fixes seen in Arun's typing (kept conservative)
    t = re.sub(r"\bCANON\b", "Cannon", t)
    t = re.sub(r"\bcanon\b", "cannon", t)
    t = t.replace("SIeep", "Sleep")  # capital-I typo for lower-l
    # Double spaces to single
    t = re.sub(r" {2,}", " ", t)
    return t.strip()


def heading_level(style: str) -> int | None:
    if style == "Title":
        return 1
    if style == "Heading1":
        return 2
    if style == "Heading2":
        return 3
    return None


def title_case_for_heading(s: str) -> str:
    s = s.rstrip(":").rstrip("–").rstrip("-").strip()
    if s.isupper():
        small = {"OR", "AND", "OF", "FROM", "THE", "TO", "A", "FOR", "IN", "ON", "WITH"}
        out = []
        for w in s.split():
            out.append(w.lower() if w in small else w.capitalize())
        if out:
            out[0] = out[0].capitalize()
        s = " ".join(out)
    return s


def is_suppressed_heading(text: str) -> bool:
    key = text.lower().rstrip(":–- ").strip()
    return key in SUPPRESSED_HEADINGS


def is_suppressed_body(text: str) -> bool:
    key = text.lower().rstrip(".:–- ").strip()
    return key in SUPPRESSED_BODY


def is_stray_label(text: str) -> bool:
    t = text.strip().rstrip(".").lower()
    if t in ("arun deshpande", "shri. arun deshpande"):
        return True
    if re.match(r"^fig\.?\s*\d+$", t):
        return True
    return False


# -- Emit -------------------------------------------------------------------

def render_chapter(chap: tuple, paras: list[dict]) -> str:
    _slug, _title, _desc, _ = chap
    lines: list[str] = []
    fig_count = 0
    for p in paras:
        lvl = heading_level(p["style"])
        if lvl is not None and p["text"]:
            if is_suppressed_heading(p["text"]):
                continue
            text = title_case_for_heading(p["text"])
            lines.append(f"\n## {text}\n")
            continue
        text = normalise_text(p["text"])
        if text and (is_stray_label(text) or is_suppressed_body(text)):
            text = ""
        for fig in p["images"]:
            fig_count += 1
            alt = f"Figure {fig_count}"
            lines.append(f"\n![{alt}](/images/book/players-guide/{fig})\n")
        if text:
            lines.append(text + "\n")
    body = "\n".join(lines)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip() + "\n"


def write_chapter_file(chap: tuple, weight: int, paras: list[dict]):
    slug, title, desc, _ = chap
    body = render_chapter(chap, paras)

    # Cover: first image found in the chapter
    cover = ""
    for p in paras:
        if p["images"]:
            cover = p["images"][0]
            break
    cover_block = ""
    if cover:
        alt = title.split("—", 1)[-1].strip() if "—" in title else title
        cover_block = (
            "cover:\n"
            f"  image: \"/images/book/players-guide/{cover}\"\n"
            f"  alt: \"{alt}\"\n"
        )

    frontmatter = (
        "---\n"
        f'title: "{title}"\n'
        f'description: "{desc}"\n'
        f"weight: {weight}\n"
        "date: 2026-08-03\n"
        'author: "Arun Deshpande"\n'
        f"{cover_block}"
        "---\n\n"
    )

    lead = f"*{desc}*\n\n"

    os.makedirs(EN_OUT, exist_ok=True)
    out_path = os.path.join(EN_OUT, f"{slug}.md")
    if os.path.basename(out_path) in SKIP_REGENERATE:
        return None, 0, 0
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(frontmatter + lead + body)
    return out_path, len(paras), len(body.split())


# -- Main -------------------------------------------------------------------

def main() -> None:
    global DOCX_DIR
    DOCX_DIR = ensure_docx_extracted()
    copy_images_to_static()

    rels = load_rels()
    all_paras = list(walk_paragraphs(rels))
    print(f"Parsed {len(all_paras)} kept-idx paragraphs.", file=sys.stderr)

    # Distribute paragraphs to chapters by index range.
    # Chapter 1 starts at idx 6 (skips title-page paras 0-5).
    by_chapter = []
    prev_end = 5  # after the title page
    for chap in CHAPTERS:
        _, _, _, end = chap
        chunk = [p for p in all_paras if prev_end < p["idx"] <= end]
        by_chapter.append((chap, chunk))
        prev_end = end

    print(f"\n{'#':3} {'Slug':<14} {'Paras':>6} {'Words':>6}  Title")
    print("-" * 90)
    for i, (chap, paras) in enumerate(by_chapter, start=1):
        if not paras:
            print(f"{i:3} {chap[0]:<14}      0 (skipped, empty range)")
            continue
        result = write_chapter_file(chap, i, paras)
        if result[0] is None:
            print(f"{i:3} {chap[0]:<14}      — (skipped, hand-maintained)")
            continue
        _, n, wc = result
        print(f"{i:3} {chap[0]:<14} {n:>6} {wc:>6}  {chap[1]}")


if __name__ == "__main__":
    main()
