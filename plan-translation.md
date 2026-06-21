# Plan: Publish the book in EN, then translate to DE

Source: `CarromTechniqandSkills.docx` — *Carrom Techniques and Skills* by Arun Deshpande.

| Property | Value |
|---|---|
| Word count | ~16,830 words |
| Paragraphs | 270 |
| Embedded images | 52 |
| Native structure | Already uses Heading1 / Heading2 styles |

---

## Workflow rules (locked)

1. **English first, German second.** No DE chapter is written until its EN counterpart is finalised and merged.
2. **Glossary is locked before any DE chapter is translated.** Approve all carrom terms with the German Carrom Federation upfront.
3. **AI first draft, federation review second.** Claude generates the German translation. Arun hands it to the German Carrom Federation for a corrections pass. The reviewer's name goes in `translatedBy` frontmatter on every chapter.
4. **Images shared across languages.** All extracted images live at `static/images/book/` and are referenced by identical paths from EN and DE.

---

## Phase 0 — Extract & restructure (Claude, ~1 session)

Goal: get the .docx contents into a Hugo-friendly form **without translating yet**.

- **0.1** Extract all 52 images from the .docx into `static/images/book/` with stable filenames (`book-fig-01.png`, `book-fig-02.png`, ...). Build a list of which image was anchored to which paragraph so we can place them in the right markdown later.
- **0.2** Parse the .docx XML into a structured JSON: every paragraph with its style (`Heading1`, `Heading2`, `BodyText`, `-`), text, and any image anchor.
- **0.3** Map the heading structure to chapter pages. **Final mapping (locked after parsing all 270 paragraphs and 52 image anchors):**

| # | Slug | Title | Words | Images |
|---|---|---|---|---|
|  1 | `chapter-01` | Introduction: What is Carrom | 112 | 6 |
|  2 | `chapter-02` | Equipment | 277 | 1 |
|  3 | `chapter-03` | Basic Rules | 363 | 0 |
|  4 | `chapter-04` | Grips | 511 | 9 |
|  5 | `chapter-05` | The Break | 299 | 5 |
|  6 | `chapter-06` | Strokes — Cut, Double, Press | 1,158 | 9 |
|  7 | `chapter-07` | Touch, Shot, Pair, Canon | 1,231 | 7 |
|  8 | `chapter-08` | Glance, Brush, Rebound, Hook | 1,147 | 6 |
|  9 | `chapter-09` | Pockets and Turning | 985 | 8 |
| 10 | `chapter-10` | Slip, Striker Slip, Double Touch | 413 | 3 |
| 11 | `chapter-11` | Bomb and Force | 1,060 | 17 |
| 12 | `chapter-12` | Defence and Offence | 3,602 | 12 |
| 13 | `chapter-13` | Mental Qualities of a Player | 3,802 | 9 |
| 14 | `chapter-14` | Advanced Stroke Positions | 1,798 | 32 |
|   |   | **TOTAL** | **16,758** | **52*** |

\* Some images are anchored to paragraphs that fall on a chapter boundary; the final placement happens during Phase 1 when we walk the docx XML paragraph-by-paragraph. The 52 image count is the total in the docx; per-chapter counts above are best estimates from paragraph windows.

---

## Phase 1 — English chapter pages (Claude, ~1 session)

Goal: every chapter listed above lives at `content/en/read/<slug>.md` and renders cleanly with images.

- **1.1** Generate the markdown for every chapter from the structured JSON. Each chapter file gets frontmatter (`title`, `weight`, `cover`, `date`, `author`) plus the body in markdown with image references at their original positions.
- **1.2** Light editorial pass — fix any OCR-style glitches the docx has, normalise carrom punctuation (e.g. "Carrom" capitalised, smart quotes, em dashes), but **do not change meaning or remove content**. Anything ambiguous gets flagged in a comment for Arun.
- **1.3** Update `content/en/read/_index.md` so the chapter list reflects the new structure.
- **1.4** Update the read/single layout if needed so cover images render and prev/next nav stays correct.
- **1.5** Verify `hugo --minify` builds cleanly, all chapter pages return 200, all images load. Screenshot a sample chapter to confirm.
- **1.6** Commit. Arun reviews the English version end-to-end before we start German.

**Stop point:** Arun's sign-off on English content. Don't proceed to Phase 2 without it.

---

## Phase 2 — Glossary lock (Arun + German Carrom Federation, async)

Goal: every carrom-specific term has an agreed German word **before** any chapter is translated.

- **2.1** Claude proposes a glossary table. I'll seed it from the strokes already named in the book; the federation finalises.
- **2.2** Lock the glossary in `README.md` (the table already there gets filled in for German).

**Seed glossary (Claude proposes, Federation confirms):**

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
| Canon | Canon |
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

Note: I've leaned toward keeping the international stroke names in English (Press, Touch, Pair, Glance, Brush, Hook, Slip, Bomb, Force) because they're the words German players actually use at the table. The Federation will adjust where they prefer a German equivalent.

**Stop point:** Federation-approved glossary committed to README.

---

## Phase 3 — German first draft (Claude, ~1 session per pass)

Goal: every EN chapter has a DE translation that follows the locked glossary.

- **3.1** For each chapter under `content/en/read/`, generate `content/de/read/<same-slug>.md` with the same structure, frontmatter (translated where appropriate), images (same paths), and a German body.
- **3.2** Strictly honour the glossary. If a term is encountered that isn't in the glossary, leave it in English with a `<!-- TODO: glossary term -->` comment for the Federation to settle.
- **3.3** Add `translatedBy: "Reviewed by the German Carrom Federation"` to every chapter's frontmatter (final reviewer name fills in during Phase 4).
- **3.4** Build and verify all DE pages render. Commit.

**Stop point:** All DE chapters published as a draft for review. Don't go live yet.

---

## Phase 4 — Federation review (Arun + DCF, async)

Goal: every German chapter is reviewed by the Federation, corrections applied.

- **4.1** Federation reviews each chapter, sends back annotated changes (PDF / Word comments / GitHub PR — whichever they prefer).
- **4.2** Apply corrections one chapter at a time. **One chapter per commit**, message format `de: review of chapter-NN — <topic>`. Replace the generic `translatedBy` value with the named reviewer.
- **4.3** If the Federation finds a glossary term we got wrong, update the glossary in README, then re-grep all DE chapters and apply the correction site-wide before moving on. Glossary drift is the one thing we cannot tolerate.

**Stop point:** All DE chapters reviewed and live. Done.

---

## Phase 5 — Maintenance rules going forward

- **EN edit triggers a DE revisit.** Any future edit to a published English chapter must be mirrored to the German version (and re-reviewed if it's material).
- **New chapters follow the same path:** EN draft → Arun sign-off → DE draft → DCF review.
- **The glossary is the source of truth.** If we ever find ourselves translating a carrom term in two different ways, the glossary wins.

---

## What I'll do next (and what I'm waiting on)

1. **Phase 0** — extract images, parse XML, finalise the chapter mapping. **Ready to start now.**
2. **Phase 1** — generate the English markdown chapter pages. **Ready to start after Phase 0.**
3. **Arun sign-off on English** — *waiting on you / Arun.*
4. **Phase 2 glossary lock with the German Carrom Federation** — *waiting on Arun to send the seed list above to the Federation.*
5. **Phase 3 German draft** — Claude, **only after step 4 is locked**.
6. **Phase 4 Federation review** — *waiting on the German Carrom Federation.*
