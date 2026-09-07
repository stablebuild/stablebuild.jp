# stablebuild.jp Project Notes

## Site Structure
- `index.html` — Japanese homepage (root)
- `features/index.html` — Japanese features page (scraped from stablebuild.com/features, then customised)
- `pricing/index.html` — Japanese pricing page (scraped from stablebuild.com/pricing, then customised)
- `company.html` — Company profile page, Japan-only, exists only on stablebuild.jp
- `blog/` — Japanese blog. Generated from Markdown, not hand-edited; see Blog below
- `_config.yml` — Jekyll config whose only job is `exclude`: it keeps CLAUDE.md,
  `blog/build.py` and the blog sources in the repo but out of the published site

## Link Conventions

### Logo / home button
- The StableBuild logo (header and footer) should always link to `/` (relative), so it returns to the Japanese homepage on stablebuild.jp

### Footer links
- All footer links should be **absolute** (e.g. `https://www.stablebuild.com/pricing`)
- Exception: `company.html` stays **relative** (`../company.html` from a subdirectory, `company.html` from root) because it is a local JP-only file
- Exception: pages that have a Japanese version on stablebuild.jp should use a **relative** link (e.g. `/features` once `features/index.html` exists)

### Docs link
- Always use `https://stablebuild.gitbook.io/ja` (never `https://docs.stablebuild.com/`)

### Header links
- Nav links (Pricing, Blog) should be **absolute** unless a Japanese version exists, in which case use relative
- "Get started" button should be **absolute** (`https://www.stablebuild.com/pricing`)
- The language switcher link should always be **absolute**, pointing to the equivalent English page on stablebuild.com (e.g. `https://www.stablebuild.com/features`)

### General rule
- Links to pages that exist locally on stablebuild.jp → **relative** (`/features`, `../company.html`, etc.)
- Links to pages that only exist on stablebuild.com → **absolute** (`https://www.stablebuild.com/pricing`)
- Language switcher → always **absolute** to stablebuild.com

### Language switcher
- index.html has an **English** link pointing to `https://www.stablebuild.com/`
- Subpages (e.g. features/) should replace the 日本語 link with an English link pointing to the equivalent English URL
- English link markup pattern (from index.html):
  ```html
  <a href="https://www.stablebuild.com/PAGE" class="link-wrapper header-link-hidde-on-tablet-copy w-inline-block" style="margin-left: 12px; margin-right: 4px;"><div class="line-rounded-icon link-icon-left"></div><div class="link-text">English</div></a>
  ```

## Adding and Translating a New Page
When scraping a new page from stablebuild.com to add to stablebuild.jp:
1. `curl -s "https://www.stablebuild.com/PAGE" -o PAGE/index.html`
2. Replace 日本語 link with English link (pointing to the English equivalent URL)
3. Add Company Profile link to the footer (between Contact and Privacy Policy), keeping it relative
4. Make all other footer links absolute (`https://www.stablebuild.com/...`), except pages that already have a JP version (use relative)
5. Make header nav links (Pricing, Blog) and Get Started button absolute, except pages with a JP version
6. Leave logo links as `/`
7. Once link structure is correct, translate all visible text to Japanese (see below)
8. Apply Katakana SEO (see below)
9. Set canonical and hreflang tags (see below)

## Translation Guidelines
Use `index.html` as the style reference for tone and phrasing.

### Canonical and hreflang
The site is served at `https://stablebuild.jp/`. Every page must have:
- A canonical pointing to its own stablebuild.jp URL (not stablebuild.com)
- `hreflang` alternate tags for language targeting

Pattern for pages that have an English equivalent on stablebuild.com:
```html
<link href="https://stablebuild.jp/PAGE" rel="canonical">
<link rel="alternate" hreflang="ja" href="https://stablebuild.jp/PAGE">
<link rel="alternate" hreflang="en" href="https://www.stablebuild.com/PAGE">
<link rel="alternate" hreflang="x-default" href="https://www.stablebuild.com/PAGE">
```

Pattern for JP-only pages (e.g. `company.html`):
```html
<link href="https://stablebuild.jp/company.html" rel="canonical">
<link rel="alternate" hreflang="ja" href="https://stablebuild.jp/company.html">
<link rel="alternate" hreflang="x-default" href="https://stablebuild.jp/company.html">
```

### Katakana SEO
Every page must include the Katakana brand name so the site is discoverable via Japanese search:
- `<title>` format: `PAGE_TITLE - ステイブルビルド (StableBuild) - サブタイトル`
- Add `<meta name="keywords" content="ステイブルビルド, StableBuild, ソフトウェア依存性, ビルドの再現性, パッケージ管理, Docker, Python, Debian, Ubuntu"/>`
- Prefix description/og:description/twitter:description with `ステイブルビルド (StableBuild) は、…`
- Footer copyright: `Copyright © ステイブルビルド all rights reserved` (no "StableBuild, Inc.")

### What to translate
- `lang="en"` → `lang="ja"` on the `<html>` tag
- `<title>` and all meta tags (description, og:title, og:description, twitter:title, twitter:description) — follow Katakana SEO format above
- Header nav link text: Docs→ドキュメント, Features→機能, Pricing→料金, Blog→ブログ, Login→ログイン, Get started→始める
- All visible h1, h2, h3, p content in the main body
- Footer nav link text stays in **English** (matching index.html)
- "Subscribe to our newsletter!" stays in **English** (matching index.html)
- Language switcher text stays as **"English"**

### Translation style
- Use natural Japanese, not literal translations (e.g. "ビルドの再現性を向上" not "決定的なビルド")
- Follow phrasing already established in index.html (e.g. ピン止め, 凍結, 依存性, ビルドの再現性)
- Use sed with sufficient context to avoid unintended replacements (e.g. target by surrounding class names)

### 表記ルール
Drop the long-vowel mark on katakana loanwords that take it optionally:

- **ユーザ** — never ユーザー (applies to compounds too: ユーザ数)

Plan names stay in English, matching the pricing page: Community / Team / Professional.

## Blog

Blog posts are written as Markdown and rendered into Webflow-styled pages. Unlike the rest
of the site, the HTML under `blog/` is generated — edit the Markdown, never the output.

```
blog/_posts/<slug>.md        source, one file per post
blog/_template/*.html        page shell and card markup
blog/build.py                the generator
blog/index.html              generated listing
blog/<slug>/index.html       generated post
```

Run `python3 blog/build.py` after any change (needs the `markdown` package), and
`python3 blog/build.py --check` to confirm the committed output is current. The generator
also rewrites the marked blog region of `sitemap.xml`.

### Front matter
```yaml
---
title: 記事のタイトル
date: 2026-05-11          # YYYY-MM-DD, drives ordering and the 2026年5月11日 byline
category: 記事
description: 一文の要約   # meta description and the excerpt on listing cards
hero: https://…           # optional; falls back to the site OG image
en_url: https://www.stablebuild.com/blog/<slug>   # omit for Japanese-original posts
featured: true            # optional, one post max; defaults to the newest
---
```

`slug` defaults to the filename — keep it identical to the English post's slug so the
hreflang pair lines up. Omitting `en_url` marks the post Japanese-only: the language
switcher falls back to the English blog index and `hreflang` follows the JP-only pattern.

### What the generator handles
- Katakana SEO: `<title>`, keywords, and a description that always carries ステイブルビルド
- Canonical, `hreflang`, `og:url`, and the `../` depth of the footer's `company.html` link
- Markdown headings, lists, links, tables (given Webflow's inline table styles) and fenced
  code blocks (given the `richtext-code-block` class the page CSS expects)
- Related posts (the two most recent others) and the listing page

Webflow's site search, category badges and pagination are dropped: they depend on
`/search` and `/blog-post-categories/*`, which only exist on stablebuild.com.

### Writing the Markdown
Translate per the Translation Guidelines below. Links follow the site's General rule, so
`/pricing`, `/blog/<slug>` and `/` stay relative, docs point at
`https://stablebuild.gitbook.io/ja`, and dashboard links carry `?lang=ja`.

## SEO Infrastructure

### sitemap.xml
Located at root. Lists all stablebuild.jp pages with hreflang alternates embedded. Update when adding a new page — add a `<url>` block following the existing pattern. Blog entries sit between the `BEGIN blog` / `END blog` markers and are rewritten by `blog/build.py` — edit them there, not by hand.

After deploying, submit `https://stablebuild.jp/sitemap.xml` to Google Search Console.

### robots.txt
Located at root. Allows all crawlers and references the sitemap. No changes needed unless a page should be excluded from indexing.

### Pages translated so far
- `features/index.html` — 機能ページ
- `pricing/index.html` — 料金ページ
- `blog/` — ブログ（stablebuild.com/blog の5記事を翻訳済み）
