# Arun Deshpande Carrom

A multilingual static site for **Arun Deshpande** — international carrom coach and author. Hosts his bio, video library, books, photo gallery, and contact details. The coaching book *Carrom Techniques and Skills* and the ICF rules book are available to read online in **English, Danish, German, Marathi, Italian, French, Sinhala, and Hindi**.

Built with **Hugo (Extended)** and a custom theme (dark / purple, sidebar navigation), deployed to **GitHub Pages** via GitHub Actions on every push to `main`.

---

## Stack

| Layer | Tool |
|---|---|
| Site generator | [Hugo Extended](https://gohugo.io/) |
| Theme | Custom — `layouts/` + `assets/css/main.css` |
| Hosting | GitHub Pages |
| CI/CD | GitHub Actions (`.github/workflows/deploy.yml`) |
| Translation workflow | AI first draft → national federation human review |

---

## Prerequisites

```bash
# macOS
brew install hugo git

# Windows (PowerShell as Admin)
winget install Hugo.Hugo.Extended
winget install Git.Git

# Verify — must say "extended"
hugo version
```

Recommended VSCode extensions: *Hugo Language and Syntax*, *Markdown All in One*, *Front Matter CMS*, *GitLens*, *Prettier*.

---

## Getting started

```bash
git clone git@github.com:swapnild2111/arundeshpande.git
cd arundeshpande

# Run the dev server
hugo server
# → http://localhost:1313/arundeshpande/
```

Build for production locally:

```bash
hugo --minify
# Output → ./public/
```

---

## Project structure

```
arundeshpande/
├── config/_default/
│   ├── hugo.toml                 # site config + 8 languages
│   ├── params.toml               # author, hero, stats, achievements
│   └── menus.{en,da,de,mr,it,fr,si,hi}.toml  # sidebar nav per language
├── content/
│   ├── en/                       # English (source — always done first)
│   │   ├── _index.md             # homepage hero copy
│   │   ├── contact.md            # email/phone/location
│   │   ├── videos/               # YouTube video categories
│   │   ├── gallery/_index.md     # photo list
│   │   └── books/
│   │       ├── _index.md         # book catalog landing
│   │       ├── students/
│   │       │   └── carrom-techniques-and-skills/   # 14 chapters + _index.md
│   │       └── rules/
│   │           └── official-carrom-rules/          # 8 chapters + _index.md
│   ├── da/ de/ mr/ it/ fr/ si/ hi/   # mirror EN structure
├── data/
│   ├── books.yaml                # catalog metadata, PDF paths, per-lang titles
│   ├── about.yaml                # bio text per language
│   └── problem-solutions.yaml    # YouTube Problem/Solution pairs
├── i18n/{en,da,de,mr,it,fr,si,hi}.toml   # UI strings
├── layouts/
│   ├── _default/{baseof,list,single,contact}.html
│   ├── index.html                # homepage
│   ├── videos/                   # video list + problems-solutions
│   ├── books/{list,single,category}.html   # book catalog + chapter pages
│   ├── gallery/list.html
│   └── partials/                 # sidebar, footer, book-grid, seo, ...
├── assets/css/main.css           # Hugo-processed CSS (minify + fingerprint)
├── scripts/
│   ├── extract-book.py           # .docx → EN markdown chapters
│   ├── generate-book-pdfs.py     # docx → translate → PDF (techniques book)
│   ├── generate-rules-pdfs.py    # markdown chapters → PDF (official rules)
│   ├── translate-books.py        # EN → da/de/mr/it/fr/si/hi book markdown
│   ├── setup-language.py         # i18n + about + non-book pages for a new lang
│   └── sync-problem-solutions.py # YouTube → data/problem-solutions.yaml
├── static/
│   ├── images/{arun-profile.jpg, gallery/, book/fig-NN.jpg}
│   ├── downloads/*.pdf           # book PDFs (see data/books.yaml)
│   └── js/app.js                 # mobile nav toggle + filter chips
└── .github/workflows/deploy.yml
```

### `static/` vs `assets/` — when to use which

Both folders are tracked in git and both end up in the deployed site. They differ in **what Hugo does at build time**:

| | `static/` | `assets/` |
|---|---|---|
| **What happens at build** | Bytes copied 1:1 into `public/` | Run through Hugo Pipes (minify, fingerprint, SCSS compile, image resize, ...) |
| **Reference from markdown / HTML** | Direct path: `<img src="/images/foo.jpg">`, `[Download](/downloads/x.pdf)` | Through `resources.Get` in a template: `{{ (resources.Get "css/main.css") | minify | fingerprint }}` then `.RelPermalink` |
| **Output filename** | Same as input (`main.css`) | Can be fingerprinted (`main.min.96a05d4...css`) for cache busting |
| **Put files here when...** | They're already in their final form: photos, PDFs, hand-written JS, favicon, CNAME | Hugo needs to do something to them: CSS minification + fingerprinting, SCSS compilation, image variants |

In this project: only `assets/css/main.css` lives in `assets/` (it gets minified and fingerprinted so browsers cache it for a year but pick up changes the moment we deploy a new version). Everything else — figures, the IAKC PDF, profile photo, app.js, favicon — sits in `static/` because none of it benefits from Hugo's processing.

Don't merge the two. Photos and PDFs in `assets/` would need their references rewritten through `resources.Get`, and CSS in `static/` would lose its cache-busting fingerprint.

---

---

## Adding content

### A new English chapter

Create `content/en/books/students/carrom-techniques-and-skills/chapter-NN.md` with this frontmatter:

```markdown
---
title: "Chapter N — Title"
description: "One-line description for SEO and chapter list."
weight: N
date: 2026-01-01
author: "Arun Deshpande"
cover:
  image: "/images/book/fig-NN.jpg"
  alt: "Alt text"
---

Chapter body in markdown.
```

### Translating chapters to another language

**Automated (recommended):** use the translation script after English is finalised:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install deep-translator pyyaml

# Translate both books to German (also: da, mr, it, fr, si, hi)
python3 scripts/translate-books.py de

# Overwrite existing translated files
python3 scripts/translate-books.py de --force
```

The script preserves images, HTML, URLs, and international carrom terms. Each translated chapter gets a `translatedBy` frontmatter line noting it is an AI draft.

**Manual:** copy `content/en/books/students/carrom-techniques-and-skills/chapter-NN.md` → `content/{lang}/books/students/carrom-techniques-and-skills/chapter-NN.md`, translate title/description/body, and add `translatedBy`. Keep `weight`, `date`, and `cover.image` identical (images are shared).

### Adding photos

- Profile photo: `static/images/arun-profile.jpg`
- Gallery photos: `static/images/gallery/photo-NN.jpg`, then add `<img>` tags inside the `<div class="gallery-grid">` in `content/{lang}/gallery/_index.md`
- Book figures: `static/images/book/fig-NN.jpg` — referenced as `/images/book/fig-NN.jpg` from every language
- Images live in `static/` and are referenced the same way from every language's markdown — never duplicate.

### Adding book PDFs

PDF download buttons are driven by `data/books.yaml`. Drop files at the paths listed there, e.g.:

- `static/downloads/carrom-techniques-and-skills-en.pdf`
- `static/downloads/carrom-techniques-and-skills-de.pdf`
- `static/downloads/carrom-official-rules-en.pdf`

If a PDF file is missing for a language, the download button is automatically disabled for that locale.

---

## Carrom glossary (locked terminology)

This glossary is the source of truth for both the English book text and any translation. **English column** is cross-checked against the [IAKC Official Rules PDF](https://www.iakc.org/wp-content/uploads/2020/02/Carrom-Official-Rules.pdf). **German column** is cross-checked against the [Deutscher Carrom Verband (carrom.de)](https://www.carrom.de/das-ist-carrom) rules page. The DCV may override any cell during Phase 4 review — when they do, update this table, then re-grep all DE chapters.

### Equipment

| English | German | Notes |
|---|---|---|
| Carrom | Carrom | proper noun |
| Carrom Board (C/B) | Carrombrett (also Carromboard) | DCV uses both |
| Carromman / Coin (C/m) | Spielstein | IAKC's formal term is "Carromman"; the book uses "coin" — we keep "coin" for readability |
| Striker | Striker | DCV keeps in English (parenthesises "Schuss-Stein") |
| Queen (red coin) | Queen (roter Stein) | DCV keeps in English |
| Pocket | Eckloch (also Loch) | DCV's word for the corner hole |
| Nets | Netze | |
| Base Line | Grundlinie | |
| Base Circle | Grundkreis | |
| Centre Circle | Mittelkreis | |
| Outer Circle | Außenkreis | |
| Frame | Rahmen | |
| Arrow (between base circles) | Pfeil | |
| Imaginary Lines | gedachte Linien | |
| Stand / Table | Ständer / Tisch | |
| Stool / Chair | Hocker / Stuhl | |
| Powder | Carrompulver (Gleitpulver) | |
| Light / Lamp | Lampe | |
| Cushion (the side, for rebounds) | Bande | DCV uses "über Bande spielen" |

### Match structure

| English | German | Notes |
|---|---|---|
| Match | Match (also Partie) | |
| Game (race to 25 points) | Game | DCV keeps in English |
| Board (one round) | Board | DCV keeps in English |
| Singles | Einzel | |
| Doubles | Doppel | |
| Trial Board | Probespiel | |
| Toss | Auslosen | |
| Change of Sides | Seitenwechsel | |
| Player | Spieler / Spielerin | |
| Opponent | Gegner | |
| Umpire | Schiedsrichter | |
| Chief Referee | Hauptschiedsrichter | |

### Actions and scoring

| English | German | Notes |
|---|---|---|
| Stroke | Schuss | |
| Proper stroke | regelgerechter Schuss | |
| Improper stroke | Fehlschuss / regelwidriger Schuss | |
| Push (jerk of elbow) | Stoß / Schieben | IAKC #11 — illegal motion |
| Thumbing (thumb shot) | Daumentechnik | |
| Break (the opening) | Anstoß | |
| Finish | Abschluss | |
| To pocket (verb) | versenken (also einlochen) | |
| Pocketing (noun) | Versenken | |
| Placing (a coin) | Platzieren | |
| Turn | Spielzug | |
| Concede | aufgeben | |
| Shot | Shot / Schlag | |
| Pair | Pair | |
| Cannon | Cannon | spelled with two n's — corrects the docx's "CANON" |
| Covering (the Queen) | Bestätigung | DCV's term |
| Due (striker-only pocket) | Strafstein | |
| Penalty | Strafe / Strafstein | |
| Foul | Fehlschuss | |
| Simple foul | einfacher Fehlschuss | |
| Technical foul | technischer Fehlschuss | |
| White Slam | White Slam | universal carrom term |
| Black Slam | Black Slam | universal carrom term |

### Grips (from Arun's book — not in IAKC)

| English | German |
|---|---|
| Grip | Griff |
| Natural grip | natürlicher Griff |
| Scissor grip | Scherengriff |
| Locking grip | Sperrgriff |
| Middle finger flat grip | Mittelfinger-Flachgriff |

### Strokes (coaching vocabulary — kept in English globally, in both EN and DE chapters)

`Shower of Strokes`, `Straight Cut`, `Cross Cut` (also Minus Cut), `Double`, `Cross Double`, `Press`, `Touch`, `Double Touch`, `Glance`, `Double Glance`, `Brush`, `Rebound`, `Simple Rebound`, `Langda Rebound`, `Hook`, `Third Pocket`, `Cross Third Pocket`, `Second Pocket`, `Cross Second Pocket`, `Turning`, `Slip`, `Striker Slip`, `Bomb` (also `Bum`), `Force`, `Spin`.

`Third/Second Pocket` becomes `Drittes/Zweites Eckloch` in DE bodies (since DCV uses "Eckloch"); the stroke name itself stays English.

### Strategy and mental qualities

| English | German |
|---|---|
| Defence | Verteidigung |
| Direct Defence | direkte Verteidigung |
| Indirect Defence | indirekte Verteidigung |
| Offence | Angriff |
| Concentration | Konzentration |
| Observation | Beobachtung |
| Patience / Stability | Geduld |
| Over-confidence | Überheblichkeit |
| Open mind | Offenheit |
| Practice | Übung |

### Organisations

| English | German |
|---|---|
| International Carrom Federation (ICF) | Internationaler Carrom-Verband |
| German Carrom Federation (DCV) | Deutscher Carrom Verband (DCV) |
| German Championship | Deutsche Meisterschaft |

---

## Deployment

Pushing to `main` triggers `.github/workflows/deploy.yml`, which builds the site with Hugo and deploys to GitHub Pages.

**One-time GitHub setup:**
1. GitHub repo → **Settings → Pages → Source** = *GitHub Actions*
2. Wait for the first workflow run on `main` to complete
3. The site will be live at `https://swapnild2111.github.io/arundeshpande/`

### Custom domain (after Arun purchases)

1. Create `static/CNAME` containing only the domain, e.g.:
   ```
   arundeshpandecarrom.com
   ```
2. At the registrar (Cloudflare or Namecheap recommended), add:
   ```
   Type    Host    Value
   A       @       185.199.108.153
   A       @       185.199.109.153
   A       @       185.199.110.153
   A       @       185.199.111.153
   CNAME   www     swapnild2111.github.io
   ```
3. GitHub repo → **Settings → Pages → Custom domain** → enter domain → enable *Enforce HTTPS*.
4. Update `baseURL` in `config/_default/hugo.toml` to the live domain.

---

## Adding a new language

1. **Declare the language** in `config/_default/hugo.toml` and create `config/_default/menus.{lang}.toml` (copy an existing menu file and translate labels).
2. **Scaffold site pages** (i18n, about bio, contact, videos, gallery — not the books):
   ```bash
   source .venv/bin/activate   # needs deep-translator + pyyaml
   python3 scripts/setup-language.py {lang}
   ```
3. **Translate the books:**
   ```bash
   python3 scripts/translate-books.py {lang}
   ```
4. **Register books** in `data/books.yaml` — add `{lang}` entries under `titles`, `descriptions`, `tagLabels`, `pdfs`, and set `languages.{lang}: true`.
5. **Add the bio** in `data/about.yaml` for the new language.
6. Confirm glossary terms with the relevant national federation before publishing translated chapters.
7. Drop translated PDFs at `static/downloads/carrom-techniques-and-skills-{lang}.pdf` (and rules PDF if applicable).
8. Run `hugo --minify` and verify all pages build.

---

## Project rules

1. **English is always done first.** Never start a translation until the English source chapter is finalised.
2. **Glossary is locked before Chapter 1 in any language.** Agree all carrom terms with the federation upfront.
3. **`translatedBy` frontmatter is mandatory** on every translated chapter, crediting the reviewer.
4. **Images are shared across languages** — all images live in `static/images/` and are referenced identically from every language.
5. **One chapter per commit** — keeps git history clean and easy to trace.
6. **Nothing goes live without federation sign-off** — translate → review → commit → push.

---

## Common tasks

```bash
# Run dev server with drafts visible
hugo server -D

# Build and check output
hugo --minify
ls public/

# Extract EN book chapters from the .docx (images must already be in static/images/book/)
python3 scripts/extract-book.py

# Generate downloadable PDFs from the source docx (all 8 languages; needs LibreOffice)
pip install -r requirements.txt   # python-docx, deep-translator, markdown
brew install --cask libreoffice    # once, for soffice
python3 scripts/generate-book-pdfs.py
python3 scripts/generate-book-pdfs.py da --force   # re-translate one language

# Generate official rules PDFs from Hugo markdown chapters (all 8 languages)
python3 scripts/generate-rules-pdfs.py
python3 scripts/generate-rules-pdfs.py de --force

# Translate books to a language
python3 scripts/translate-books.py de

# Create a new content file with default frontmatter
hugo new content content/en/books/students/carrom-techniques-and-skills/chapter-03.md

# Sync Problems & Solutions pairs from YouTube (see below)
python3 scripts/sync-problem-solutions.py
```

---

## Sync Problems & Solutions (YouTube)

Arun uploads **Problem N** / **Solution N** videos to the [Carrom Guru YouTube channel](https://www.youtube.com/@Shrikant_Potharkar_carrom). The site reads pairs from `data/problem-solutions.yaml`. Missing partners show a **Coming Soon** placeholder.

### Automatic (recommended)

1. Create a [YouTube Data API v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com) key (free quota is enough).
2. Add it as a GitHub repository secret: **Settings → Secrets → Actions → `YOUTUBE_API_KEY`**
3. The workflow [`.github/workflows/sync-problem-solutions.yml`](.github/workflows/sync-problem-solutions.yml) runs **every Sunday at 06:00 UTC** and can be triggered manually from the **Actions** tab.

When new videos are found, the workflow commits an updated `data/problem-solutions.yaml` and the deploy workflow republishes the site.

### Manual (local)

```bash
# Sync from YouTube (requires API key)
YOUTUBE_API_KEY=your_key python3 scripts/sync-problem-solutions.py

# Preview without writing
YOUTUBE_API_KEY=your_key python3 scripts/sync-problem-solutions.py --dry-run
```

Then commit and push `data/problem-solutions.yaml` if it changed.

---

## License & credits

Content © Arun Deshpande. Site built and maintained by Swapnil Deshpande.
