# Arun Deshpande Carrom — Hugo Multilingual Site
## Development Plan

> **How to use this file:** Open this in VSCode with the Claude plugin. Start each session by pasting this file into Claude and saying which week/task you are on. Claude will do the work; you review and commit.

---

## Stack Decision

| Layer | Tool | Cost |
|---|---|---|
| Site generator | Hugo (Extended) | Free |
| Theme | PaperMod | Free |
| Hosting | GitHub Pages | Free |
| CI/CD | GitHub Actions | Free |
| Domain | Bought by Arun (Namecheap or Cloudflare Registrar) | ~€10–12/year |
| Translation | AI first draft + Federation human review | Free |

---

## Prerequisites

Install before starting:

```bash
# macOS
brew install hugo git

# Windows (PowerShell as Admin)
winget install Hugo.Hugo.Extended
winget install Git.Git

# Verify — must say "extended"
hugo version
git --version
```

VSCode extensions to install:
- Hugo Language and Syntax
- Markdown All in One
- Front Matter CMS
- GitLens
- Prettier

---

## Target Folder Structure

```
arun-deshpande-carrom/
│
├── config/
│   └── _default/
│       ├── hugo.toml              ← site config + all 4 languages declared
│       ├── params.toml            ← theme params, author info, profile photo
│       └── menus.en.toml         ← nav per language (duplicate for de/fr/it)
│
├── content/
│   ├── en/                        ← English (source, always complete first)
│   │   ├── _index.md
│   │   ├── about.md
│   │   ├── gallery.md
│   │   ├── contact.md
│   │   └── book/
│   │       ├── _index.md
│   │       ├── chapter-01.md
│   │       ├── chapter-02.md
│   │       └── ...
│   ├── de/                        ← German (first translation)
│   │   └── book/
│   │       └── chapter-01.md      ← mirrors EN structure exactly
│   ├── fr/                        ← French (Phase 2)
│   └── it/                        ← Italian (Phase 2)
│
├── static/
│   ├── images/
│   │   ├── arun-profile.jpg
│   │   ├── gallery/
│   │   └── chapters/              ← diagrams and photos per chapter
│   ├── downloads/
│   │   ├── carrom-book-en.pdf
│   │   └── carrom-book-de.pdf
│   └── CNAME                      ← custom domain (add after domain purchased)
│
├── layouts/
│   └── partials/
│       ├── language-switcher.html ← shows EN/DE/FR/IT toggle on every page
│       └── chapter-nav.html       ← prev / next chapter links
│
├── assets/
│   └── css/
│       └── custom.css             ← style overrides on top of PaperMod
│
└── .github/
    └── workflows/
        └── deploy.yml             ← auto-build and deploy on every git push
```

---

## Carrom Glossary (lock before translating anything)

This glossary must be agreed with the German Carrom Federation before Chapter 1 is translated. Consistent terminology across all chapters is critical.

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

> Add rows as new terms appear during translation. Share this table with each federation reviewer before they begin.

---

## Key Config Files

### config/_default/hugo.toml
```toml
baseURL = "https://arundeshpandecarrom.com/"
title = "Arun Deshpande — Carrom Coach"
theme = "PaperMod"
defaultContentLanguage = "en"
defaultContentLanguageInSubdir = false
enableRobotsTXT = true
enableGitInfo = true

[languages]

  [languages.en]
    languageName = "English"
    languageCode = "en"
    weight = 1
    contentDir = "content/en"
    [languages.en.params]
      description = "Carrom coaching, technique and book by Arun Deshpande"

  [languages.de]
    languageName = "Deutsch"
    languageCode = "de"
    weight = 2
    contentDir = "content/de"
    [languages.de.params]
      description = "Carrom Coaching, Technik und Buch von Arun Deshpande"

  [languages.fr]
    languageName = "Français"
    languageCode = "fr"
    weight = 3
    contentDir = "content/fr"

  [languages.it]
    languageName = "Italiano"
    languageCode = "it"
    weight = 4
    contentDir = "content/it"

[outputs]
  home = ["HTML", "RSS"]

[markup]
  [markup.goldmark.renderer]
    unsafe = true
  [markup.highlight]
    style = "github"
```

### config/_default/params.toml
```toml
author = "Arun Deshpande"
ShowReadingTime = false
ShowShareButtons = false
ShowPostNavLinks = true
ShowBreadCrumbs = true
ShowToc = true
TocOpen = false

[profileMode]
  enabled = true
  title = "Arun Deshpande"
  subtitle = "International Carrom Coach & Author"
  imageUrl = "/images/arun-profile.jpg"
  imageTitle = "Arun Deshpande"

  [[profileMode.buttons]]
    name = "Read the Book"
    url = "/book/"

  [[profileMode.buttons]]
    name = "Gallery"
    url = "/gallery/"

  [[profileMode.buttons]]
    name = "About"
    url = "/about/"
```

### .github/workflows/deploy.yml
```yaml
name: Deploy Hugo site to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
          fetch-depth: 0

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: 'latest'
          extended: true

      - name: Build
        run: hugo --minify

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./public

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### layouts/partials/language-switcher.html
```html
{{ if .IsTranslated }}
<div class="lang-switcher">
  <span>🌐</span>
  {{ range .Translations }}
    <a href="{{ .Permalink }}">{{ .Language.LanguageName }}</a>
  {{ end }}
</div>
{{ end }}
```

### assets/css/custom.css
```css
.lang-switcher {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  font-size: 0.85rem;
  margin-bottom: 1.2rem;
}
.lang-switcher a {
  padding: 2px 8px;
  border: 1px solid currentColor;
  border-radius: 4px;
  text-decoration: none;
  opacity: 0.7;
}
.lang-switcher a:hover { opacity: 1; }
```

---

## Sample Content Frontmatter

### English chapter (content/en/book/chapter-01.md)
```markdown
---
title: "Chapter 1 — The Basics of Carrom"
description: "Board setup, pieces, and the fundamental rules every player must know."
weight: 1
date: 2024-01-01
author: "Arun Deshpande"
cover:
  image: "/images/chapters/chapter-01-cover.jpg"
  alt: "Carrom board setup"
---
```

### German chapter (content/de/book/chapter-01.md)
```markdown
---
title: "Kapitel 1 — Die Grundlagen des Carrom"
description: "Aufbau des Bretts, Spielsteine und die grundlegenden Regeln."
weight: 1
date: 2024-01-01
author: "Arun Deshpande"
translatedBy: "Geprüft von der Deutschen Carrom-Vereinigung"
cover:
  image: "/images/chapters/chapter-01-cover.jpg"
  alt: "Carrom-Brett Aufbau"
---
```

---

## Custom Domain Setup (after Arun buys domain)

1. Create file `static/CNAME` containing just the domain:
   ```
   arundeshpandecarrom.com
   ```

2. At the domain registrar, add these DNS records:
   ```
   Type    Host    Value
   A       @       185.199.108.153
   A       @       185.199.109.153
   A       @       185.199.110.153
   A       @       185.199.111.153
   CNAME   www     yourgithubusername.github.io
   ```

3. In GitHub → repo Settings → Pages → Custom domain → enter domain → enable Enforce HTTPS

---

## Build Phases

### Phase 1 — Foundation (Week 1)
- [ ] Run `hugo new site arun-deshpande-carrom`
- [ ] Add PaperMod theme as git submodule
- [ ] Create `config/_default/hugo.toml` with all 4 languages declared
- [ ] Create `config/_default/params.toml` with profile info
- [ ] Create GitHub repo, push, enable GitHub Pages in repo settings
- [ ] Add `.github/workflows/deploy.yml`
- [ ] Verify site builds and deploys at `yourusername.github.io/`

### Phase 2 — English Content (Week 1–2)
- [ ] Create `content/en/_index.md` (homepage)
- [ ] Create `content/en/about.md` (Arun's bio, titles, achievements)
- [ ] Create `content/en/book/_index.md` (book landing page with chapter list)
- [ ] Create `content/en/book/chapter-01.md` through last chapter
- [ ] Create `content/en/gallery.md` (photo grid)
- [ ] Create `content/en/contact.md`
- [ ] Add profile photo to `static/images/arun-profile.jpg`
- [ ] Add chapter photos to `static/images/chapters/`
- [ ] Add English PDF to `static/downloads/carrom-book-en.pdf`
- [ ] Add language switcher partial and custom CSS
- [ ] Verify all pages live and looking correct

### Phase 3 — German Translation (Week 3–4)
- [ ] Finalise glossary table (above) with German Carrom Federation
- [ ] Translate `content/en/_index.md` → `content/de/_index.md`
- [ ] Translate `content/en/about.md` → `content/de/about.md`
- [ ] Translate `content/en/book/_index.md` → `content/de/book/_index.md`
- [ ] Translate chapters one by one — AI draft, then send to federation for review
- [ ] Receive reviewed chapter → publish (commit + push)
- [ ] Add `translatedBy` frontmatter crediting the federation on each chapter
- [ ] Add German PDF to `static/downloads/carrom-book-de.pdf`
- [ ] Verify language switcher works EN ↔ DE on every page

### Phase 4 — Domain Go-Live
- [ ] Arun purchases domain (recommend Cloudflare Registrar or Namecheap)
- [ ] Add `static/CNAME` file
- [ ] Set DNS records at registrar (see above)
- [ ] Enable custom domain + HTTPS in GitHub Pages settings
- [ ] Test full site at live domain

### Phase 5 — French + Italian (Later)
- [ ] Contact French Carrom Federation for translation review agreement
- [ ] Repeat Phase 3 process for `content/fr/`
- [ ] Contact Italian Carrom Federation
- [ ] Repeat Phase 3 process for `content/it/`

---

## Claude Prompts to Use in VSCode

Copy-paste these into Claude (VSCode plugin) at the relevant phase:

**Scaffold the site:**
> "I am building a Hugo multilingual static site for a carrom coaching book. The plan is in plan.md. Start Phase 1: scaffold the full folder structure, create hugo.toml, params.toml, and the GitHub Actions deploy.yml exactly as specified."

**Add English content:**
> "I am on Phase 2. Create content/en/book/chapter-01.md using the frontmatter format in plan.md. The chapter content is: [paste chapter text from Word doc]"

**Translate a chapter:**
> "Translate this Hugo markdown chapter from English to German. Use the glossary in plan.md for all carrom-specific terms. Preserve all frontmatter fields, add translatedBy field. Output only the complete .md file ready to save. Source: [paste EN chapter]"

**Add a new language:**
> "I am starting Phase 5. Add French (fr) to the site following plan.md. Show me: 1) any hugo.toml changes needed, 2) the folder structure to create under content/fr/, 3) the translated _index.md and about.md files."

**Debug a build error:**
> "My Hugo build is failing with this error: [paste error]. Here is my hugo.toml: [paste]. What is wrong and how do I fix it?"

---

## Rules for This Project

1. **English is always done first** — never start a translation until the English source chapter is finalised
2. **Glossary is locked before Chapter 1 DE** — agree all carrom terms with the federation upfront
3. **translatedBy frontmatter is mandatory** — every translated chapter must credit the reviewer
4. **Images are shared across languages** — never duplicate image files per language; all images live in `static/images/` and are referenced the same way in all markdown files
5. **One chapter per commit** — keep git history clean and easy to trace
6. **Nothing goes live without federation sign-off** — translate → review → commit → push
