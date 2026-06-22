#!/usr/bin/env python3
"""
Post-process Carrom Techniques chapters: join docx line-breaks and add
definition-card stubs for ## headings that lack them.

Hand-polished chapters (definition cards written manually) are skipped.
"""

import re
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK_DIR = os.path.join(
    REPO, "content/en/books/students/carrom-techniques-and-skills"
)

SKIP_CARDS = {"chapter-01.md", "chapter-02.md", "chapter-03.md", "chapter-04.md", "chapter-05.md"}

# One-line definitions for stroke / section headings (auto card when missing)
DEFS = {
    "Shower of Strokes": "An overview of the fundamental strokes covered in this chapter.",
    "Cut": "Pocketing a coin with the striker on a cross line from the coin.",
    "Straight Cut": "Pocketing a coin with the striker in a straight line with the coin.",
    "Cross Cut or Minus Cut": "Pocketing a coin with the striker on a cross (minus) line when a straight cut is impossible.",
    "Double": "Pocketing a coin in the base pocket by hitting it off the opposite frame.",
    "Cross Double": "A double played from a cross line — the coin crosses the striker's path.",
    "Press": "Pocketing the nearer of two touching coins in a straight line parallel to the side frame.",
    "Touch": "Pocketing your coin by touching it to another coin.",
    "Shot": "Pocketing the front coin of two touching coins by hitting the coin behind.",
    "Pair": "Two coins with a gap between them — the reverse principle of a shot applies.",
    "Canon": "A pair with considerable distance between the coins; requires great accuracy.",
    "Cannon": "A pair with considerable distance between the coins; requires great accuracy.",
    "Glance": "Pocket the second coin while the first coin hits the opposite frame and comes near the base frame.",
    "Double Glance": "Glancing two coins one after the other when one glance cannot reach the target.",
    "Brush": "Like a glance, but the first coin goes to the opposite or side frame instead of the base frame.",
    "Rebound": "Pocketing a coin near the left or right frame by hitting the opposite frame.",
    "Simple Rebound": "A coin near the left frame pocketed by hitting the striker on the opposite frame.",
    "Langda Rebound or Off the Side Rebound": "Pocketing by hitting the opposite and side frame.",
    "Hook": "Pocketing by rebound except off the left or right frame side.",
    "Third Pocket": "Pocketing to the opposite right pocket by hitting the side frame.",
    "Cross Third Pocket": "Third pocket played from a cross line with deflection off the opposite frame.",
    "Turning": "Pocketing your coin by hitting through an opponent's coin blocking the path.",
    "Second": "Pocketing to the opposite pocket by hitting the base frame when the opponent blocks the pocket.",
    "Cross Second": "Second pocket played from the base circle with a cross hit on the blocking coin.",
    "Slip": "Pocketing a coin touching a frame by hitting its quarter point.",
    "The Striker Slip": "Striker slips from one coin to strike and pocket another nearby.",
    "Double Touch": "Striker touches the coin twice before pocketing — used near side frames.",
    "Bomb (bum)": "Hard stroke against the frame to disturb the board and drag coins toward you.",
    "Force": "Powerful stroke using the principle of equal force — often to pocket the Queen through blockers.",
    "Direct Defence": "Making the opponent's coin difficult without touching your own coin.",
    "Indirect Defence": "Defence through strokes such as glance and brush.",
    "Offense": "Aggressive play to pocket coins and finish boards — essential alongside defence.",
    "Wrong Defence and Its Result": "A lesson from a critical match — choosing the wrong defensive move.",
    "Experience In Madras": "How partner understanding won a national doubles semi-final.",
    "Concentration": "Fix your eye on the board and the exact point of contact on the coin.",
    "Observation": "Watch opponents and conditions — powder, grip, weak sides — to exploit them.",
    "Never Have Over Confience": "Over-confidence after a lead is a common cause of defeat.",
    "Stability or Patience": "Never accept defeat until the last coin is actually pocketed.",
    "Never Underestimate the Opponents": "Every opponent can punish careless play.",
    "An Open Mind": "Keep learning from others' strokes and combinations.",
    "Practice": "Practice with players of equal or higher standard — not only weaker opponents.",
}


def join_blocks(body: str) -> str:
    """Join lines within a block; merge fragment blocks split by blank lines."""
    blocks = re.split(r"\n\n+", body.strip())
    merged: list[str] = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if (
            block.startswith("#")
            or block.startswith("!")
            or block.startswith("<")
            or block.startswith("—")
            or re.match(r"^\*\*.+\*\*$", block)
            or re.match(r"^\d+\)", block)
        ):
            cleaned = block
        else:
            lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
            cleaned = " ".join(lines) if lines else block
        if (
            merged
            and not merged[-1].startswith("#")
            and not merged[-1].startswith("!")
            and not merged[-1].startswith("<")
            and not re.match(r"^\d+\)", merged[-1])
            and not merged[-1].rstrip().endswith((".", "!", "?", ":", '"', ")", "]", "'"))
            and cleaned
            and not cleaned.startswith("#")
            and not cleaned.startswith("!")
            and not cleaned.startswith("<")
            and (cleaned[0].islower() or merged[-1].endswith((",", " For", " In", " At", " The", " A", " An")))
        ):
            merged[-1] = merged[-1].rstrip() + " " + cleaned.lstrip()
        else:
            merged.append(cleaned)
    return "\n\n".join(merged)


def join_broken_paragraphs(body: str) -> str:
    body = join_blocks(body)
    return body


def add_definition_cards(body: str) -> str:
    parts = re.split(r"(^## .+$)", body, flags=re.MULTILINE)
    if len(parts) < 3:
        return body
    result = [parts[0]]
    for i in range(1, len(parts), 2):
        heading = parts[i]
        content = parts[i + 1] if i + 1 < len(parts) else ""
        result.append(heading)
        title = heading.replace("## ", "").strip()
        if 'class="definition-grid"' in content[:400]:
            result.append(content)
            continue
        defn = DEFS.get(title)
        if defn:
            card = (
                f"\n\n<div class=\"definition-grid\">\n"
                f"  <div class=\"definition-card\">\n"
                f"    <span class=\"term\">{title}</span>\n"
                f"    <p class=\"def\">{defn}</p>\n"
                f"  </div>\n"
                f"</div>\n"
            )
            result.append(card + content)
        else:
            result.append(content)
    return "".join(result)


IMAGE_BLOCK_RE = re.compile(r"^!\[[^\]]*\]\([^)]+\)\s*$", re.MULTILINE)


def reorder_images_first(body: str) -> str:
    """Place every section image before its definition card and prose."""
    parts = re.split(r"(^## .+$)", body, flags=re.MULTILINE)
    if len(parts) < 2:
        return body

    out = [parts[0].strip()]
    if out[0]:
        out[0] += "\n\n"

    for i in range(1, len(parts), 2):
        heading = parts[i]
        content = parts[i + 1] if i + 1 < len(parts) else ""
        images = IMAGE_BLOCK_RE.findall(content)
        rest = IMAGE_BLOCK_RE.sub("", content)
        rest = re.sub(r"\n{3,}", "\n\n", rest).strip()

        section = heading
        for img in images:
            section += f"\n\n{img}"
        if rest:
            section += "\n\n" + rest
        out.append(section)

    return "\n\n".join(s for s in out if s.strip()) + "\n"


def strip_garbage(text: str) -> str:
    """Remove replacement chars and non-text lines from docx extraction glitches."""
    text = text.replace("\ufffd", "")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    lines: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            lines.append(line)
            continue
        if re.fullmatch(r"[\?\uFFFD]{4,}", s):
            continue
        printable = sum(
            1 for c in s if c.isalnum() or c.isspace() or c in ".,;:!?\"'()[]—–-/%"
        )
        if len(s) >= 12 and printable / len(s) < 0.45:
            continue
        lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def fix_typos(text: str) -> str:
    text = text.replace("Canon", "Cannon")
    text = text.replace("SriLanka", "Sri Lanka")
    text = text.replace("Over Confience", "Over-Confidence")
    text = text.replace("lndirect", "Indirect")
    text = text.replace("Marry people", "Many people")
    text = text.replace("Shivalingam", "Shivlingam")
    text = text.replace("  .", ".")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def process(path: str, name: str) -> None:
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    if not raw.startswith("---"):
        return
    end = raw.index("---", 3) + 3
    fm, body = raw[:end], raw[end:].lstrip("\n")
    body = join_broken_paragraphs(body)
    if name not in SKIP_CARDS:
        body = add_definition_cards(body)
    body = reorder_images_first(body)
    body = strip_garbage(body)
    body = fix_typos(body)
    with open(path, "w", encoding="utf-8") as f:
        f.write(fm + "\n\n" + body.strip() + "\n")


def main():
    for name in sorted(os.listdir(BOOK_DIR)):
        if not name.startswith("chapter-") or not name.endswith(".md"):
            continue
        path = os.path.join(BOOK_DIR, name)
        process(path, name)
        tag = "cards+reorder" if name not in SKIP_CARDS else "reorder"
        print(f"done  {name} ({tag})")


if __name__ == "__main__":
    main()
