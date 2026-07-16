# -*- coding: utf-8 -*-
"""
Crystl Labs Automation Pipeline Compiler v2.0
Author: Crystl Labs Senior Dev
Year: 2026

Automates compilation of Markdown (.md) blogs into standalone post pages 
and updates the index index pages with summaries and links.
"""

import os
import re
import sys
from datetime import datetime

def ensure_directories():
    """Generates localized storage architectures if they don't exist yet."""
    paths = ['_posts/ceo', '_posts/dev', 'ceo', 'dev']
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"[ENGINE] Verified/Created directory: {path}")

def parse_table_row(line):
    """Splits a `| a | b |` row into trimmed cells, honoring `\\|` as an escaped literal pipe."""
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    cells = re.split(r'(?<!\\)\|', line)
    return [c.strip().replace('\\|', '|') for c in cells]

def convert_lists(content):
    """Groups consecutive '- ' lines into a single <ul>, line by line (avoids eating the
    blank line after a list that a regex-based wrap would consume as part of the last </li>)."""
    lines = content.split('\n')
    out = []
    i = 0
    while i < len(lines):
        m = re.match(r'^\s*-\s+(.*)$', lines[i])
        if m:
            items = []
            while i < len(lines):
                m2 = re.match(r'^\s*-\s+(.*)$', lines[i])
                if not m2:
                    break
                items.append(m2.group(1))
                i += 1
            li_html = ''.join(f'<li class="ml-4 list-disc text-gray-400 text-sm py-1">{item}</li>' for item in items)
            out.append(f'<ul class="my-4">{li_html}</ul>')
        else:
            out.append(lines[i])
            i += 1
    return '\n'.join(out)

def convert_tables(content):
    """Converts GFM-style pipe tables into HTML tables, line by line."""
    lines = content.split('\n')
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        is_header = line.strip().startswith('|')
        is_separator = i + 1 < len(lines) and re.match(r'^\s*\|?[\s:|-]+\|?\s*$', lines[i + 1] or '')
        if is_header and is_separator:
            header = parse_table_row(line)
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append(parse_table_row(lines[i]))
                i += 1
            thead = ''.join(f'<th class="text-left text-[11px] font-mono text-gray-400 uppercase tracking-wide px-3 py-2 border-b border-white/10 whitespace-nowrap">{h}</th>' for h in header)
            tbody = ''
            for row in rows:
                tds = ''.join(f'<td class="text-sm text-gray-300 px-3 py-2 border-b border-white/5 whitespace-nowrap">{c}</td>' for c in row)
                tbody += f'<tr>{tds}</tr>'
            out.append(f'<div class="overflow-x-auto my-6"><table class="w-full border-collapse"><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table></div>')
        else:
            out.append(line)
            i += 1
    return '\n'.join(out)

def parse_markdown_to_html(content):
    """
    Custom lightweight parser to render standard Markdown components
    into premium, responsive HTML without bloated third-party libraries.
    """
    # Parse bold text
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    # Parse italic text (after bold, so leftover single asterisks are unambiguous)
    content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
    # Parse tables (before headers/lists, since separator rows contain '-' and '|')
    content = convert_tables(content)
    # Parse headers
    content = re.sub(r'### (.*?)\n', r'<h4 class="text-sm font-semibold text-white mt-4 mb-2">\1</h4>\n', content)
    content = re.sub(r'## (.*?)\n', r'<h3 class="text-base font-mono text-brandGreen mt-6 mb-3">\1</h3>\n', content)
    content = re.sub(r'# (.*?)\n', r'<h2 class="text-lg font-extrabold tracking-tight text-white mt-8 mb-4">\1</h2>\n', content)
    # Parse lists
    content = convert_lists(content)
    # Parse code blocks
    content = re.sub(
        r'```(.*?)\n(.*?)```',
        r'<pre class="bg-black/40 border border-white/10 p-4 rounded-lg font-mono text-xs text-brandGreen overflow-x-auto my-6"><code class="language-\1">\2</code></pre>',
        content,
        flags=re.DOTALL
    )
    # Parse images
    content = re.sub(
        r'!\[(.*?)\]\((.*?)\)',
        r'<img src="\2" alt="\1" class="max-w-full my-6 rounded-xl border border-white/10 shadow-xl shadow-black/30 block mx-auto">',
        content
    )
    
    # Wrap standard paragraphs with linebreaks
    paragraphs = content.split('\n\n')
    formatted_p = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if not p.startswith('<h') and not p.startswith('<ul') and not p.startswith('<li') and not p.startswith('<pre') and not p.startswith('<img') and not p.startswith('<div'):
            p = f'<p class="text-gray-400 text-sm leading-relaxed mb-4">{p}</p>'
        formatted_p.append(p)
    
    return '\n'.join(formatted_p)

def parse_post(file_path):
    """Splits custom metadata tags and formats post output properties."""
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    # Match Frontmatter bounds
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', raw_text, re.DOTALL)
    if not frontmatter_match:
        print(f"[WARN] No metadata wrapper found on file: {file_path}. Using fallbacks.")
        return {
            'title': 'Untitled Dispatch',
            'date': datetime.today().strftime('%Y-%m-%d'),
            'summary': 'System parameters compiled successfully.',
            'tags': ['System'],
            'body': parse_markdown_to_html(raw_text)
        }

    metadata_raw = frontmatter_match.group(1)
    body = frontmatter_match.group(2)

    metadata = {}
    for line in metadata_raw.split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            metadata[key.strip().lower()] = val.strip()

    title = metadata.get('title', 'Untitled Dispatch')
    date_str = metadata.get('date', datetime.today().strftime('%Y-%m-%d'))
    summary = metadata.get('summary', 'System parameters compiled successfully.')
    tags_raw = metadata.get('tags', '')
    tags = [t.strip() for t in tags_raw.split(',') if t.strip()]

    html_content = parse_markdown_to_html(body)

    return {
        'title': title,
        'date': date_str,
        'summary': summary,
        'tags': tags,
        'body': html_content
    }

def generate_standalone_page(post, category, slug, color, tag):
    """Generates a complete, beautiful standalone HTML page for an article inside its respective folder."""
    back_url = "../ceo-blog.html" if category == "ceo" else "../blogs.html"
    accent_color = "brandPink" if category == "ceo" else "brandBlue"
    glow_rgb = "217,70,239" if category == "ceo" else "59,130,246"

    tags_elements = ""
    for t in post['tags']:
        tags_elements += f'<span class="text-[11px] font-mono text-gray-400 bg-white/5 px-2.5 py-1 rounded border border-white/10">{t}</span>\n'

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post['title']} | Crystl Labs</title>
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
            background-image: radial-gradient(circle at 20% 0%, rgba({glow_rgb},0.07), transparent 40%);
        }}
    </style>
</head>
<body class="bg-darkBg text-gray-300 font-sans antialiased min-h-screen md:h-screen flex flex-col md:overflow-hidden">

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
                CONNECTED
            </span>
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
                        <li><a href="../projects.html" class="block px-2.5 py-1.5 rounded-md text-gray-500 text-xs font-mono hover:bg-white/5 hover:text-white transition-colors truncate">projects.html</a></li>
                        <li>
                            <span class="flex items-center justify-between px-2.5 py-1.5 rounded-md bg-white/5 border-l-2 border-brandGreen text-white text-xs font-mono">
                                blogs.html
                                <span class="w-1.5 h-1.5 rounded-full bg-brandGreen animate-pulse flex-shrink-0"></span>
                            </span>
                        </li>
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
                <article class="rounded-2xl border border-white/10 bg-panelBg/60 p-6 md:p-8 shadow-xl shadow-black/20">
                    <header class="mb-8 border-b border-white/10 pb-6">
                        <div class="flex justify-between items-center mb-4">
                            <span class="text-[11px] font-mono text-{accent_color} tracking-wide">{tag} // ARTICLE</span>
                            <span class="text-[11px] font-mono text-gray-500">{post['date']}</span>
                        </div>
                        <h1 class="text-xl md:text-2xl font-extrabold tracking-tight text-white mb-3">{post['title']} //</h1>
                        <p class="font-mono text-[11px] text-gray-500 uppercase tracking-wide mb-4">Written by AP39</p>
                        <p class="text-gray-400 text-sm leading-relaxed border-l-2 border-white/10 pl-4 py-1">
                            {post['summary']}
                        </p>
                    </header>

                    <div class="prose prose-invert max-w-none text-gray-300">
                        {post['body']}
                    </div>

                    <div class="border-t border-white/10 pt-6 mt-8 flex flex-wrap gap-2">
                        {tags_elements}
                    </div>
                </article>

                <div class="mt-8 text-center">
                    <a href="{back_url}" class="inline-block px-6 py-2.5 rounded-lg border border-white/10 text-gray-400 font-mono text-xs uppercase tracking-wide hover:text-white hover:border-white/20 transition-colors">
                        &lt;- Return to directory
                    </a>
                </div>
            </div>
        </main>
    </div>

    <script>
        function toggleMenu() {{
            document.getElementById('sidebar').classList.toggle('-translate-x-full');
            document.getElementById('sidebarBackdrop').classList.toggle('hidden');
            document.getElementById('iconOpen').classList.toggle('hidden');
            document.getElementById('iconClose').classList.toggle('hidden');
        }}
    </script>
</body>
</html>
"""
    file_name = f"{category}/{slug}.html"
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"[ENGINE] Created stand-alone page: {file_name}")

def compile_posts(folder, tag_color, prefix):
    """
    Iterates through localized markdown dispatches, compiles individual HTML files,
    and returns compiled index preview snippets.
    """
    category = "ceo" if "ceo" in folder else "dev"
    posts = []
    if not os.path.exists(folder):
        return ""

    for file_name in sorted(os.listdir(folder), reverse=True):
        if file_name.endswith('.md'):
            slug = file_name.replace('.md', '')
            path = os.path.join(folder, file_name)
            post = parse_post(path)
            if post:
                post['slug'] = slug
                posts.append(post)

    # Sort posts by date descending
    posts.sort(key=lambda x: x['date'], reverse=True)

    compiled_html = ""
    for idx, post in enumerate(posts):
        slug = post['slug']
        tag_elements = ""
        for tag in post['tags']:
            tag_elements += f'<span class="text-[11px] font-mono text-gray-400 bg-white/5 px-2.5 py-1 rounded border border-white/10">{tag}</span>\n'

        # Generate individual static post files
        generate_standalone_page(post, category, slug, tag_color, f"{prefix}_{idx+1:03d}")

        # Generate index cards that link to standalone pages (fully clickable blocks)
        compiled_html += f"""
                    <a href="{category}/{slug}.html" class="group block text-left rounded-2xl border border-white/10 bg-panelBg/60 hover:bg-panelBg hover:border-{tag_color}/40 p-6 shadow-lg shadow-black/20 transition-all">
                        <div class="flex justify-between items-center mb-4">
                            <span class="text-[11px] font-mono text-{tag_color} tracking-wide">{prefix}_{idx+1:03d} // DIRECTIVE</span>
                            <span class="text-[11px] font-mono text-gray-500">{post['date']}</span>
                        </div>
                        <h2 class="text-lg font-semibold text-white mb-3 group-hover:text-{tag_color} transition-colors">{post['title']}</h2>
                        <p class="text-gray-400 text-sm leading-relaxed mb-6">
                            {post['summary']}
                        </p>
                        <div class="flex flex-wrap justify-between items-center gap-4 border-t border-white/10 pt-4">
                            <div class="flex flex-wrap gap-2">
                                {tag_elements}
                            </div>
                            <span class="text-[11px] font-mono text-gray-500 group-hover:text-white transition-colors">
                                READ LOG ->
                            </span>
                        </div>
                    </a>
        """
    return compiled_html

def inject_to_html(target_file, compiled_posts):
    """Securely updates static deployment structures without breaking layout frameworks."""
    if not os.path.exists(target_file):
        print(f"[ERROR] Could not find target build template file: {target_file}")
        return

    with open(target_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Regex targeting our layout anchor points
    pattern = r'(<!--\s*BEGIN_STATIC_POSTS\s*-->).*?(<!--\s*END_STATIC_POSTS\s*-->)'
    
    if not re.search(pattern, html_content, re.DOTALL):
        print(f"[ERROR] Build anchor comments missing on: {target_file}")
        return

    updated_html = re.sub(
        pattern,
        f"\\1\n{compiled_posts}\n                    \\2",
        html_content,
        flags=re.DOTALL
    )

    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(updated_html)

    print(f"[SUCCESS] Re-compiled and verified static logs inside: {target_file}")

def run_pipeline():
    """Initializes standard parsing operations on target local repositories."""
    print("====================================================")
    print(" CRYSTL LABS // AUTOMATED COMPILATION SYSTEM v2.0   ")
    print("====================================================")
    
    ensure_directories()
    
    # Process CEO transmissions
    print("\n[ENGINE] Analyzing CEO executive transmissions...")
    ceo_html = compile_posts('_posts/ceo', 'brandPink', 'TRANS')
    if ceo_html:
        inject_to_html('ceo-blog.html', ceo_html)
    else:
        print("[ENGINE] No Markdown sources found in _posts/ceo. Keeping defaults.")

    # Process Developer logs
    print("\n[ENGINE] Analyzing Dev senior dispatches...")
    dev_html = compile_posts('_posts/dev', 'brandBlue', 'BUILD')
    if dev_html:
        inject_to_html('blogs.html', dev_html)
    else:
        print("[ENGINE] No Markdown sources found in _posts/dev. Keeping defaults.")

    print("\n====================================================")
    print(" COMPILATION COMPLETE // READY FOR PRODUCTION PUSH  ")
    print("====================================================")

if __name__ == "__main__":
    run_pipeline()