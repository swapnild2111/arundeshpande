# Arun Deshpande Carrom

A multilingual static site for **Arun Deshpande** — international carrom coach and author. Hosts his bio, video library, books, photo gallery, contact details, and the full carrom book in English, German, French, and Italian (added progressively).

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
│   ├── hugo.toml                 # site config + 4 languages declared
│   ├── params.toml               # author, hero, stats, achievements
│   └── menus.{en,de,fr,it}.toml  # sidebar nav per language
├── content/
│   ├── en/                       # English (source — always done first)
│   │   ├── _index.md             # homepage hero copy
│   │   ├── about.md              # bio, rendered inside homepage
│   │   ├── contact.md            # email/phone/location, rendered inside contact card
│   │   ├── videos/_index.md      # YouTube video list
│   │   ├── books/_index.md       # PDF library — many downloadable books (plural)
│   │   ├── gallery/_index.md     # photo list
│   │   └── read/_index.md, chapter-01.md, ...  # The book — Arun's Carrom Techniques & Skills, as readable chapters (singular)
│   ├── de/                       # German (mirrors EN structure exactly)
│   ├── fr/                       # French (Phase 5)
│   └── it/                       # Italian (Phase 5)
├── i18n/{en,de,fr,it}.toml       # UI strings (button labels, etc.)
├── layouts/
│   ├── _default/{baseof,list,single,contact}.html
│   ├── index.html                # homepage
│   ├── videos/list.html
│   ├── books/list.html
│   ├── gallery/list.html
│   ├── read/{list,single}.html   # book chapter index + per-chapter pages
│   └── partials/
│       ├── sidebar.html, footer.html
│       └── icons/{home,play,book,image,mail,trophy,medal,...}.html
├── assets/css/main.css           # files Hugo PROCESSES (minify, fingerprint, etc.) — see note below
├── static/
│   ├── images/{arun-profile.jpg, gallery/, book/fig-NN.jpg}
│   ├── downloads/*.pdf           # PDFs referenced by content/{lang}/books
│   ├── js/app.js                 # mobile nav toggle + filter chips
│   └── CNAME                     # custom domain (after purchase)
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

Create `content/en/read/chapter-NN.md` with this frontmatter:

```markdown
---
title: "Chapter N — Title"
description: "One-line description for SEO and chapter list."
weight: N
date: 2026-01-01
author: "Arun Deshpande"
cover:
  image: "/images/chapters/chapter-NN-cover.jpg"
  alt: "Alt text"
---

Chapter body in markdown.
```

### Translating an existing chapter to German

1. Copy `content/en/read/chapter-NN.md` → `content/de/read/chapter-NN.md`.
2. Translate title, description, and body.
3. Add the `translatedBy` field to frontmatter:
   ```yaml
   translatedBy: "Geprüft von der Deutschen Carrom-Vereinigung"
   ```
4. Keep `weight`, `date`, `cover.image` identical to the English file (images are shared across languages).

### Adding photos

- Profile photo: `static/images/arun-profile.jpg`
- Gallery photos: `static/images/gallery/photo-NN.jpg`, then add `<img>` tags inside the `<div class="gallery-grid">` in `content/{lang}/gallery.md`
- Chapter covers/diagrams: `static/images/chapters/`
- Images live in `static/` and are referenced the same way from every language's markdown — never duplicate.

### Adding the book PDF

- `static/downloads/carrom-book-en.pdf`
- `static/downloads/carrom-book-de.pdf`

The book index page already links to these.

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

## Adding a new language (Phase 5: French / Italian)

1. The language is already declared in `config/_default/hugo.toml` and `config/_default/menus.{fr,it}.toml`.
2. Create `content/{fr,it}/_index.md`, `about.md`, `gallery.md`, `contact.md`, `read/_index.md`, then chapters one by one.
3. Confirm glossary terms with the relevant national federation **before** translating Chapter 1.
4. Add `translatedBy` to every translated chapter's frontmatter.
5. Drop the translated PDF at `static/downloads/carrom-book-{fr,it}.pdf`.

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

# Update PaperMod theme to latest
git submodule update --remote themes/PaperMod
git add themes/PaperMod
git commit -m "Update PaperMod theme"

# Create a new content file with default frontmatter
hugo new content content/en/read/chapter-03.md

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

Content © Arun Deshpande. Site built and maintained by Swapnil Deshpande. Theme: [PaperMod](https://github.com/adityatelange/hugo-PaperMod) (MIT).
