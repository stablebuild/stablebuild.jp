#!/usr/bin/env python3
"""Render the Japanese blog: blog/_posts/*.md -> blog/index.html + blog/<slug>/index.html.

    python3 blog/build.py            # write the pages and refresh sitemap.xml
    python3 blog/build.py --check    # fail if anything is out of date

Requires the `markdown` package.
"""

import argparse
import datetime
import html
import itertools
import pathlib
import re
import sys

try:
    import markdown
except ImportError:
    sys.exit('blog/build.py needs the markdown package: python3 -m pip install markdown')

BLOG = pathlib.Path(__file__).resolve().parent
SITE = BLOG.parent
TEMPLATES = BLOG / '_template'
SOURCES = BLOG / '_posts'
SITEMAP = SITE / 'sitemap.xml'

BASE = 'https://stablebuild.jp'
EN_BASE = 'https://www.stablebuild.com'
BRAND = 'ステイブルビルド (StableBuild)'
DEFAULT_OG_IMAGE = f'{BASE}/og-image.jpg'
INDEX_TITLE = f'ブログ - {BRAND} - ソフトウェア依存性を凍結・固定'
INDEX_DESCRIPTION = (f'{BRAND} は、Docker、Python、Debian、Ubuntu、カスタムリポジトリ全体で'
                     '過去および現在のソフトウェアパッケージを維持し、'
                     'ソフトウェアが常にビルドできることを保証します。')

# Webflow's rich text does not style tables, so the English posts carry these
# inline styles. Markdown tables get the same treatment for a consistent look.
TABLE_STYLES = {
    'table': 'width: 100%; border-collapse: collapse; text-align: left; font-family: inherit;'
             ' margin-bottom: 24px',
    'thead_tr': 'border-bottom: 2px solid #e2e8f0',
    'th': 'padding: 12px 16px; font-weight: 600',
    'tr': 'border-bottom: 1px solid #edf2f7',
    'td': 'padding: 12px 16px',
    'label_cell': 'white-space: nowrap',
}

REQUIRED = ('title', 'date', 'description')


def die(msg):
    sys.exit(f'blog/build.py: {msg}')


def read_template(name):
    return (TEMPLATES / name).read_text(encoding='utf-8')


def fill(template, **values):
    """Substitute {{KEY}} placeholders in one pass, so values are never rescanned."""
    def replace(match):
        key = match.group(1)
        if key not in values:
            die(f'template placeholder {{{{{key}}}}} has no value')
        return values[key]
    return re.sub(r'\{\{(\w+)\}\}', replace, template)


def parse_front_matter(text, path):
    if not text.startswith('---\n'):
        die(f'{path.name} must start with a --- front matter block')
    _, raw, body = text.split('---\n', 2)
    meta = {}
    for lineno, line in enumerate(raw.splitlines(), start=2):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if ':' not in line:
            die(f'{path.name}:{lineno}: expected "key: value"')
        key, value = line.split(':', 1)
        meta[key.strip()] = value.strip()
    missing = [k for k in REQUIRED if not meta.get(k)]
    if missing:
        die(f'{path.name}: front matter is missing {", ".join(missing)}')
    return meta, body.lstrip('\n')


def jp_date(date):
    return f'{date.year}年{date.month}月{date.day}日'


def style_tables(body):
    """Add the inline table styles Webflow's rich text expects.

    The first column carries the row label, so it is kept on one line: Japanese
    breaks between any two characters, which otherwise splits コンテナイメージ
    across lines and squeezes the column to almost nothing.
    """
    body = body.replace('<table>', f'<table style="{TABLE_STYLES["table"]}">')

    def row(match):
        column = itertools.count()

        def cell(m):
            tag, attrs = m.group(1), m.group(2)
            style = TABLE_STYLES[tag]
            if next(column) == 0:
                style += f'; {TABLE_STYLES["label_cell"]}'
            # an alignment row in the Markdown puts the column alignment on the cell
            align = re.search(r'align="([a-z]+)"|text-align:\s*([a-z]+)', attrs)
            if align:
                style += f'; text-align: {align.group(1) or align.group(2)}'
            return f'<{tag} style="{style}">'
        return re.sub(r'<(th|td)\b([^>]*)>', cell, match.group(0))
    body = re.sub(r'<tr>.*?</tr>', row, body, flags=re.S)

    def head(match):
        return match.group(0).replace('<tr>', f'<tr style="{TABLE_STYLES["thead_tr"]}">')
    body = re.sub(r'<thead>.*?</thead>', head, body, flags=re.S)

    def rows(match):
        block = match.group(0).replace('<tr>', f'<tr style="{TABLE_STYLES["tr"]}">')
        # the final row needs no separator below it
        i = block.rfind(f'<tr style="{TABLE_STYLES["tr"]}">')
        return block[:i] + '<tr>' + block[i + len(f'<tr style="{TABLE_STYLES["tr"]}">'):] if i != -1 else block
    return re.sub(r'<tbody>.*?</tbody>', rows, body, flags=re.S)


def render_body(source):
    body = markdown.markdown(source, extensions=['tables', 'fenced_code', 'sane_lists'])
    # match the code block styling already defined in the page's <style> block
    body = re.sub(r'<pre>(\s*<code)', r'<pre class="richtext-code-block">\1', body)
    return style_tables(body)


def load_posts():
    if not SOURCES.is_dir():
        die(f'no {SOURCES.relative_to(SITE)} directory')
    posts = []
    for path in sorted(SOURCES.glob('*.md')):
        meta, source = parse_front_matter(path.read_text(encoding='utf-8'), path)
        try:
            date = datetime.date.fromisoformat(meta['date'])
        except ValueError:
            die(f'{path.name}: date must be YYYY-MM-DD, got {meta["date"]!r}')
        slug = meta.get('slug') or path.stem
        posts.append({
            'slug': slug,
            'title': meta['title'],
            'date': date,
            'category': meta.get('category', '記事'),
            'description': meta['description'],
            'hero': meta.get('hero', ''),
            'en_url': meta.get('en_url', ''),
            'featured': meta.get('featured', '').lower() == 'true',
            'url': f'/blog/{slug}',
            'body': render_body(source),
        })
    if not posts:
        die(f'no posts found in {SOURCES.relative_to(SITE)}')
    duplicates = {p['slug'] for p in posts if sum(q['slug'] == p['slug'] for q in posts) > 1}
    if duplicates:
        die(f'duplicate slugs: {", ".join(sorted(duplicates))}')
    featured = [p for p in posts if p['featured']]
    if len(featured) > 1:
        die(f'more than one post marked featured: {", ".join(p["slug"] for p in featured)}')
    posts.sort(key=lambda p: (p['date'], p['slug']), reverse=True)
    return posts


def meta_description(post):
    """Keep the katakana brand name in every description, for Japanese search."""
    if 'ステイブルビルド' in post['description']:
        return post['description']
    return f'{BRAND} ブログ｜{post["description"]}'


def head_links(path, en_url):
    """Canonical plus hreflang alternates for one page."""
    lines = [f'<link href="{BASE}{path}" rel="canonical"/>',
             f'<link rel="alternate" hreflang="ja" href="{BASE}{path}"/>']
    if en_url:
        lines.append(f'<link rel="alternate" hreflang="en" href="{en_url}"/>')
        lines.append(f'<link rel="alternate" hreflang="x-default" href="{en_url}"/>')
    else:
        # Japanese-original post: no English equivalent to point at
        lines.append(f'<link rel="alternate" hreflang="x-default" href="{BASE}{path}"/>')
    return '\n'.join(lines)


def render_card(template, post):
    excerpt = (f'<p class="blog-card-excerpt mg-bottom-24px">{html.escape(post["description"])}</p>'
               if post['description'] else '')
    return fill(template,
                URL=post['url'],
                IMAGE=post['hero'] or DEFAULT_OG_IMAGE,
                TITLE=html.escape(post['title']),
                CATEGORY=html.escape(post['category']),
                EXCERPT=excerpt,
                DATE=jp_date(post['date']))


def render_post(post, others):
    hero = ('<div class="inner-container _976px center">'
            f'<img src="{post["hero"]}" alt="{html.escape(post["title"])}" '
            'class="border-radius-24px width-100"/></div>') if post['hero'] else ''
    card = read_template('card-related.html')
    related = ''
    if others:
        related = fill(read_template('related.html'),
                       RELATED_CARDS=''.join(render_card(card, p) for p in others[:2]))
    return fill(read_template('post.html'),
                WF_PAGE='6558cb02ceb72f12e74052e5',
                TITLE=html.escape(f'{post["title"]} - {BRAND} - ブログ'),
                DESCRIPTION=html.escape(meta_description(post)),
                OG_IMAGE=post['hero'] or DEFAULT_OG_IMAGE,
                OG_URL=f'{BASE}{post["url"]}',
                HEAD_LINKS=head_links(post['url'], post['en_url']),
                EN_URL=post['en_url'] or f'{EN_BASE}/blog',
                COMPANY_URL='../../company.html',
                CATEGORY=html.escape(post['category']),
                DATE=jp_date(post['date']),
                POST_TITLE=html.escape(post['title']),
                HERO=hero,
                BODY=post['body'],
                RELATED=related)


def render_index(posts):
    featured = next((p for p in posts if p['featured']), posts[0])
    rest = [p for p in posts if p is not featured]
    return fill(read_template('index.html'),
                WF_PAGE='6558cb02ceb72f12e74052da',
                TITLE=html.escape(INDEX_TITLE),
                DESCRIPTION=html.escape(INDEX_DESCRIPTION),
                OG_IMAGE=DEFAULT_OG_IMAGE,
                OG_URL=f'{BASE}/blog',
                HEAD_LINKS=head_links('/blog', f'{EN_BASE}/blog'),
                EN_URL=f'{EN_BASE}/blog',
                COMPANY_URL='../company.html',
                FEATURED=render_card(read_template('card-featured.html'), featured),
                POSTS=''.join(render_card(read_template('card-list.html'), p) for p in rest))


def sitemap_entries(posts):
    blocks = []
    for path, en_url, freq, priority in (
            [('/blog', f'{EN_BASE}/blog', 'weekly', '0.8')]
            + [(p['url'], p['en_url'], 'yearly', '0.6') for p in posts]):
        lines = [f'    <loc>{BASE}{path}</loc>',
                 f'    <xhtml:link rel="alternate" hreflang="ja" href="{BASE}{path}"/>']
        if en_url:
            lines.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{en_url}"/>')
            lines.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{en_url}"/>')
        else:
            lines.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{BASE}{path}"/>')
        lines += [f'    <changefreq>{freq}</changefreq>', f'    <priority>{priority}</priority>']
        blocks.append('  <url>\n' + '\n'.join(lines) + '\n  </url>')
    return '\n\n'.join(blocks)


BEGIN = '  <!-- BEGIN blog: generated by blog/build.py -->'
END = '  <!-- END blog -->'


def render_sitemap(posts):
    text = SITEMAP.read_text(encoding='utf-8')
    if BEGIN not in text or END not in text:
        die(f'sitemap.xml needs the "{BEGIN.strip()}" / "{END.strip()}" markers')
    head, rest = text.split(BEGIN, 1)
    _, foot = rest.split(END, 1)
    return f'{head}{BEGIN}\n{sitemap_entries(posts)}\n{END}{foot}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='report stale output instead of writing it')
    args = parser.parse_args()

    posts = load_posts()
    outputs = {BLOG / 'index.html': render_index(posts), SITEMAP: render_sitemap(posts)}
    for post in posts:
        others = [p for p in posts if p is not post]
        outputs[BLOG / post['slug'] / 'index.html'] = render_post(post, others)

    stale = [p for p, text in outputs.items()
             if not p.exists() or p.read_text(encoding='utf-8') != text]
    if args.check:
        for path in sorted(stale):
            print(f'out of date: {path.relative_to(SITE)}')
        if stale:
            sys.exit('blog/build.py --check failed; run python3 blog/build.py')
        print(f'{len(posts)} posts, all output up to date')
        return

    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
    for path in sorted(outputs):
        print(f'{"wrote" if path in stale else "  ok "} {path.relative_to(SITE)}')
    print(f'{len(posts)} posts')


if __name__ == '__main__':
    main()
