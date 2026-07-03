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

def parse_markdown_to_html(content):
    """
    Custom lightweight parser to render standard Markdown components
    into premium, responsive HTML without bloated third-party libraries.
    """
    # Parse bold text
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    # Parse headers
    content = re.sub(r'### (.*?)\n', r'<h4 class="text-sm font-bold text-white mt-4 mb-2">\1</h4>\n', content)
    content = re.sub(r'## (.*?)\n', r'<h3 class="text-base font-pixel text-brandGreen mt-6 mb-3 uppercase">\1</h3>\n', content)
    content = re.sub(r'# (.*?)\n', r'<h2 class="text-lg font-pixel text-white mt-8 mb-4 uppercase">\1</h2>\n', content)
    # Parse lists
    content = re.sub(r'^\s*-\s*(.*?)$', r'<li class="ml-4 list-disc text-gray-400 text-sm py-1">\1</li>', content, flags=re.MULTILINE)
    # Wrap lists
    content = re.sub(r'(<li.*?>.*?</li>\n?)+', r'<ul class="my-4">\g<0></ul>', content)
    # Parse code blocks (retro styled terminals)
    content = re.sub(
        r'```(.*?)\n(.*?)```', 
        r'<pre class="bg-black/60 border-2 border-[#252542] p-4 rounded font-mono text-xs text-brandGreen overflow-x-auto my-6"><code class="language-\1">\2</code></pre>', 
        content, 
        flags=re.DOTALL
    )
    # Parse images
    content = re.sub(
        r'!\[(.*?)\]\((.*?)\)',
        r'<img src="\2" alt="\1" class="max-w-full my-6 border-4 border-[#252542] shadow-[4px_4px_0_0_#252542] block mx-auto rounded">',
        content
    )
    
    # Wrap standard paragraphs with linebreaks
    paragraphs = content.split('\n\n')
    formatted_p = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if not p.startswith('<h') and not p.startswith('<ul') and not p.startswith('<li') and not p.startswith('<pre') and not p.startswith('<img'):
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
    back_url = "../ceo-blog.html" if category == "ceo" else "../dev-blog.html"
    accent_color = "brandPink" if color == "brandPink" else "brandBlue"
    
    tags_elements = ""
    for t in post['tags']:
        tags_elements += f'<span class="text-xs font-mono text-brandGreen bg-gray-800/50 px-2.5 py-1 border border-gray-700">{t}</span>\n'

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post['title']} | Crystl Labs</title>
    <link rel="icon" type="image/jpeg" href="../favicon.jpg">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{ darkBg: '#0f0f1b', panelBg: '#171729', brandPink: '#D946EF', brandBlue: '#3B82F6', brandGreen: '#39FF14' }},
                    fontFamily: {{ pixel: ['"Press Start 2P"', 'cursive'], sans: ['Inter', 'sans-serif'] }}
                }}
            }}
        }}
    </script>
    <style>
        ::-webkit-scrollbar {{ width: 12px; }}
        ::-webkit-scrollbar-track {{ background: #0f0f1b; border-left: 2px solid #252542; }}
        ::-webkit-scrollbar-thumb {{ background: #252542; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #D946EF; }}
        .glow-text {{ text-shadow: 0 0 8px rgba(217, 70, 239, 0.6); }}
    </style>
</head>
<body class="bg-darkBg text-gray-300 font-sans antialiased min-h-screen md:h-screen flex flex-col md:overflow-hidden border-[4px] md:border-[8px] border-[#252542]">
    
    <nav class="bg-panelBg px-4 py-2 md:px-6 md:py-3 flex justify-between items-center border-b-4 border-[#252542] shrink-0 z-20">
        <a href="../index.html" class="flex items-center gap-4 md:gap-6 hover:opacity-80">
            <img src="../crystl1.jpg" alt="" class="h-6 md:h-8 w-auto">
            <span class="font-pixel text-[10px] md:text-xs text-white uppercase hidden sm:block">Crystl_Engine_v1.0</span>
        </a>
        <div class="flex items-center space-x-4 md:space-x-6 font-pixel text-[10px] text-gray-500 uppercase">
            <a href="{back_url}" class="hover:text-brandBlue transition"><- Back_To_Logs</a>
        </div>
    </nav>

    <div class="flex flex-col md:flex-row flex-grow md:overflow-hidden relative">
        <aside class="w-full md:w-48 bg-panelBg border-b-4 md:border-b-0 md:border-r-4 border-[#252542] p-4 shrink-0 md:overflow-y-auto">
            <h2 class="text-brandPink font-pixel text-[10px] mb-4 md:mb-6 uppercase tracking-widest">>> Explorer</h2>
            <ul class="space-y-3 md:space-y-4 text-sm font-sans text-gray-400">
                <li class="hover:text-white transition-transform cursor-pointer flex items-center gap-2 mb-2">
                    <span class="text-brandBlue font-pixel text-[8px]">📁</span> <span>src_files</span>
                </li>
                <li class="px-2 py-1 text-gray-500 text-xs hover:text-white transition-colors">
                    <a href="../index.html" class="block w-full truncate">📄 index.html</a>
                </li>
                <li class="px-2 py-1 text-gray-500 text-xs hover:text-white transition-colors">
                    <a href="../privacy.html" class="block w-full truncate">📄 privacy.html</a>
                </li>
                <li class="px-2 py-1 text-gray-500 text-xs hover:text-white transition-colors">
                    <a href="../terms.html" class="block w-full truncate">📄 terms.html</a>
                </li>
                <li class="px-2 py-1 text-gray-500 text-xs hover:text-white transition-colors">
                    <a href="../data-deletion.html" class="block w-full truncate">📄 data-deletion.html</a>
                </li>
                <li class="hover:text-white transition-transform cursor-pointer flex items-center gap-2 mt-6 mb-2">
                    <span class="text-brandPink font-pixel text-[8px]">📁</span> <span>public_logs</span>
                </li>
                <li class="px-2 py-1 text-gray-500 text-xs hover:text-white transition-colors">
                    <a href="../ceo-blog.html" class="block w-full truncate">📄 ceo_executive.log</a>
                </li>
                <li class="px-2 py-1.5 text-brandGreen font-bold bg-gray-800 rounded border border-gray-700 flex justify-between items-center shadow-md text-xs">
                    <span class="truncate">📄 dev_senior.log</span><span class="w-2 h-2 rounded-full bg-brandBlue animate-pulse ml-2 flex-shrink-0"></span>
                </li>
            </ul>
        </aside>

        <main class="flex-grow p-6 md:p-8 md:overflow-y-auto bg-darkBg relative">
            <div class="max-w-3xl mx-auto">
                <article class="bg-panelBg border-4 border-[#252542] p-8 shadow-[8px_8px_0_0_#252542]">
                    <header class="mb-8 border-b border-[#252542] pb-6">
                        <div class="flex justify-between items-center mb-4">
                            <span class="text-xs font-pixel text-{accent_color}">{tag} // ARTICLE</span>
                            <span class="text-xs font-mono text-gray-500">{post['date']}</span>
                        </div>
                        <h1 class="text-xl md:text-2xl font-bold text-white mb-4">{post['title']}</h1>
                        <p class="text-gray-400 text-sm font-mono leading-relaxed border-l-4 border-brandGreen pl-4 py-1">
                            {post['summary']}
                        </p>
                    </header>

                    <div class="prose prose-invert max-w-none text-gray-300">
                        {post['body']}
                    </div>

                    <div class="border-t border-[#252542] pt-6 mt-8 flex flex-wrap gap-2">
                        {tags_elements}
                    </div>
                </article>
                
                <div class="mt-8 text-center">
                    <a href="{back_url}" class="inline-block px-6 py-2 border-2 border-brandGreen text-brandGreen font-pixel text-xs hover:bg-brandGreen hover:text-black transition">
                        <- RETURN TO DIRECTORY
                    </a>
                </div>
            </div>
        </main>
    </div>

    <footer class="bg-black border-t-4 border-[#252542] p-3 md:p-4 shrink-0 h-auto md:h-20 md:overflow-y-auto font-pixel text-[8px] md:text-[10px] leading-relaxed text-brandGreen flex flex-col justify-center">
        <div class="flex flex-col md:flex-row justify-between md:items-center w-full gap-2">
            <div>
                <p>> Reading Transmission Article Stream: Closed Loop Connected</p>
            </div>
            <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 text-gray-500 mt-2 md:mt-0">
                <div class="flex flex-wrap gap-3">
                    <span>SYS_LINKS:</span>
                    <a href="../privacy.html" class="hover:text-white transition">[ PRIVACY ]</a>
                    <a href="../terms.html" class="hover:text-white transition">[ TERMS ]</a>
                    <a href="../data-deletion.html" class="hover:text-white transition">[ DELETION ]</a>
                </div>
                <span class="text-gray-700">© 2026 CRYSTL LABS</span>
            </div>
        </div>
    </footer>
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
            tag_elements += f'<span class="text-xs font-mono text-brandGreen bg-gray-800/50 px-2.5 py-1 border border-gray-700">{tag}</span>\n'

        # Generate individual static post files
        generate_standalone_page(post, category, slug, tag_color, f"{prefix}_{idx+1:03d}")

        # Generate index cards that link to standalone pages (fully clickable blocks)
        compiled_html += f"""
                    <a href="{category}/{slug}.html" class="group block text-left bg-panelBg border-4 border-[#252542] p-6 shadow-[4px_4px_0_0_#252542] hover:border-{tag_color} transition-colors">
                        <div class="flex justify-between items-center mb-4">
                            <span class="text-xs font-pixel text-{tag_color}">{prefix}_{idx+1:03d} // DIRECTIVE</span>
                            <span class="text-xs font-mono text-gray-500">{post['date']}</span>
                        </div>
                        <h2 class="text-lg font-bold text-white mb-3 group-hover:text-{tag_color} transition-colors">{post['title']}</h2>
                        <p class="text-gray-400 text-sm leading-relaxed mb-6 font-sans">
                            {post['summary']}
                        </p>
                        <div class="flex flex-wrap justify-between items-center gap-4 border-t border-[#252542] pt-4">
                            <div class="flex flex-wrap gap-2">
                                {tag_elements}
                            </div>
                            <span class="text-xs font-pixel text-brandGreen group-hover:text-white transition">
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
        inject_to_html('dev-blog.html', dev_html)
    else:
        print("[ENGINE] No Markdown sources found in _posts/dev. Keeping defaults.")

    print("\n====================================================")
    print(" COMPILATION COMPLETE // READY FOR PRODUCTION PUSH  ")
    print("====================================================")

if __name__ == "__main__":
    run_pipeline()