# Plan: Publish books in EN, then translate

Original scope: *Carrom Techniques and Skills* (Arun Deshpande) — English first, German second with federation review.

**Current scope:** both site books in **8 languages** — EN, DA, DE, MR, IT, FR, SI, HI. AI first drafts are done for all languages; human federation review is still pending for non-English.

| Book | EN source | Chapters | Images |
|---|---|---|---|
| **Carrom Techniques and Skills** | `static/downloads/CarromTechniqandSkills.docx` | 14 | 52 (`static/images/book/fig-NN.jpg`) |
| **Official Carrom Rules & Regulations** | ICF PDF + wikiHow callouts | 8 | cover only |

Techniques book stats (from .docx parse):

| Property | Value |
|---|---|
| Word count | ~16,830 words |
| Paragraphs | 270 |
| Embedded images | 52 |
| Native structure | Heading1 / Heading2 styles |

---

## Status at a glance

| Phase | What | Status |
|---|---|---|
| **0** | Extract .docx → images + chapter mapping | **Done** — `scripts/extract-book.py`, images at `static/images/book/fig-NN.jpg` |
| **1** | English chapter pages live on site | **Done** — `content/en/books/…`, Hugo builds clean |
| **2** | Glossary locked in README | **Done** (DE-focused; federation may still adjust) |
| **3** | AI translation drafts | **Done** — all 8 langs × both books via `scripts/translate-books.py` |
| **4** | Federation / native-speaker review | **Pending** — every non-EN chapter still has AI-draft `translatedBy` |
| **5** | PDFs per language | **Partial** — EN PDFs only; other langs auto-disable download until file exists |
| **6** | Arun sign-off on EN techniques book | **Pending** — editorial review before treating EN as final |

---

## Workflow rules (locked)

1. **English first.** No translation work starts until the English source chapter is finalised.
2. **Glossary before human translation.** For German, agree carrom terms with the Deutscher Carrom Verband (DCV) before federation review. Extend the same principle to other languages where a national federation exists.
3. **AI first draft, human review second.** `scripts/translate-books.py` generates drafts. Reviewer's name replaces the generic `translatedBy` after sign-off.
4. **Images shared across languages.** All figures live at `static/images/book/` and are referenced identically from every language (`/images/book/fig-NN.jpg`).
5. **One chapter per commit** during federation review — keeps git history traceable.
6. **EN edit triggers a revisit.** Any material change to a published English chapter must be mirrored to every enabled translation (and re-reviewed if substantive).

---

## Content paths

Books live under Hugo's `books` section (not the retired `/read` or `/book` URL trees):

```
content/{lang}/books/
├── students/carrom-techniques-and-skills/
│   ├── _index.md
│   └── chapter-01.md … chapter-14.md
└── rules/official-carrom-rules/
    ├── _index.md
    └── chapter-01.md … chapter-08.md
```

Catalog metadata (titles, descriptions, PDF paths, per-lang enable flags): `data/books.yaml`.

Site layouts: `layouts/books/{list,single,category}.html`.

---

## Tooling

| Script | Purpose |
|---|---|
| `scripts/generate-book-pdfs.py` | Translate `CarromTechniqandSkills.docx` to all 8 languages and export `static/downloads/carrom-techniques-and-skills-{lang}.pdf` (requires LibreOffice) |
| `scripts/generate-rules-pdfs.py` | Export `content/{lang}/books/rules/official-carrom-rules/` markdown to `static/downloads/carrom-official-rules-{lang}.pdf` |
| `scripts/translate-books.py` | Translate both books EN → `da` / `de` / `mr` / `it` / `fr` / `si` / `hi`. Preserves HTML, image paths, URLs, and carrom terms. Use `--force` to overwrite. |
| `scripts/setup-language.py` | Scaffold i18n, about bio, and non-book pages for a new language |
| `scripts/beautify-techniques-book.py` | One-off HTML/markdown cleanup pass on techniques chapters |

Translation deps: `python3 -m venv .venv && pip install deep-translator pyyaml`

---

## Phase 0 — Extract & restructure ✅ Done

Goal: get the .docx contents into a Hugo-friendly form **without translating**.

- **0.1** ✅ Extract 52 images → `static/images/book/fig-01.jpg` … `fig-52.jpg` (resized JPEGs; original docx names `image1.png` … `image52.png`).
- **0.2** ✅ Parse docx XML paragraph-by-paragraph (styles, text, image anchors) inside `extract-book.py`.
- **0.3** ✅ Chapter mapping locked:

| # | Slug | Title (as published) | ~Words | ~Images |
|---|---|---|---|---|
| 1 | `chapter-01` | The Mantra | 112 | 6 |
| 2 | `chapter-02` | Equipment | 277 | 1 |
| 3 | `chapter-03` | Basic Rules | 363 | 0 |
| 4 | `chapter-04` | Grips | 511 | 9 |
| 5 | `chapter-05` | The Break | 299 | 5 |
| 6 | `chapter-06` | Strokes: Cut, Double, Press | 1,158 | 9 |
| 7 | `chapter-07` | Touch, Shot, Pair, Cannon | 1,231 | 7 |
| 8 | `chapter-08` | Glance, Brush, Rebound, Hook | 1,147 | 6 |
| 9 | `chapter-09` | Pockets and Turning | 985 | 8 |
| 10 | `chapter-10` | Slip, Striker Slip, Double Touch | 413 | 3 |
| 11 | `chapter-11` | Bomb and Force | 1,060 | 17 |
| 12 | `chapter-12` | Defence and Offence | 3,602 | 12 |
| 13 | `chapter-13` | Mental Qualities of a Player | 3,802 | 9 |
| 14 | `chapter-14` | Advanced Stroke Positions | 1,798 | 32 |
| | | **TOTAL** | **~16,758** | **52** |

Note: chapter 1 title changed from the original docx heading ("Introduction: What is Carrom") to **The Mantra** during editorial pass — Arun's preface letter.

---

## Phase 1 — English chapter pages ✅ Done

Goal: every chapter renders cleanly with images at `content/en/books/students/carrom-techniques-and-skills/<slug>.md`.

- **1.1** ✅ Markdown generated from docx with frontmatter (`title`, `weight`, `cover`, `date`, `author`) and inline figures.
- **1.2** ✅ Light editorial pass — punctuation, "Cannon" spelling (not "Canon"), callout HTML preserved.
- **1.3** ✅ `_index.md` updated; book registered in `data/books.yaml`.
- **1.4** ✅ `layouts/books/single.html` — cover images, prev/next chapter nav.
- **1.5** ✅ `hugo --minify` builds cleanly; legacy `/read` and `/book` URL aliases removed.
- **1.6** ⏳ **Arun sign-off on English** — treat as stop point before calling EN "final".

**Second book (rules):** EN rules book also complete at `content/en/books/rules/official-carrom-rules/` — 8 chapters adapted from ICF PDF with beginner callouts.

---

## Phase 2 — Glossary lock ✅ Done (DE seed; federation may refine)

Goal: every carrom-specific term has an agreed translation **before** human review begins.

- **2.1** ✅ Glossary proposed and expanded — see **Carrom glossary** section in `README.md` (equipment, match structure, strokes, strategy, organisations). Cross-checked against IAKC rules PDF and DCV terminology.
- **2.2** ✅ Locked in README as source of truth.

**Seed glossary (original DE proposal — DCV may override during Phase 4):**

| English | Proposed German |
|---|---|
| Striker | Schläger |
| Queen | Königin |
| Coin / piece | Spielstein |
| Carrom board | Carromboard |
| Baseline | Grundlinie |
| Base circle | Grundkreis |
| Pocket | Tasche / Loch |
| Break | Eröffnung |
| Grip (general) | Griff |
| Natural grip | Natürlicher Griff |
| Scissor grip | Scherengriff |
| Locking grip | Sperrgriff |
| Middle finger flat grip | Mittelfinger-Flachgriff |
| Thumb shot | Daumentechnik |
| Straight cut | Gerader Cut |
| Cross cut / minus cut | Cross Cut / Minus Cut |
| Double | Doublé |
| Cross double | Cross Doublé |
| Press | Press |
| Touch | Touch |
| Pair | Pair |
| Cannon | Cannon |
| Glance | Glance |
| Brush | Brush |
| Rebound | Rebound |
| Langda rebound | Langda Rebound |
| Hook | Hook |
| Third pocket | Drittes Pocket |
| Turning | Drehung |
| Slip | Slip |
| Striker slip | Striker Slip |
| Double touch | Double Touch |
| Bomb (Bum) | Bomb |
| Force | Force |
| Direct defence | Direkte Verteidigung |
| Indirect defence | Indirekte Verteidigung |
| Offence | Angriff |
| Concentration | Konzentration |
| Observation | Beobachtung |
| Patience | Geduld |
| Practice | Übung |

International stroke names stay in English at the table — they're what German players use in practice. DCV adjusts during review.

**Stop point for new languages:** agree terms with the relevant federation before Phase 4 review begins.

---

## Phase 3 — Translation first drafts ✅ Done (all 8 languages)

Goal: every EN chapter has a translation draft in each enabled language.

- **3.1** ✅ `content/{lang}/books/students/carrom-techniques-and-skills/<slug>.md` for DA, DE, MR, IT, FR, SI, HI — same structure, translated frontmatter, shared image paths.
- **3.2** ✅ Glossary terms and `KEEP_TERMS` list honoured by `translate-books.py`; unknown terms stay English.
- **3.3** ✅ Each chapter has AI-draft `translatedBy` (e.g. DE: `"Aus dem Englischen übersetzt (KI-Entwurf)."`).
- **3.4** ✅ Same for rules book — 8 chapters × 8 languages.
- **3.5** ✅ All langs enabled in `data/books.yaml`; site shell (menus, i18n, about) via `setup-language.py`.

**Stop point:** drafts are live on site for reading; treat as **draft** until Phase 4 review.

To regenerate a language after EN changes:

```bash
source .venv/bin/activate
python3 scripts/translate-books.py de --force
```

---

## Phase 4 — Federation / native-speaker review ⏳ Pending

Goal: every non-English chapter is reviewed by a qualified reviewer; corrections applied.

Priority order (original plan):

1. **German (DE)** — Deutscher Carrom Verband review of techniques + rules books.
2. **Other languages** — engage national federations or trusted native speakers as available.

Per chapter:

- **4.1** Reviewer reads chapter, sends annotated changes (PDF / Word / GitHub PR).
- **4.2** Apply corrections. **One chapter per commit**, e.g. `de: review chapter-06 — strokes`. Replace generic `translatedBy` with named reviewer.
- **4.3** If a glossary term was wrong, update README glossary first, then grep all chapters in that language and fix site-wide before moving on.

**Stop point:** all reviewed chapters live with named `translatedBy`. DE was the original "done" milestone; extend to each language as reviewers become available.

---

## Phase 5 — PDFs per language ⏳ Partial

Goal: downloadable PDF for each book in each enabled language.

| File | EN | DA | DE | MR | IT | FR | SI | HI |
|---|---|---|---|---|---|---|---|---|
| `carrom-techniques-and-skills-{lang}.pdf` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `carrom-official-rules-{lang}.pdf` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Paths are declared in `data/books.yaml`. Hugo disables the download button automatically when the file is missing from `static/downloads/`.

After Phase 4 review, export reviewed markdown → PDF and drop at the path for that language.

---

## Phase 6 — Maintenance going forward

- **EN edit → all langs.** Material EN change → re-translate affected chapters (`translate-books.py --force`) → re-review if substantive.
- **New chapter path:** EN draft → Arun sign-off → AI translate → federation review → PDF export.
- **New language path:** declare in `hugo.toml` → `setup-language.py` → `translate-books.py` → register in `data/books.yaml` → federation review → PDF.
- **Glossary wins.** If the same term appears two ways, update README and fix all chapters — never let drift accumulate.
- **Retired URLs.** Do not re-add `/read/` or `/book/` aliases; canonical paths are under `/books/`.

---

## What remains (action list)

| # | Owner | Action | Blocks |
|---|---|---|---|
| 1 | Arun | End-to-end review of EN *Techniques* book; flag editorial fixes | Calling EN "final" |
| 2 | Arun | Send DE seed glossary to DCV for confirmation | DE Phase 4 |
| 3 | DCV | Review DE chapters (techniques + rules); return corrections | DE going from draft → signed-off |
| 4 | Swapnil | Apply DCV corrections one chapter per commit; update `translatedBy` | — |
| 5 | Arun / federations | Identify reviewers for DA, MR, IT, FR, SI, HI | Non-DE Phase 4 |
| 6 | Arun | Provide translated PDFs (or approve export from reviewed markdown) | Download buttons for non-EN |
| 7 | Swapnil | Re-run `translate-books.py --force` after any material EN edit | Keeping langs in sync |

---

## Language matrix (site enablement)

All languages declared in `config/_default/hugo.toml` with matching `menus.{lang}.toml`, `i18n/{lang}.toml`, and `data/about.yaml` entries.

| Code | Language | Techniques (online) | Rules (online) | PDF | Federation review |
|---|---|---|---|---|---|
| `en` | English | ✅ published | ✅ published | ✅ | source |
| `da` | Danish | ✅ AI draft | ✅ AI draft | ⏳ | ⏳ |
| `de` | German | ✅ AI draft | ✅ AI draft | ⏳ | ⏳ DCV |
| `mr` | Marathi | ✅ AI draft | ✅ AI draft | ⏳ | ⏳ |
| `it` | Italian | ✅ AI draft | ✅ AI draft | ⏳ | ⏳ |
| `fr` | French | ✅ AI draft | ✅ AI draft | ⏳ | ⏳ |
| `si` | Sinhala | ✅ AI draft | ✅ AI draft | ⏳ | ⏳ |
| `hi` | Hindi | ✅ AI draft | ✅ AI draft | ⏳ | ⏳ |
