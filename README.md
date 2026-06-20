# Arun Deshpande Carrom

A multilingual static site for **Arun Deshpande** — international carrom coach and author. Hosts his bio, gallery, contact details, and the full carrom book in English, German, French, and Italian (added progressively).

Built with **Hugo (Extended)** + **PaperMod** theme, deployed to **GitHub Pages** via GitHub Actions on every push to `main`.

---

## Stack

| Layer | Tool |
|---|---|
| Site generator | [Hugo Extended](https://gohugo.io/) |
| Theme | [PaperMod](https://github.com/adityatelange/hugo-PaperMod) (git submodule) |
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
# Clone with the theme submodule
git clone --recurse-submodules git@github.com:swapnild2111/arundeshpande.git
cd arundeshpande

# If you already cloned without --recurse-submodules:
git submodule update --init --recursive

# Run the dev server
hugo server
# → http://localhost:1313/
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
│   ├── hugo.toml           # site config + all 4 languages declared
│   ├── params.toml         # theme params, profile photo, home buttons
│   └── menus.{en,de,fr,it}.toml  # nav per language
├── content/
│   ├── en/                 # English (source — always done first)
│   │   ├── _index.md
│   │   ├── about.md, gallery.md, contact.md
│   │   └── book/{_index,chapter-01,chapter-02,...}.md
│   ├── de/                 # German (mirrors EN structure exactly)
│   ├── fr/                 # French (Phase 5)
│   └── it/                 # Italian (Phase 5)
├── static/
│   ├── images/{arun-profile.jpg, gallery/, chapters/}
│   ├── downloads/{carrom-book-en.pdf, carrom-book-de.pdf}
│   └── CNAME               # custom domain (added after purchase)
├── layouts/partials/
│   ├── language-switcher.html
│   ├── chapter-nav.html
│   ├── extend_head.html    # injects custom.css
│   └── extend_footer.html  # renders language switcher
├── assets/css/custom.css
├── themes/PaperMod/        # git submodule — do not edit directly
└── .github/workflows/deploy.yml
```

---

## Adding content

### A new English chapter

Create `content/en/book/chapter-NN.md` with this frontmatter:

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

1. Copy `content/en/book/chapter-NN.md` → `content/de/book/chapter-NN.md`.
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

Lock this with each national federation **before** translating Chapter 1 in their language. Add rows as new terms appear during translation.

| English | German | French | Italian |
|---|---|---|---|
| Striker | Schläger | Frappeur | Battitore |
| Queen | Königin | Reine | Regina |
| Coin | Spielstein | Pion | Pedina |
| Baseline | Grundlinie | Ligne de base | Linea di base |
| Thumb shot | Daumentechnik | Coup du pouce | Colpo del pollice |
| Board | Brett | Plateau | Tavola |
| Pocket | Tasche | Poche | Buca |
| Break | Eröffnung | Ouverture | Apertura |
| Due | Aufschlagrecht | Droit de frappe | Diritto di battuta |
| Covering | Abdecken | Couvrir | Coprire |

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
2. Create `content/{fr,it}/_index.md`, `about.md`, `gallery.md`, `contact.md`, `book/_index.md`, then chapters one by one.
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
hugo new content content/en/book/chapter-03.md
```

---

## License & credits

Content © Arun Deshpande. Site built and maintained by Swapnil Deshpande. Theme: [PaperMod](https://github.com/adityatelange/hugo-PaperMod) (MIT).
