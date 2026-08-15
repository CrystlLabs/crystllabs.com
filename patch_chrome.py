# -*- coding: utf-8 -*-
"""
Crystl Labs // Chrome patcher

index.html, projects.html and the legal pages are hand-maintained, so the shared
bits drift. This walks them and enforces two things that a policy review looks
for on every page, not just the home page:

  1. the AdSense loader is present
  2. contact.html is in the sidebar

Idempotent: running it twice changes nothing.

Run:  python patch_chrome.py
"""

import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))

PAGES = ['index.html', 'projects.html', 'personnel.html',
         'privacy.html', 'terms.html', 'data-deletion.html']

ADS = ('    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
       '?client=ca-pub-8883757785147352" crossorigin="anonymous"></script>\n')

CONTACT_LI = ('                        <li><a href="contact.html" class="block px-2.5 py-1.5 '
              'rounded-md text-gray-500 text-xs font-mono hover:bg-white/5 hover:text-white '
              'transition-colors truncate">contact.html</a></li>\n')


def patch(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    before, notes = text, []

    if 'adsbygoogle.js' not in text:
        # Straight after the Tailwind tag, matching the placement index.html already uses.
        text, n = re.subn(r'(\n[ \t]*<script src="https://cdn\.tailwindcss\.com"></script>\n)',
                          lambda m: m.group(1) + ADS, text, count=1)
        if n:
            notes.append('adsense')
        else:
            text = text.replace('</head>', ADS + '</head>', 1)
            notes.append('adsense(head)')

    if 'contact.html' not in text:
        m = re.search(r'^[ \t]*<li><a href="personnel\.html".*?</li>\n', text, re.M | re.S)
        if m:
            text = text[:m.end()] + CONTACT_LI + text[m.end():]
            notes.append('contact-link')
        else:
            notes.append('contact-link:SKIPPED (no personnel.html sidebar entry)')

    if text != before:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
    print(f'[CHROME] {os.path.basename(path):22s} {", ".join(notes) if notes else "already current"}')


def main():
    for name in PAGES:
        p = os.path.join(ROOT, name)
        if os.path.exists(p):
            patch(p)
        else:
            print(f'[CHROME] {name:22s} MISSING')


if __name__ == '__main__':
    main()
