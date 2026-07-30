# -*- coding: utf-8 -*-
"""
Crystl Labs // App Page Compiler v1.0
Author: Crystl Labs Senior Dev
Year: 2026

Single source of truth: apps_data.json
Emits:
  - apps/<slug>.html      one standalone, indexable, trilingual page per app
  - apps/apps.data.js     window.CRYSTL_APPS array consumed by projects.html
                          (drives the grid + modal, "both pages + popup")

Run:  python build_apps.py
"""

import os
import re
import json
import html

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(ROOT, 'apps_data.json')
APPS_DIR = os.path.join(ROOT, 'apps')

LANGS = ('en', 'ko', 'ja')


def esc(s):
    return html.escape(s or '', quote=True)


def play_svg(cls='w-4 h-4'):
    return (f'<svg class="{cls}" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">'
            '<path d="M3.6 2.3c-.3.3-.5.7-.5 1.2v16.9c0 .5.2.9.5 1.2l9.3-9.6-9.3-9.7zm12.9 6.1L6.1 2.5'
            'l8.8 9.1 1.6-1.6zm3.7 2.2l-2.9-1.7-1.9 1.9 1.9 1.9 2.9-1.7c.6-.3.6-1.4 0-1.7zM6.1 21.5'
            'l10.4-5.9-1.6-1.6-8.8 9.1z"/></svg>')


def load_apps():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    apps = data['apps']
    for a in apps:
        a.setdefault('platform', 'Android')
        # icon lives at apps/<slug>.png; page sits inside apps/ so it references bare filename
        a.setdefault('icon', f"{a['slug']}.png")
        # 'Live' unlocks the store button, the Live badge and the screenshot strip.
        # Anything else (or absent) keeps the old "In development" placeholder.
        a.setdefault('status', 'In development')
        a.setdefault('storeUrl', '')
        # paths are relative to apps/, same convention as icon
        a.setdefault('screenshots', [])
    return apps


def is_live(app):
    return app.get('status') == 'Live' and bool(app.get('storeUrl'))


# ---------------------------------------------------------------------------
# Standalone per-app page
# ---------------------------------------------------------------------------
def render_page(app):
    slug = app['slug']
    tier = app.get('tier', 'Volume')
    tier_accent = 'brandPink' if tier == 'Flagship' else 'brandBlue'
    # JS payload for in-page language switching
    payload = json.dumps({
        'name': app['name'], 'tagline': app['tagline'], 'desc': app['desc']
    }, ensure_ascii=False)

    name_en = esc(app['name']['en'])
    tagline_en = esc(app['tagline']['en'])
    desc_en = esc(app['desc']['en'])

    live = is_live(app)
    store_url = esc(app.get('storeUrl', ''))

    # Live badge next to Platform / Tier
    live_badge = ('\n                            <span class="font-mono text-[10px] uppercase tracking-wider '
                  'text-brandGreen border border-brandGreen/40 bg-brandGreen/10 rounded px-1.5 py-0.5">Live'
                  '</span>') if live else ''

    # Store button: a real anchor once the app ships, the old dead chip until then
    if live:
        store_block = f'''<a id="apStoreLink" href="{store_url}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-2 rounded-xl bg-brandGreen/10 border border-brandGreen/40 px-4 py-3 text-brandGreen font-mono text-xs uppercase tracking-wide hover:bg-brandGreen/20 transition-colors">
                    {play_svg()}
                    <span id="apStore">Get it on Google Play</span>
                </a>'''
    else:
        store_block = f'''<div class="inline-flex items-center gap-2 rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-gray-400 font-mono text-xs uppercase tracking-wide cursor-default select-none">
                    {play_svg('w-4 h-4 text-brandGreen/80')}
                    <span id="apStore">In development</span>
                </div>'''

    store_labels = ({'en': 'Get it on Google Play', 'ko': 'Google Play에서 받기', 'ja': 'Google Play で入手'}
                    if live else
                    {'en': 'In development', 'ko': '개발 중', 'ja': '開発中'})
    shots_labels = {'en': 'Screenshots //', 'ko': '스크린샷 //', 'ja': 'スクリーンショット //'}
    store_str = json.dumps({lang: {'store': store_labels[lang], 'shots': shots_labels[lang]}
                            for lang in LANGS}, ensure_ascii=False)

    shots = app.get('screenshots') or []
    if shots:
        tiles = ''.join(f'''
                        <img src="{esc(s)}" alt="{name_en} screenshot {n}" loading="lazy" width="270" height="579" class="snap-start shrink-0 w-40 md:w-48 rounded-xl border border-white/10 shadow-lg shadow-black/30">'''
                        for n, s in enumerate(shots, 1))
        shots_block = f'''

                <section class="mt-10">
                    <h2 id="apShotsHead" class="font-mono text-[11px] md:text-xs text-brandBlue uppercase tracking-widest mb-4">Screenshots //</h2>
                    <div class="flex gap-3 md:gap-4 overflow-x-auto snap-x no-scrollbar pb-2">{tiles}
                    </div>
                </section>'''
    else:
        shots_block = ''

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name_en} | Crystl Labs</title>
    <meta name="description" content="{tagline_en}">
    <meta property="og:title" content="{name_en} | Crystl Labs">
    <meta property="og:description" content="{tagline_en}">
    <meta property="og:image" content="{esc(app['icon'])}">
    <meta property="og:type" content="website">
    <link rel="canonical" href="https://crystllabs.com/apps/{slug}.html">
    <link rel="icon" type="image/png" href="../favicon.png">
    <script src="https://cdn.tailwindcss.com"></script>
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
        ::-webkit-scrollbar {{ width: 10px; }}
        ::-webkit-scrollbar-track {{ background: #0a0a12; }}
        ::-webkit-scrollbar-thumb {{ background: #22222f; border-radius: 999px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #D946EF; }}
        .bg-grid {{
            background-image:
                radial-gradient(circle at 15% 0%, rgba(217,70,239,0.07), transparent 40%),
                radial-gradient(circle at 85% 15%, rgba(59,130,246,0.07), transparent 40%);
        }}
        .no-scrollbar {{ -ms-overflow-style: none; scrollbar-width: none; }}
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
    </style>
</head>
<body class="bg-darkBg text-gray-200 font-sans antialiased min-h-screen flex flex-col">

    <button onclick="toggleMenu()" class="md:hidden fixed top-3 left-3 z-50 p-2 rounded-lg bg-panelBg/90 backdrop-blur-md border border-white/10 text-gray-300 hover:text-white transition-colors shadow-lg shadow-black/30" aria-label="Toggle menu">
        <svg id="iconOpen" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/></svg>
        <svg id="iconClose" class="w-5 h-5 hidden" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
    </button>

    <nav class="bg-panelBg/70 backdrop-blur-md pl-12 pr-4 py-3 md:px-6 flex justify-between items-center border-b border-white/10 shrink-0">
        <div class="flex items-center gap-3">
            <a href="../index.html" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
                <img src="../crystl1.png" alt="" class="h-6 md:h-7 w-auto rounded-sm">
                <span class="font-mono text-[11px] md:text-xs text-white/90 tracking-wide uppercase">Crystl Labs</span>
            </a>
        </div>
        <div class="flex items-center gap-3 md:gap-6 font-mono text-[11px] text-gray-500 uppercase tracking-wide">
            <span class="hidden md:inline-flex items-center gap-1.5 text-brandGreen/90">
                <span class="w-1.5 h-1.5 rounded-full bg-brandGreen animate-pulse"></span>
                <span>CONNECTED</span>
            </span>
            <select id="langSelect" onchange="switchLang(this.value)" class="bg-white/5 text-gray-300 px-2 py-1.5 rounded-md outline-none border border-white/10 cursor-pointer text-[11px] hover:border-white/20 transition-colors">
                <option value="en">EN</option>
                <option value="ko">KR</option>
                <option value="ja">JP</option>
            </select>
        </div>
    </nav>

    <div class="flex flex-col md:flex-row flex-grow md:overflow-hidden relative">
        <div id="sidebarBackdrop" onclick="toggleMenu()" class="hidden md:hidden fixed top-14 inset-x-0 bottom-0 bg-black/60 z-30"></div>

        <aside id="sidebar" class="fixed md:static top-14 md:top-auto bottom-0 md:bottom-auto left-0 z-40 w-64 md:w-44 -translate-x-full md:translate-x-0 transition-transform duration-200 bg-panelBg md:bg-panelBg/40 border-r border-white/10 p-4 shrink-0 overflow-y-auto">
            <ul class="space-y-1 text-sm font-sans text-gray-400">
                <li class="text-gray-600 font-mono text-[10px] uppercase tracking-wider mb-2 flex items-center gap-2">
                    <span>📁</span> <span>src_files</span>
                </li>
                <li class="ml-1">
                    <a href="../index.html" class="block px-2.5 py-1.5 rounded-md text-gray-500 text-xs font-mono hover:bg-white/5 hover:text-white transition-colors truncate">index.html</a>
                    <ul class="mt-1 ml-3 pl-3 border-l border-white/10 space-y-1">
                        <li>
                            <a href="../projects.html" class="flex items-center justify-between px-2.5 py-1.5 rounded-md bg-white/5 border-l-2 border-brandGreen text-white text-xs font-mono hover:bg-white/10 transition-colors">
                                projects.html
                                <span class="w-1.5 h-1.5 rounded-full bg-brandGreen animate-pulse flex-shrink-0"></span>
                            </a>
                        </li>
                        <li><a href="../blogs.html" class="block px-2.5 py-1.5 rounded-md text-gray-500 text-xs font-mono hover:bg-white/5 hover:text-white transition-colors truncate">blogs.html</a></li>
                        <li><a href="../personnel.html" class="block px-2.5 py-1.5 rounded-md text-gray-500 text-xs font-mono hover:bg-white/5 hover:text-white transition-colors truncate">personnel.html</a></li>
                        <li><a href="../privacy.html" class="block px-2.5 py-1.5 rounded-md text-gray-500 text-xs font-mono hover:bg-white/5 hover:text-white transition-colors truncate">privacy.html</a></li>
                        <li><a href="../terms.html" class="block px-2.5 py-1.5 rounded-md text-gray-500 text-xs font-mono hover:bg-white/5 hover:text-white transition-colors truncate">terms.html</a></li>
                        <li><a href="../data-deletion.html" class="block px-2.5 py-1.5 rounded-md text-gray-500 text-xs font-mono hover:bg-white/5 hover:text-white transition-colors truncate">data-deletion.html</a></li>
                    </ul>
                </li>
            </ul>
        </aside>

        <main class="flex-grow p-5 md:p-10 overflow-y-auto bg-darkBg bg-grid relative">
            <div class="max-w-3xl mx-auto">
                <a href="../projects.html" class="inline-flex items-center gap-2 mb-6 font-mono text-[11px] text-gray-500 uppercase tracking-wide hover:text-white transition-colors">&lt;- all projects</a>

                <header class="flex items-center gap-5 mb-6">
                    <img id="apIcon" src="{esc(app['icon'])}" alt="{name_en}" class="w-20 h-20 md:w-28 md:h-28 rounded-2xl border border-white/10 shadow-lg shadow-black/30 shrink-0">
                    <div>
                        <h1 id="apName" class="text-2xl md:text-4xl font-extrabold text-white leading-tight">{name_en}</h1>
                        <div class="flex flex-wrap items-center gap-2 mt-2">
                            <span class="font-mono text-[10px] uppercase tracking-wider text-brandGreen/90 border border-brandGreen/30 rounded px-1.5 py-0.5">{esc(app['platform'])}</span>
                            <span class="font-mono text-[10px] uppercase tracking-wider text-{tier_accent}/90 border border-{tier_accent}/30 rounded px-1.5 py-0.5">{esc(tier)}</span>{live_badge}
                        </div>
                    </div>
                </header>

                <p id="apTagline" class="text-brandPink/90 text-base md:text-lg font-medium mb-6">{tagline_en}</p>

                <p id="apDesc" class="text-gray-300 text-sm md:text-[15px] leading-relaxed mb-8 max-w-2xl">{desc_en}</p>

                {store_block}{shots_block}
            </div>
        </main>
    </div>

    <script>
        const APP = {payload};
        const STR = {store_str};
        function currentLang() {{
            const l = localStorage.getItem('crystl_lang') || 'ko';
            return ['en','ko','ja'].includes(l) ? l : 'ko';
        }}
        function switchLang(lang) {{
            if (!['en','ko','ja'].includes(lang)) lang = 'ko';
            localStorage.setItem('crystl_lang', lang);
            document.getElementById('langSelect').value = lang;
            document.getElementById('apName').textContent = APP.name[lang];
            document.getElementById('apTagline').textContent = APP.tagline[lang];
            document.getElementById('apDesc').textContent = APP.desc[lang];
            document.getElementById('apStore').textContent = STR[lang].store;
            const shotsHead = document.getElementById('apShotsHead');
            if (shotsHead) shotsHead.textContent = STR[lang].shots;
            document.documentElement.lang = lang;
        }}
        function toggleMenu() {{
            document.getElementById('sidebar').classList.toggle('-translate-x-full');
            document.getElementById('sidebarBackdrop').classList.toggle('hidden');
            document.getElementById('iconOpen').classList.toggle('hidden');
            document.getElementById('iconClose').classList.toggle('hidden');
        }}
        window.onload = () => switchLang(currentLang());
    </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Data file consumed by projects.html (grid + modal)
# ---------------------------------------------------------------------------
def render_data_js(apps):
    slim = [{
        'id': a['slug'],
        'slug': a['slug'],
        'icon': f"apps/{a['slug']}.png",
        'page': f"apps/{a['slug']}.html",
        'tier': a.get('tier', 'Volume'),
        'platform': a.get('platform', 'Android'),
        'name': a['name'],
        'tagline': a['tagline'],
        'desc': a['desc'],
        'status': a.get('status', 'In development'),
        'storeUrl': a.get('storeUrl', ''),
        # root-relative here, because index.html/projects.html sit at the site root
        'screenshots': [f"apps/{s}" for s in (a.get('screenshots') or [])],
    } for a in apps]
    body = json.dumps(slim, ensure_ascii=False, indent=4)
    return "// AUTO-GENERATED by build_apps.py — do not edit by hand.\n" \
           "window.CRYSTL_APPS = " + body + ";\n"


# ---------------------------------------------------------------------------
# Static seed markup for the JS-rendered carousels/grids
#
# index.html and projects.html ship those containers empty and fill them from
# apps.data.js at runtime, so a crawler that does not execute JS sees no
# projects and no links to the per-app pages. That is what AdSense rejected the
# site for. We seed the containers with equivalent static markup between
# marker comments; renderApps()/renderGrid() still overwrite them on load, so
# the browser experience is unchanged. Anchors (not buttons) so the per-app
# pages are reachable without JS.
# ---------------------------------------------------------------------------
def _seed(html_text, container_id, inner):
    """Replace the contents of <div id="container_id"> between prerender markers."""
    start = f'<!-- prerender:{container_id} -->'
    end = f'<!-- /prerender:{container_id} -->'
    block = f'{start}{inner}\n                    {end}'

    marked = re.compile(re.escape(start) + r'.*?' + re.escape(end), re.S)
    if marked.search(html_text):
        return marked.sub(lambda _: block, html_text, count=1)

    empty = re.compile(r'(<div id="' + re.escape(container_id) + r'"[^>]*>)(\s*)(</div>)')
    if not empty.search(html_text):
        return None
    return empty.sub(lambda m: m.group(1) + block + m.group(3), html_text, count=1)


def _app_cards(apps, layout):
    out = []
    for a in apps:
        name = esc(a['name']['en'])
        href = f"apps/{a['slug']}.html"
        icon = f"apps/{a['slug']}.png"
        badge = ('<span class="mt-2 inline-block font-mono text-[10px] uppercase tracking-wider '
                 'text-brandGreen border border-brandGreen/40 bg-brandGreen/10 rounded px-1.5 py-0.5">Live</span>'
                 if is_live(a) else '')
        badge_carousel = f'\n                            {badge}' if badge else ''
        badge_grid = f'\n                            {badge}' if badge else ''
        if layout == 'carousel':
            out.append(f'''
                        <a href="{href}" class="group snap-start shrink-0 w-64 md:w-72 text-left rounded-2xl border border-white/10 bg-panelBg/60 hover:bg-panelBg hover:border-brandPink/40 p-5 md:p-6 shadow-lg shadow-black/20 transition-all block">
                            <div class="flex items-center gap-4 mb-4">
                                <img src="{icon}" alt="" class="w-14 h-14 md:w-16 md:h-16 rounded-2xl border border-white/10 shadow-md shadow-black/30 shrink-0">
                                <h3 class="text-base md:text-lg font-bold text-white leading-tight">{name}</h3>
                            </div>
                            <p class="text-sm text-gray-400 leading-relaxed">{esc(a['tagline']['en'])}</p>{badge_carousel}
                        </a>''')
        else:
            out.append(f'''
                        <a href="{href}" class="group text-center rounded-2xl border border-white/10 bg-panelBg/60 hover:bg-panelBg hover:border-brandPink/40 p-4 md:p-5 shadow-lg shadow-black/20 transition-all flex flex-col items-center">
                            <img src="{icon}" alt="" class="w-20 h-20 md:w-24 md:h-24 rounded-2xl border border-white/10 shadow-md shadow-black/30 mb-3">
                            <h3 class="text-sm md:text-base font-bold text-white leading-tight">{name}</h3>
                            <p class="mt-1.5 text-xs text-gray-400 leading-snug">{esc(a['tagline']['en'])}</p>{badge_grid}
                        </a>''')
    return ''.join(out)


def _heat_cards(html_text):
    """Mirror the heatProjects array declared inline on the page."""
    m = re.search(r'const heatProjects\s*=\s*\[(.*?)\];', html_text, re.S)
    if not m:
        return ''
    out = []
    for entry in re.finditer(r'\{([^}]*)\}', m.group(1)):
        src = entry.group(1)
        name = re.search(r'name\s*:\s*"([^"]*)"', src)
        tag = re.search(r'tag\s*:\s*"([^"]*)"', src)
        if not name:
            continue
        name = name.group(1)
        initial = name.replace('Project ', '')[:1]
        tag_html = f'\n                            <p class="mt-0.5 text-xs md:text-sm text-gray-400">{esc(tag.group(1))}</p>' if tag else ''
        out.append(f'''
                        <div class="group rounded-2xl border border-brandBlue/30 bg-gradient-to-br from-brandBlue/10 via-panelBg/60 to-brandPink/5 p-5 md:p-6 shadow-lg shadow-black/20 flex items-center gap-4">
                            <div class="w-14 h-14 md:w-16 md:h-16 shrink-0 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-xl md:text-2xl font-extrabold text-gradient">{esc(initial)}</div>
                            <div>
                                <h3 class="text-base md:text-lg font-bold text-white leading-tight">{esc(name)}</h3>{tag_html}
                                <span class="mt-1.5 inline-block font-mono text-[10px] uppercase tracking-wider text-brandBlue/90 border border-brandBlue/30 rounded px-1.5 py-0.5">Prerelease</span>
                            </div>
                        </div>''')
    return ''.join(out)


def _site_cards(html_text):
    """Mirror the siteProjects array declared inline on the page."""
    m = re.search(r'const siteProjects\s*=\s*\[(.*?)\];', html_text, re.S)
    if not m:
        return ''
    out = []
    for entry in re.finditer(r'\{([^}]*)\}', m.group(1)):
        src = entry.group(1)
        fields = {k: re.search(k + r'\s*:\s*"([^"]*)"', src) for k in ('name', 'initial', 'tag', 'url')}
        if not (fields['name'] and fields['url']):
            continue
        name = fields['name'].group(1)
        initial = fields['initial'].group(1) if fields['initial'] else name[:1]
        tag_html = (f'\n                                <p class="mt-0.5 text-xs md:text-sm text-gray-400">{esc(fields["tag"].group(1))}</p>'
                    if fields['tag'] else '')
        out.append(f'''
                        <a href="{esc(fields['url'].group(1))}" class="group rounded-2xl border border-white/10 bg-panelBg/60 hover:bg-panelBg hover:border-brandPink/40 p-5 md:p-6 shadow-lg shadow-black/20 transition-all flex items-center gap-4">
                            <div class="w-14 h-14 md:w-16 md:h-16 shrink-0 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-xl md:text-2xl font-extrabold text-gradient">{esc(initial)}</div>
                            <div>
                                <h3 class="text-base md:text-lg font-bold text-white leading-tight group-hover:text-brandPink transition-colors">{esc(name)}</h3>{tag_html}
                                <span class="mt-1.5 inline-block font-mono text-[10px] uppercase tracking-wider text-brandGreen/90 border border-brandGreen/30 rounded px-1.5 py-0.5">Live</span>
                            </div>
                        </a>''')
    return ''.join(out)


def seed_static_cards(apps):
    targets = [
        ('index.html', [('heatCarousel', None), ('siteGrid', 'sites'), ('appCarousel', ('carousel', 9))]),
        ('projects.html', [('heatGrid', None), ('siteGrid', 'sites'), ('appGrid', ('grid', None))]),
    ]
    for name, containers in targets:
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            print(f'[SEED] skip {name} (not found)')
            continue
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        original = text
        for container_id, spec in containers:
            if spec is None:
                inner = _heat_cards(text)
            elif spec == 'sites':
                inner = _site_cards(text)
            else:
                layout, limit = spec
                inner = _app_cards(apps[:limit] if limit else apps, layout)
            if not inner:
                continue
            updated = _seed(text, container_id, inner)
            if updated is None:
                print(f'[SEED] warn {name}: #{container_id} not found or not empty')
                continue
            text = updated
        if text != original:
            with open(path, 'w', encoding='utf-8', newline='') as f:
                f.write(text)
            print(f'[SEED] {name} static cards refreshed')
        else:
            print(f'[SEED] {name} unchanged')


SITE = 'https://crystllabs.com'

TOP_PAGES = [
    ('', '1.0'),
    ('projects.html', '0.9'),
    ('blogs.html', '0.7'),
    ('personnel.html', '0.6'),
    ('privacy.html', '0.5'),
    ('terms.html', '0.5'),
    ('data-deletion.html', '0.5'),
]


def write_sitemap(apps):
    urls = [f'{SITE}/{p}' for p, _ in TOP_PAGES]
    prios = [pr for _, pr in TOP_PAGES]
    for a in apps:
        urls.append(f"{SITE}/apps/{a['slug']}.html")
        prios.append('0.8')

    body = '\n'.join(
        f'  <url>\n    <loc>{u}</loc>\n    <priority>{p}</priority>\n  </url>'
        for u, p in zip(urls, prios)
    )
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           f'{body}\n</urlset>\n')
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8', newline='') as f:
        f.write(xml)
    print(f'[SEO]  sitemap.xml ({len(urls)} urls)')


def main():
    apps = load_apps()
    os.makedirs(APPS_DIR, exist_ok=True)

    for app in apps:
        out = os.path.join(APPS_DIR, f"{app['slug']}.html")
        with open(out, 'w', encoding='utf-8') as f:
            f.write(render_page(app))
        print(f"[APP] page  -> apps/{app['slug']}.html")

    data_out = os.path.join(APPS_DIR, 'apps.data.js')
    with open(data_out, 'w', encoding='utf-8') as f:
        f.write(render_data_js(apps))
    print(f"[APP] data  -> apps/apps.data.js  ({len(apps)} apps)")

    seed_static_cards(apps)
    write_sitemap(apps)
    print("Done.")


if __name__ == '__main__':
    main()
