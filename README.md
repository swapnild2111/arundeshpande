<div align="center">

# 🎯 Arun Deshpande Carrom

**A free, open-source coaching portal for one of carrom's master coaches — built so the game reaches every learner, in every language.**

[![Live](https://img.shields.io/badge/Live-swapnild2111.github.io%2Farundeshpande-4f8ef7?style=flat-square)](https://swapnild2111.github.io/arundeshpande/)
[![License: MIT](https://img.shields.io/badge/License-MIT-4ade80?style=flat-square)](LICENSE)
[![Built with Hugo](https://img.shields.io/badge/Built%20with-Hugo-ff4088?style=flat-square)](https://gohugo.io/)
[![Languages: 11](https://img.shields.io/badge/Languages-11-7dd3fc?style=flat-square)](#languages)
[![No tracking](https://img.shields.io/badge/Tracking-none-f87171?style=flat-square)](#why-this-exists)

[**👉 Open the portal**](https://swapnild2111.github.io/arundeshpande/)

</div>

---

## What's inside

Three decades of carrom coaching from **Shri Arun Deshpande** — 7× Maharashtra State Champion and former coach of the India National Carrom Team — gathered in one place, free to read and free to download, in 11 languages.

| Section | What's there | What you do |
|---|---|---|
| 📘 **Carrom Techniques and Skills** | Arun's complete coaching book — 14 chapters | Read online or download the PDF in your language. Covers grip, break, every major stroke (cut, double, press, touch, glance, brush, rebound, slip, bomb, force), defence, offence, and advanced board positions |
| 📜 **Official Carrom Rules** | The complete ICF laws — 8 chapters | Equipment, definitions, match procedure, scoring, fouls, and the Queen rules — sourced from the International Carrom Federation |
| 🎥 **Video Library** | 60+ tutorial videos | Categorised by skill level — Beginner / Intermediate / Champion. Each chapter section links to the videos that demonstrate the stroke on the board |
| 🧩 **Problems & Solutions** | Paired YouTube videos | Real board situations and how to play out of them. New pairs auto-sync from Arun's channel weekly |
| 📥 **Downloadable PDFs** | Both books in every language | Professionally rendered. Italian translation is currently an AI draft pending the authorised European Carrom Confederation version |

---

## Why this exists

Arun's mission is straightforward: **carrom should reach as many players as possible, freely.** Most carrom material online is gated, paywalled, English-only, or scattered across YouTube comments. This portal isn't.

- 🆓 **Completely free** — no ads, no subscriptions, no premium tier
- 🔐 **No account, no email, no signup** — open the site, start reading
- 🚫 **No tracking on you** — no analytics, no fingerprinting, no third-party scripts beyond YouTube embeds when you play a video
- 📚 **Real coaching content** — every chapter is Arun's own writing, with figures from the original manuscript and tutorial videos pinned to the matching sections
- 🌐 **11 languages** — English, Dansk, Deutsch, मराठी, Italiano, Français, සිංහල, हिन्दी, ગુજરાતી, Polski, ꯃꯩꯇꯩꯂꯣꯟ — auto-detected from your browser at the root URL
- 📱 **Works on your phone** — responsive layout; sticky chapter navigation; no app store
- 💾 **Your preferences stay with you** — the only client-side state is your chosen language, kept in `localStorage`

It started as a side project to put one book online for one carrom coach. It grew into a 9-language portal because the European Carrom Confederation, the Sri Lankan players, and the Marathi-speaking kids back home all wanted to read it in their own language.

---

## Standout features

### 🌐 9 languages — and each PDF too

Every page of the site translates to **English, Dansk, Deutsch, मराठी, Italiano, Français, සිංහල, हिन्दी, ગુજરાતી, Polski, ꯃꯩꯇꯩꯂꯣꯟ**. So do both PDF downloads. The language switcher in the top-right groups them by region (International / European / South Asian) so you can find yours fast — and the site auto-detects your browser's preferred language at the root URL so most visitors never have to switch manually.

### 🤖 AI-drafted, human-reviewed translations

Translations start as an **AI draft** through a custom pipeline that uses Google Translate but protects what shouldn't be touched — carrom terminology (Striker, Queen, Cut, Touch, Bomb…), HTML markup, image paths, and URLs all survive intact, even across script changes (Latin → Devanagari → Sinhala → Gujarati). Each chapter then gets reviewed by a native speaker, with a `translatedBy` line crediting the reviewer once a translation is validated.

### 📍 Each book chapter linked to the videos that demonstrate it

`data/chapter-videos.yaml` maps every chapter section to the YouTube tutorial videos that show the stroke on the board. So when you're reading about the **Cross Cut**, the matching videos are right there in the chapter, sorted by skill level (Beginner / Intermediate / Champion). Works across all 9 languages — the mapping uses English slugs internally, then resolves to whatever the section is called in your language by matching its position.

### 📚 Click-anywhere book rows, language-picker PDF download

The Books page renders each book as a compact horizontal row — small cover, title, meta, two-line description — that's clickable anywhere except on the action buttons. The green **Download PDF** button opens a per-language picker showing all 9 versions; the current locale's row is highlighted, but no PDF auto-downloads — every download is an explicit choice.

### 📖 Sticky chapter navigation with live scroll progress

Every chapter page has a thin top rail that follows you down the page: **← Previous chapter | Chapter N of M | Next chapter →**. A subtle violet progress bar along the rail's bottom edge fills as you scroll through the chapter prose (not the page) — so you always know where you are without breaking the reading flow.

### 🎬 Weekly auto-sync of Problem/Solution video pairs

A scheduled GitHub Action polls Arun's YouTube channel every Sunday at 06:00 UTC, finds any new **Problem N** / **Solution N** pairs, and commits them to `data/problem-solutions.yaml`. The deploy workflow then republishes the site automatically. Missing partners (a Problem with no Solution yet) show a **Coming Soon** placeholder.

### 🛡️ Privacy by design

No analytics, no cookies, no third-party trackers. The only network requests the site makes are to GitHub Pages (for the site itself), Google Fonts (for the typography), and YouTube (only when you actively play a video). Your reading position, language choice, and any other state lives entirely in your browser.

---

## Languages

| Code | Language | Native label | Region |
|---|---|---|---|
| `en` | English | English | International |
| `da` | Danish | Dansk | European |
| `de` | German | Deutsch | European |
| `it` | Italian | Italiano | European |
| `fr` | French | Français | European |
| `mr` | Marathi | मराठी | South Asian |
| `hi` | Hindi | हिन्दी | South Asian |
| `gu` | Gujarati | ગુજરાતી | South Asian |
| `pl` | Polish | Polski | European |
| `si` | Sinhala | සිංහල | South Asian |
| `mni` | Manipuri (Meitei) | ꯃꯩꯇꯩꯂꯣꯟ | South Asian |

Want to review or improve the translation into your language? **That's the most valuable contribution possible.** Open an issue with the language code in the title, or reach Arun via the [Contact page](https://swapnild2111.github.io/arundeshpande/en/contact/).

---

## Quick start

### Use it (just open the link)

👉 **<https://swapnild2111.github.io/arundeshpande/>**

That's it. Open the page, pick your language from the top-right corner, start reading. Bookmark, leave, come back — your language choice is remembered.

### For developers

The site uses **Hugo Extended** as a static site generator with a custom theme (no third-party theme dependency). The entire visual identity lives in a single `assets/css/main.css` file. Deployment is fully automated through GitHub Actions on every push to `main`.

```bash
# macOS — install Hugo Extended + Git
brew install hugo git

# Clone and serve
git clone https://github.com/swapnild2111/arundeshpande.git
cd arundeshpande
hugo server
# → http://localhost:1313/arundeshpande/
```

Build for production locally:

```bash
hugo --minify   # output to ./public/
```

### Project layout

```
arundeshpande/
├── config/_default/
│   ├── hugo.toml                # site config, 9 languages
│   ├── params.toml              # author, hero, stats, achievements
│   └── menus.{lang}.toml        # sidebar nav per language
├── content/
│   ├── en/                      # English — the source of truth
│   │   └── books/
│   │       ├── students/carrom-techniques-and-skills/   # 14 chapters
│   │       └── rules/official-carrom-rules/             # 8 chapters
│   └── da/ de/ mr/ it/ fr/ si/ hi/ gu/ pl/ mni/          # mirror EN
├── data/
│   ├── books.yaml               # catalogue, PDF paths, per-lang titles
│   ├── about.yaml               # bio per language
│   ├── chapter-videos.yaml      # maps chapter sections → tutorial videos
│   └── problem-solutions.yaml   # Problem/Solution video pairs
├── i18n/{lang}.toml             # UI strings, per language
├── layouts/                     # Hugo templates (custom theme)
├── assets/css/main.css          # the entire theme
├── static/                      # images, PDFs, JS
├── scripts/                     # translation + PDF generation pipeline
└── .github/workflows/           # auto-deploy + weekly P&S sync
```

### Translation pipeline

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install deep-translator pyyaml python-docx markdown

# Translate both books to a new language
python3 scripts/translate-books.py de

# Regenerate PDFs (requires LibreOffice on PATH)
brew install --cask libreoffice
python3 scripts/generate-book-pdfs.py de
python3 scripts/generate-rules-pdfs.py de
```

The translation script uses self-closing XML-style sentinels (`<x42/>`) to protect terminology and HTML from Google Translate. Each translated chapter gets a `translatedBy` frontmatter line noting it's an AI draft until a native reviewer signs off.

### Adding a new language

1. Declare the language in `config/_default/hugo.toml` and create `config/_default/menus.{lang}.toml`.
2. Scaffold site pages: `python3 scripts/setup-language.py {lang}`.
3. Translate the books: `python3 scripts/translate-books.py {lang}`.
4. Register entries under `titles`, `descriptions`, `tagLabels`, `pdfs`, `languages.{lang}: true` in `data/books.yaml`.
5. Add the bio in `data/about.yaml` under the new language code.
6. Generate the PDFs: `python3 scripts/generate-book-pdfs.py {lang}` and `python3 scripts/generate-rules-pdfs.py {lang}`.
7. Build (`hugo --minify`) and verify all pages render.

### Problem & Solution auto-sync

A scheduled GitHub Action ([`sync-problem-solutions.yml`](.github/workflows/sync-problem-solutions.yml)) polls Arun's YouTube channel every Sunday and commits new Problem/Solution video pairs to `data/problem-solutions.yaml`. To enable it, add a `YOUTUBE_API_KEY` secret to the repo (free YouTube Data API v3 quota is enough).

---

## Contributing

If you spot a translation issue, a broken video link, or any factual error in the rules — please open an issue with the language code in the title, e.g. `[de] Chapter 6 — Cut section`.

The most valuable contribution is **native-speaker translation review.** Each AI-drafted chapter benefits enormously from someone who actually plays carrom in that language. The Italian translation is currently the AI draft only — the European Carrom Confederation has offered an existing Arun-authorised Italian translation that will replace it soon.

---

## License

- **Code** — [MIT License](LICENSE). Hugo templates, CSS, JavaScript, build scripts, and site configuration are free to use, fork, and modify.
- **Book content** — © Arun Deshpande. *Carrom Techniques and Skills* and all original coaching material remain his copyright. Please contact him before reproducing or redistributing the book.
- **ICF rules** — summarised from publicly-available sources. See `data/books.yaml` for attribution.

Built and maintained by [Swapnil Deshpande](https://github.com/swapnild2111). Coaching by Shri Arun Deshpande — and three decades of carrom knowledge that the world deserves to learn from.
