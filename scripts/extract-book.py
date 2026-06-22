#!/usr/bin/env python3
"""
Extract Carrom Techniques and Skills (.docx) into Hugo markdown chapters.

Reads:
  static/downloads/CarromTechniqandSkills.docx
  (unzipped on demand to .cache/docx-extract/)
Writes:
  content/en/books/students/carrom-techniques-and-skills/chapter-NN.md
    (the _index.md is hand-maintained and not regenerated)

Image handling:
  - 52 images were already copied to static/images/book/fig-NN.jpg (resized).
  - The docx names them image1.png..image52.png; our fig-NN matches the natural sort
    of those names (image1.png -> fig-01, image2.png -> fig-02, ...).
  - In the docx XML, an inline image references an rId; we resolve rId -> "image<N>.png"
    via word/_rels/document.xml.rels, then map to fig-<NN>.jpg.

Chapter mapping (locked in plan-translation.md):
  Each chapter consumes a paragraph index range from the docx.
"""

import re
import os
import sys
import shutil
import zipfile
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX_PATH = os.path.join(REPO, "static", "downloads", "CarromTechniqandSkills.docx")
DOCX_CACHE = os.path.join(REPO, ".cache", "docx-extract")
DOCX_DIR = DOCX_CACHE  # set by ensure_docx_extracted() before parsing
# Hand-maintained chapters — not overwritten by the extractor.
SKIP_REGENERATE = {"chapter-01.md"}

EN_OUT = os.path.join(REPO, "content/en/books/students/carrom-techniques-and-skills")

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PIC_NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def ensure_docx_extracted() -> str:
    """Unzip the source docx into .cache when missing or stale."""
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


def load_rels():
    """rId -> 'image1.png' style filename"""
    tree = ET.parse(f"{DOCX_DIR}/word/_rels/document.xml.rels")
    root = tree.getroot()
    out = {}
    for rel in root:
        rid = rel.get("Id")
        target = rel.get("Target", "")
        if target.startswith("media/image"):
            out[rid] = target.replace("media/", "")
    return out


def image_filename_to_fig(filename):
    """image12.png -> fig-12.jpg (since our resized files are JPEGs)"""
    m = re.match(r"image(\d+)\.png", filename)
    if not m:
        return None
    n = int(m.group(1))
    return f"fig-{n:02d}.jpg"


def walk_paragraphs(rels):
    """
    Yield dicts for every paragraph in document order:
      {idx, style, text, image_figs: ["fig-12.jpg", ...]}
    style: '' / 'Heading1' / 'Heading2' / 'Title' / 'BodyText' / etc.
    """
    tree = ET.parse(f"{DOCX_DIR}/word/document.xml")
    root = tree.getroot()
    body = root.find(W + "body")
    idx = 0
    for p in body.iter(W + "p"):
        # Style
        style = ""
        pStyle_el = p.find(f".//{W}pStyle")
        if pStyle_el is not None:
            style = pStyle_el.get(W + "val", "")
        # Text
        text = "".join(t.text or "" for t in p.iter(W + "t")).strip()
        # Images (look for a:blip elements within w:drawing)
        image_figs = []
        for blip in p.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"):
            rid = blip.get(R + "embed")
            if rid and rid in rels:
                fig = image_filename_to_fig(rels[rid])
                if fig:
                    image_figs.append(fig)
        # Legacy w:pict (older Word) also has imagedata, but the docx uses w:drawing
        if text or image_figs:
            yield {
                "idx": idx,
                "style": style,
                "text": text,
                "images": image_figs,
            }
            idx += 1


# -- chapter map: (slug, title, description, last_para_idx_inclusive) ----------
#
# Boundaries are paragraph indices from `walk_paragraphs` (i.e., post-filter).
# Cross-checked against /tmp/book-structure.txt that we computed earlier.
CHAPTERS = [
    # (slug, title, description, last_para_idx_inclusive)
    # Boundaries are locked from the heading scan; the next chapter starts at
    # the heading paragraph that follows.
    ("chapter-01", "Chapter 1 — The Mantra",
        "Arun Deshpande's note to the reader — the spirit in which to approach carrom, and why your relationship with the game matters more than any single match.",
        15),
    ("chapter-02", "Chapter 2 — Equipment",
        "Every part of the carrom set — board, frames, pockets, base lines, circles, coins, striker, stand, lamp.",
        31),
    ("chapter-03", "Chapter 3 — Basic Rules",
        "How a game is set up and scored, the rules around the Queen, fouls, and Dues.",
        44),
    ("chapter-04", "Chapter 4 — Grips",
        "Natural grip, scissor grip, locking grip, middle finger flat grip — when and how to use each one.",
        61),
    ("chapter-05", "Chapter 5 — The Break",
        "Breaking from the left base circle, breaking from near the base circle — the opening shot of every board.",
        69),
    ("chapter-06", "Chapter 6 — Strokes: Cut, Double, Press",
        "Shower of Strokes, Straight Cut, Cross Cut, Double, Cross Double, and the Press.",
        89),
    ("chapter-07", "Chapter 7 — Touch, Shot, Pair, Cannon",
        "Touch and its variations, Shot, Pair, and Cannon — strokes that set up multiple coins at once.",
        106),
    ("chapter-08", "Chapter 8 — Glance, Brush, Rebound, Hook",
        "Glance, Double Glance, Brush, Rebound, Simple Rebound, Langda Rebound, and Hook.",
        135),
    ("chapter-09", "Chapter 9 — Pockets and Turning",
        "Third Pocket, Cross Third Pocket, Turning, Second Pocket, and Cross Second Pocket.",
        158),
    ("chapter-10", "Chapter 10 — Slip, Striker Slip, Double Touch",
        "Slip, Striker Slip, and Double Touch — fine-control strokes used when coins overlap.",
        169),
    ("chapter-11", "Chapter 11 — Bomb and Force",
        "The Bomb (Bum) and Force strokes — powerful shots used to break up clusters and reset the board.",
        191),
    ("chapter-12", "Chapter 12 — Defence and Offence",
        "Direct and Indirect Defence, offence, and lessons from Arun's experience in Madras.",
        228),
    ("chapter-13", "Chapter 13 — Mental Qualities of a Player",
        "Concentration, Observation, the danger of over-confidence, Stability/Patience, Open Mind, and Practice.",
        279),
    ("chapter-14", "Chapter 14 — Advanced Stroke Positions",
        "Walkthroughs of advanced board positions — figures 32 through 47 — and how Arun plays them.",
        9999),  # paragraph 280 onwards (everything to end)
]


# Headings (and stray content) that should NOT be emitted into the rendered
# chapter, because the chapter page already has a title.
# Match against the docx text (case-insensitive, trimmed of trailing punctuation).
SUPPRESSED_HEADINGS = {
    "written by",
    "mantra",
    "what exactly is \"carrom\" grip",
    "the progress of carrom",
    "index",
    "sitting position shower of strokes defence and offence qualities of the players advanced strokes",
    "chapter 5",
    "chapter-5",
    "chapter-6",
    "chapter-7",
    "advanced strokes",
    # The Title style on the cover page renders the book's own title; the
    # chapter page already shows a title, so drop it.
    "carrom techniques and skills",
}

# Body-text paragraphs that should also be suppressed (title-page artifacts,
# bare TOC fragments, attribution lines that appear without context).
SUPPRESSED_BODY = {
    "shri. arun deshpande",
    "--author",
    "arun deshpande",
    "index",
    "sitting position shower of strokes defence and offence qualities of the players advanced strokes",
    "what exactly is \"carrom\"",
    "what exactly is carrom",
}


# -- text normalisation -----------------------------------------------------

def normalise_text(t):
    """Clean up OCR-style quirks in the docx text."""
    if not t:
        return t
    # Smart quotes -> straight
    t = t.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    # Glossary corrections
    t = re.sub(r"\bCANON\b", "Cannon", t)
    t = re.sub(r"\bcanon\b", "cannon", t)
    # Common typo fixes from the docx (kept conservative — only fix obvious typos)
    t = t.replace("CONFIENCE", "CONFIDENCE")
    t = t.replace("Excercizes", "Exercises")
    t = t.replace("coinsare", "coins are")
    t = t.replace("infig.", "in fig.")
    t = t.replace("DeshpandeFIG.", "Deshpande FIG.")
    t = re.sub(r"\bprayed\b", "played", t)  # "can be prayed after practice"
    # Stray double spaces
    t = re.sub(r" {2,}", " ", t)
    # Normalise "Fig." / "fig." spacing
    t = re.sub(r"\bfig\.\s*(\d+)", lambda m: f"Fig. {m.group(1)}", t, flags=re.IGNORECASE)
    t = t.replace("\ufffd", "")
    t = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", t)
    return t.strip()


def heading_level(style):
    if style == "Title":
        return 1
    if style == "Heading1":
        return 2
    if style == "Heading2":
        return 3
    return None


# -- markdown emission ------------------------------------------------------

def title_case_for_heading(s):
    """The docx headings are ALL CAPS for many entries — soften them.
    Keep acronyms and stroke names recognisable.
    """
    s = s.rstrip(":").rstrip("–").rstrip("-").strip()
    # Detect ALL CAPS
    if s.isupper():
        # Title-case it, but preserve common carrom abbreviations
        words = s.split()
        out = []
        for w in words:
            if w in {"OR", "AND", "OF", "FROM", "THE", "TO", "A", "FOR"}:
                out.append(w.lower())
            else:
                out.append(w.capitalize())
        if out:
            out[0] = out[0].capitalize()
        s = " ".join(out)
    return s


def is_suppressed_heading(text):
    return text.lower().rstrip(":–- ").strip() in SUPPRESSED_HEADINGS


def is_suppressed_body(text):
    return text.lower().rstrip(".:–- ").strip() in SUPPRESSED_BODY


def render_chapter(chap, paras):
    """Emit a chapter's markdown body (no frontmatter)."""
    slug, title, desc, _ = chap
    lines = []
    fig_count = 0
    for p in paras:
        # Heading?
        lvl = heading_level(p["style"])
        if lvl is not None and p["text"]:
            # Drop noise headings that conflict with the chapter title
            if is_suppressed_heading(p["text"]):
                continue
            text = title_case_for_heading(p["text"])
            # All chapter-internal headings render as ##
            # (the H1 is rendered by the layout from frontmatter title)
            lines.append(f"\n## {text}\n")
            continue
        # Body paragraph
        text = normalise_text(p["text"])
        # Skip stray bare labels like "Arun Deshpande" / "Fig. 37" that appear
        # by themselves in the docx after page breaks, or title-page artifacts.
        if text and (is_stray_label(text) or is_suppressed_body(text)):
            text = ""
        # Image before description (book layout)
        for fig in p["images"]:
            fig_count += 1
            alt = f"Figure {fig_count}"
            m = re.search(r"fig\.?\s*(\d+)", p["text"], re.IGNORECASE)
            if m:
                alt = f"Figure {m.group(1)}"
            lines.append(f"\n![{alt}](/images/book/{fig})\n")
        if text:
            lines.append(text + "\n")
    body = "\n".join(lines)
    # Collapse 3+ blank lines to 2
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip() + "\n"


def is_stray_label(text):
    """True if the paragraph is a stray label like 'FIG. 37' or 'Arun Deshpande' alone.
    These appear in the docx as artefacts of the original page layout.
    """
    t = text.strip().rstrip(".").lower()
    if t in ("arun deshpande", "fig. 37", "fig 37"):
        return True
    if re.match(r"^fig\.?\s*\d+$", t):
        return True
    return False


def write_chapter_file(chap, weight, paras):
    slug, title, desc, _ = chap
    body = render_chapter(chap, paras)

    # Cover image: use the first image in the chapter if any
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
            f"  image: \"/images/book/{cover}\"\n"
            f"  alt: \"{alt}\"\n"
        )

    aliases_block = (
        "aliases:\n"
        f"  - /read/{slug}/\n"
        f"  - /en/read/{slug}/\n"
    )

    frontmatter = (
        "---\n"
        f"title: \"{title}\"\n"
        f"description: \"{desc}\"\n"
        f"weight: {weight}\n"
        "date: 2026-01-01\n"
        "author: \"Arun Deshpande\"\n"
        f"{cover_block}"
        f"{aliases_block}"
        "---\n\n"
    )

    # Italic lead intro — mirrors the Rules chapters' style. Uses the
    # chapter description as the in-page lead so the page reads naturally
    # below the chapter title rendered by the layout.
    lead = f"*{desc}*\n\n"

    out_path = os.path.join(EN_OUT, f"{slug}.md")
    if os.path.basename(out_path) in SKIP_REGENERATE:
        return None, 0, 0
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(frontmatter + lead + body)
    return out_path, len(paras), len(body.split())


def main():
    global DOCX_DIR
    DOCX_DIR = ensure_docx_extracted()
    rels = load_rels()
    all_paras = list(walk_paragraphs(rels))
    print(f"Parsed {len(all_paras)} paragraphs.", file=sys.stderr)

    # Distribute paragraphs to chapters by index range
    by_chapter = []
    prev_end = -1
    for chap in CHAPTERS:
        slug, title, desc, end = chap
        chunk = [p for p in all_paras if prev_end < p["idx"] <= end]
        by_chapter.append((chap, chunk))
        prev_end = end

    # Write
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
        path, n, wc = result
        print(f"{i:3} {chap[0]:<14} {n:>6} {wc:>6}  {chap[1]}")


if __name__ == "__main__":
    main()
