# -*- coding: utf-8 -*-
"""
Crystl Labs // Blog Compiler v1.0

Single source of truth: blog_src/<slug>.json  ({title, slug, date, excerpt, content})
`content` is a Markdown subset: ## headings, tables, fenced code, bullets,
**bold**, `code`, links and images.

Emits:
  - blog/<slug>.html   one standalone, indexable article per post
  - blogs.html         the index that links to them

Run:  python build_blog.py
"""

import os
import re
import json
import glob
import html
import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT, 'blog_src')
OUT_DIR = os.path.join(ROOT, 'blog')

SITE = 'https://crystllabs.com'
AUTHOR = 'AP39'
ADSENSE = ('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
           '?client=ca-pub-8883757785147352" crossorigin="anonymous"></script>')


def esc(s):
    return html.escape(s or '', quote=True)


# ---------------------------------------------------------------------------
# Markdown subset -> HTML
#
# Deliberately small. Only the constructs the posts actually use are handled,
# so there is no silent mangling of anything else: an unrecognised line becomes
# a paragraph rather than being guessed at.
# ---------------------------------------------------------------------------
def _inline(t):
    """Inline spans. Code is extracted first so its contents are never escaped
    into markup or picked up by the bold/link passes."""
    stash = []

    def keep(m):
        stash.append(f'<code class="px-1.5 py-0.5 rounded bg-white/10 text-brandGreen/90 '
                     f'font-mono text-[0.85em]">{esc(m.group(1))}</code>')
        return f'\x00{len(stash) - 1}\x00'

    t = re.sub(r'`([^`]+)`', keep, t)
    t = esc(t)
    t = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',
               lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}" loading="lazy" '
                         f'class="rounded-xl border border-white/10 my-6 max-w-full h-auto">', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
               lambda m: f'<a href="{m.group(2)}" class="text-brandBlue hover:text-brandPink '
                         f'underline underline-offset-2 transition-colors">{m.group(1)}</a>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong class="text-white font-semibold">\1</strong>', t)
    return re.sub(r'\x00(\d+)\x00', lambda m: stash[int(m.group(1))], t)


def _table(rows):
    """A Markdown pipe table. The separator row (|---|---|) is dropped."""
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]
    body = [r for r in cells[1:] if not all(re.fullmatch(r':?-{2,}:?', c) for c in r)]
    head = ''.join(
        f'<th class="text-left font-mono text-[11px] uppercase tracking-wider '
        f'text-brandBlue/90 px-3 py-2 border-b border-white/15">{_inline(c)}</th>'
        for c in cells[0])
    trs = ''.join(
        '<tr class="border-b border-white/5 last:border-0">' + ''.join(
            f'<td class="px-3 py-2 align-top text-gray-300">{_inline(c)}</td>' for c in r
        ) + '</tr>' for r in body)
    return ('<div class="my-6 overflow-x-auto rounded-xl border border-white/10 bg-panelBg/40">'
            f'<table class="w-full text-sm border-collapse"><thead><tr>{head}</tr></thead>'
            f'<tbody>{trs}</tbody></table></div>')


def md_to_html(md):
    out, buf, i = [], [], 0
    lines = md.replace('\r\n', '\n').split('\n')

    def flush():
        if buf:
            out.append(f'<p class="my-5 leading-[1.75] text-gray-300">{_inline(" ".join(buf))}</p>')
            buf.clear()

    while i < len(lines):
        line = lines[i]

        if line.startswith('```'):
            flush()
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i])
                i += 1
            out.append('<pre class="my-6 overflow-x-auto rounded-xl border border-white/10 '
                       'bg-black/40 p-4 text-[13px] leading-relaxed"><code class="font-mono '
                       f'text-gray-300">{esc(chr(10).join(code))}</code></pre>')
            i += 1
            continue

        if line.startswith('|') and line.rstrip().endswith('|'):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append(lines[i])
                i += 1
            out.append(_table(rows))
            continue

        if re.match(r'^[-*] ', line):
            flush()
            items = []
            while i < len(lines) and re.match(r'^[-*] ', lines[i]):
                items.append(f'<li class="my-1.5">{_inline(lines[i][2:])}</li>')
                i += 1
            out.append('<ul class="my-5 pl-5 list-disc marker:text-brandPink/70 '
                       f'text-gray-300 leading-[1.7]">{"".join(items)}</ul>')
            continue

        m = re.match(r'^(#{1,4}) +(.*)', line)
        if m:
            flush()
            lvl = min(len(m.group(1)) + 1, 4)   # a post's # is the <h1>, so shift down one
            size = {2: 'text-xl md:text-2xl mt-12', 3: 'text-lg md:text-xl mt-9',
                    4: 'text-base md:text-lg mt-7'}[lvl]
            out.append(f'<h{lvl} class="{size} mb-3 font-bold text-white scroll-mt-20">'
                       f'{_inline(m.group(2))}</h{lvl}>')
            i += 1
            continue

        if re.match(r'^-{3,}\s*$', line):
            flush()
            out.append('<hr class="my-10 border-white/10">')
            i += 1
            continue

        if not line.strip():
            flush()
        else:
            buf.append(line.strip())
        i += 1

    flush()
    return '\n'.join(out)


# ---------------------------------------------------------------------------
def load_posts():
    posts = []
    for f in glob.glob(os.path.join(SRC_DIR, '*.json')):
        with open(f, 'r', encoding='utf-8') as fh:
            p = json.load(fh)
        p['words'] = len(p['content'].split())
        p['minutes'] = max(1, round(p['words'] / 220))
        p['day'] = p['date'][:10]
        p['pretty'] = datetime.date.fromisoformat(p['day']).strftime('%d %b %Y').upper()
        posts.append(p)
    posts.sort(key=lambda p: p['day'], reverse=True)
    return posts


NAV = '''
    <button onclick="toggleMenu()" class="md:hidden fixed top-3 left-3 z-50 p-2 rounded-lg bg-panelBg/90 backdrop-blur-md border border-white/10 text-gray-300 hover:text-white transition-colors shadow-lg shadow-black/30" aria-label="Toggle menu">
        <svg id="iconOpen" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/></svg>
        <svg id="iconClose" class="w-5 h-5 hidden" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
    </button>

    <nav class="bg-panelBg/70 backdrop-blur-md pl-12 pr-4 py-3 md:px-6 flex justify-between items-center border-b border-white/10 shrink-0">
        <a href="{root}index.html" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <img src="{root}crystl1.png" alt="" class="h-6 md:h-7 w-auto rounded-sm">
            <span class="font-mono text-[11px] md:text-xs text-white/90 tracking-wide uppercase">Crystl Labs</span>
        </a>
        <span class="hidden md:inline-flex items-center gap-1.5 font-mono text-[11px] text-brandGreen/90 uppercase tracking-wide">
            <span class="w-1.5 h-1.5 rounded-full bg-brandGreen animate-pulse"></span>
            <span>CONNECTED</span>
        </span>
    </nav>
'''


def sidebar(root, active):
    def item(href, label):
        on = href == active
        cls = ('flex items-center justify-between px-2.5 py-1.5 rounded-md bg-white/5 border-l-2 '
               'border-brandGreen text-white text-xs font-mono hover:bg-white/10 transition-colors'
               if on else
               'block px-2.5 py-1.5 rounded-md text-gray-500 text-xs font-mono hover:bg-white/5 '
               'hover:text-white transition-colors truncate')
        dot = ('\n                                <span class="w-1.5 h-1.5 rounded-full bg-brandGreen '
               'animate-pulse flex-shrink-0"></span>' if on else '')
        return (f'<li><a href="{root}{href}" class="{cls}">{label}{dot}</a></li>')

    links = ''.join('\n                            ' + item(h, l) for h, l in (
        ('projects.html', 'projects.html'),
        ('blogs.html', 'blogs.html'),
        ('personnel.html', 'personnel.html'),
        ('contact.html', 'contact.html'),
        ('privacy.html', 'privacy.html'),
        ('terms.html', 'terms.html'),
        ('data-deletion.html', 'data-deletion.html'),
    ))
    return f'''
        <aside id="sidebar" class="fixed md:static top-14 md:top-auto bottom-0 md:bottom-auto left-0 z-40 w-64 md:w-44 -translate-x-full md:translate-x-0 transition-transform duration-200 bg-panelBg md:bg-panelBg/40 border-r border-white/10 p-4 shrink-0 overflow-y-auto">
            <ul class="space-y-1 text-sm font-sans text-gray-400">
                <li class="text-gray-600 font-mono text-[10px] uppercase tracking-wider mb-2 flex items-center gap-2">
                    <span>&#128193;</span> <span>src_files</span>
                </li>
                <li class="ml-1">
                    <a href="{root}index.html" class="block px-2.5 py-1.5 rounded-md text-gray-500 text-xs font-mono hover:bg-white/5 hover:text-white transition-colors truncate">index.html</a>
                    <ul class="mt-1 ml-3 pl-3 border-l border-white/10 space-y-1">{links}
                    </ul>
                </li>
            </ul>
        </aside>'''


HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="dark">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="{canonical}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:type" content="{ogtype}">
    <meta property="og:url" content="{canonical}">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="icon" type="image/png" href="{root}favicon.png">
    <script src="https://cdn.tailwindcss.com"></script>
    ''' + ADSENSE + '''
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{ darkBg: '#0a0a12', panelBg: '#13131f', brandPink: '#D946EF', brandBlue: '#3B82F6', brandGreen: '#39FF14' }},
                    fontFamily: {{ mono: ['"JetBrains Mono"', 'monospace'], sans: ['Inter', 'sans-serif'] }}
                }}
            }}
        }}
    </script>
    <style>
        :root {{ color-scheme: dark; }}
        ::-webkit-scrollbar {{ width: 10px; }}
        ::-webkit-scrollbar-track {{ background: #0a0a12; }}
        ::-webkit-scrollbar-thumb {{ background: #22222f; border-radius: 999px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #D946EF; }}
        .bg-grid {{
            background-image:
                radial-gradient(circle at 15% 0%, rgba(217,70,239,0.07), transparent 40%),
                radial-gradient(circle at 85% 15%, rgba(59,130,246,0.07), transparent 40%);
        }}
    </style>
{extra_head}</head>
<body class="bg-darkBg text-gray-200 font-sans antialiased min-h-screen flex flex-col">
''' + NAV + '''
    <div class="flex flex-col md:flex-row flex-grow md:overflow-hidden relative">
        <div id="sidebarBackdrop" onclick="toggleMenu()" class="hidden md:hidden fixed top-14 inset-x-0 bottom-0 bg-black/60 z-30"></div>
{sidebar}

        <main class="flex-grow p-5 md:p-10 overflow-y-auto bg-darkBg bg-grid relative">
'''

TAIL = '''        </main>
    </div>

    <script>
        function toggleMenu() {
            document.getElementById('sidebar').classList.toggle('-translate-x-full');
            document.getElementById('sidebarBackdrop').classList.toggle('hidden');
            document.getElementById('iconOpen').classList.toggle('hidden');
            document.getElementById('iconClose').classList.toggle('hidden');
        }
    </script>
</body>
</html>
'''


def render_post(p, prev_p, next_p):
    canonical = f"{SITE}/blog/{p['slug']}.html"
    ld = json.dumps({
        '@context': 'https://schema.org',
        '@type': 'BlogPosting',
        'headline': p['title'],
        'description': p['excerpt'],
        'datePublished': p['date'],
        'author': {'@type': 'Person', 'name': AUTHOR, 'url': 'https://ap39.crystllabs.com/'},
        'publisher': {'@type': 'Organization', 'name': 'Crystl Labs',
                      'logo': {'@type': 'ImageObject', 'url': f'{SITE}/crystl1.png'}},
        'mainEntityOfPage': canonical,
        'wordCount': p['words'],
    }, ensure_ascii=False)

    head = HEAD.format(
        title=esc(p['title']) + ' | Crystl Labs',
        desc=esc(p['excerpt']),
        canonical=canonical,
        ogtype='article',
        root='../',
        sidebar=sidebar('../', 'blogs.html'),
        extra_head=f'    <script type="application/ld+json">{ld}</script>\n',
    )

    def chip(other, label, align):
        if not other:
            return '<span></span>'
        return (f'<a href="{other["slug"]}.html" class="group max-w-[48%] {align} rounded-xl border '
                f'border-white/10 bg-panelBg/50 hover:border-brandPink/40 hover:bg-panelBg px-4 py-3 '
                f'transition-all">'
                f'<span class="block font-mono text-[10px] uppercase tracking-wider text-gray-500">{label}</span>'
                f'<span class="block mt-1 text-sm text-gray-300 group-hover:text-white transition-colors">'
                f'{esc(other["title"])}</span></a>')

    return head + f'''            <article class="max-w-3xl mx-auto">
                <a href="../blogs.html" class="inline-flex items-center gap-2 mb-6 font-mono text-[11px] text-gray-500 uppercase tracking-wide hover:text-white transition-colors">&lt;- all posts</a>

                <header class="mb-8 pb-8 border-b border-white/10">
                    <div class="font-mono text-[11px] uppercase tracking-widest text-brandBlue/90 mb-3">Directive {esc(p['day'])}</div>
                    <h1 class="text-2xl md:text-4xl font-extrabold text-white leading-tight">{esc(p['title'])}</h1>
                    <p class="mt-4 text-gray-400 text-sm md:text-base leading-relaxed">{esc(p['excerpt'])}</p>
                    <div class="mt-5 flex flex-wrap items-center gap-3 font-mono text-[11px] uppercase tracking-wider text-gray-500">
                        <span class="text-brandPink/90">By {AUTHOR}</span>
                        <span class="text-white/20">/</span>
                        <time datetime="{esc(p['day'])}">{esc(p['pretty'])}</time>
                        <span class="text-white/20">/</span>
                        <span>{p['minutes']} min read</span>
                    </div>
                </header>

                <div class="text-[15px] md:text-base">
{md_to_html(p['content'])}
                </div>

                <footer class="mt-14 pt-8 border-t border-white/10">
                    <p class="text-sm text-gray-500 leading-relaxed">Written by {AUTHOR}, who builds the apps at
                        <a href="../index.html" class="text-brandBlue hover:text-brandPink underline underline-offset-2 transition-colors">Crystl Labs</a>.
                        Numbers in these posts come from runs that were actually made, not from memory. Corrections go to
                        <a href="../contact.html" class="text-brandBlue hover:text-brandPink underline underline-offset-2 transition-colors">contact</a>.</p>
                    <nav class="mt-8 flex justify-between gap-4">{chip(next_p, 'Newer', 'text-left')}{chip(prev_p, 'Older', 'text-right ml-auto')}</nav>
                </footer>
            </article>
''' + TAIL


def render_index(posts):
    head = HEAD.format(
        title='Blog | Crystl Labs',
        desc='Engineering write-ups from Crystl Labs: framework overhead, quantum optimisation, '
             'simulation design and the numbers behind them.',
        canonical=f'{SITE}/blogs.html',
        ogtype='website',
        root='',
        sidebar=sidebar('', 'blogs.html'),
        extra_head='',
    )
    cards = ''.join(f'''
                    <a href="blog/{p['slug']}.html" class="group block rounded-2xl border border-white/10 bg-panelBg/60 hover:bg-panelBg hover:border-brandPink/40 p-5 md:p-6 shadow-lg shadow-black/20 transition-all">
                        <div class="font-mono text-[10px] uppercase tracking-widest text-brandBlue/90 mb-2">Directive {esc(p['day'])} / {p['minutes']} min</div>
                        <h2 class="text-lg md:text-xl font-bold text-white leading-snug group-hover:text-brandPink transition-colors">{esc(p['title'])}</h2>
                        <p class="mt-2.5 text-sm text-gray-400 leading-relaxed">{esc(p['excerpt'])}</p>
                        <span class="mt-4 inline-block font-mono text-[10px] uppercase tracking-wider text-gray-500 group-hover:text-white transition-colors">Read on -&gt;</span>
                    </a>''' for p in posts)

    return head + f'''            <div class="max-w-3xl mx-auto">
                <header class="mb-8">
                    <h1 class="text-3xl md:text-5xl font-extrabold text-white">Blog</h1>
                    <p class="mt-3 text-gray-400 text-sm md:text-base leading-relaxed">Engineering write-ups from the Crystl Labs workbench: what we measured, what it cost, and what we changed because of it. {len(posts)} posts.</p>
                </header>

                <div class="grid gap-4">{cards}
                </div>
            </div>
''' + TAIL


def seed_home_writing(posts):
    """Put the three newest posts on the home page.

    Without this the only route from the home page to an article is the sidebar,
    which is both bad for a reader and bad for a crawler working out what the
    site is mostly about. Written between markers so it can be regenerated.
    """
    path = os.path.join(ROOT, 'index.html')
    if not os.path.exists(path):
        print('[BLOG] skip index.html (not found)')
        return
    with open(path, encoding='utf-8') as f:
        text = f.read()

    cards = ''.join(f'''
                        <a href="blog/{p['slug']}.html" class="group rounded-2xl border border-white/10 bg-panelBg/60 hover:bg-panelBg hover:border-brandPink/40 p-5 md:p-6 shadow-lg shadow-black/20 transition-all block">
                            <div class="font-mono text-[10px] uppercase tracking-widest text-brandBlue/90 mb-2">{esc(p['day'])} / {p['minutes']} min</div>
                            <h3 class="text-base md:text-lg font-bold text-white leading-snug group-hover:text-brandPink transition-colors">{esc(p['title'])}</h3>
                            <p class="mt-2 text-sm text-gray-400 leading-relaxed">{esc(p['excerpt'][:150])}{'&hellip;' if len(p['excerpt']) > 150 else ''}</p>
                        </a>''' for p in posts[:3])

    block = f'''<!-- prerender:homeWriting -->
                <section class="mt-12 md:mt-16">
                    <div class="flex items-baseline justify-between mb-4 md:mb-5">
                        <h2 class="font-mono text-[11px] md:text-xs text-brandBlue uppercase tracking-widest">Writing //</h2>
                        <a href="blogs.html" class="font-mono text-[11px] text-gray-500 hover:text-white transition-colors">View all -&gt;</a>
                    </div>
                    <p class="text-sm text-gray-400 leading-relaxed mb-5 max-w-2xl">Engineering write-ups from the workbench: what we measured, what it cost, and what changed because of it. {len(posts)} posts.</p>
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">{cards}
                    </div>
                </section>
                <!-- /prerender:homeWriting -->'''

    marked = re.compile(r'<!-- prerender:homeWriting -->.*?<!-- /prerender:homeWriting -->', re.S)
    if marked.search(text):
        new = marked.sub(lambda _: block, text, count=1)
    else:
        anchor = '\n            </div>\n        </main>'
        if anchor not in text:
            print('[BLOG] warn index.html: no anchor for the writing block')
            return
        new = text.replace(anchor, '\n\n                ' + block + anchor, 1)

    if new != text:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(new)
        print('[BLOG] index.html writing block refreshed')
    else:
        print('[BLOG] index.html unchanged')


def main():
    posts = load_posts()
    os.makedirs(OUT_DIR, exist_ok=True)
    for n, p in enumerate(posts):
        prev_p = posts[n + 1] if n + 1 < len(posts) else None
        next_p = posts[n - 1] if n else None
        out = os.path.join(OUT_DIR, f"{p['slug']}.html")
        with open(out, 'w', encoding='utf-8', newline='') as f:
            f.write(render_post(p, prev_p, next_p))
        print(f"[BLOG] post  -> blog/{p['slug']}.html  ({p['words']} words)")

    with open(os.path.join(ROOT, 'blogs.html'), 'w', encoding='utf-8', newline='') as f:
        f.write(render_index(posts))
    print(f'[BLOG] index -> blogs.html ({len(posts)} posts, '
          f'{sum(p["words"] for p in posts)} words total)')
    seed_home_writing(posts)
    return posts


if __name__ == '__main__':
    main()
