#!/usr/bin/env python3
"""
Bake the English i18n strings into the static HTML.

The pages ship as a shell: elements carry data-i18n="key" and are left empty,
then switchLang() fills them from the inline `i18n` object at runtime. Crawlers
that do not execute JS therefore see almost no text, which is what got
crystllabs.com rejected by AdSense for low-value content.

This pass writes the English value into every data-i18n element that is
currently EMPTY. switchLang() still overwrites it on load, so behaviour in a
real browser is unchanged. Elements that already contain static text are left
alone. Idempotent: re-running finds them non-empty and skips.

Run after any edit to an inline i18n dictionary:
    python prerender_i18n.py
"""
import os
import re
import sys

PAGES = [
    'index.html', 'projects.html', 'blogs.html', 'personnel.html',
    'privacy.html', 'terms.html', 'data-deletion.html', 'ceo-blog.html',
]

ROOT = os.path.dirname(os.path.abspath(__file__))


def find_en_block(html):
    """Return the source text of the `en: { ... }` object in the inline i18n dict."""
    m = re.search(r'\ben\s*:\s*\{', html)
    if not m:
        return None
    i = m.end() - 1
    depth = 0
    quote = None
    esc = False
    while i < len(html):
        c = html[i]
        if esc:
            esc = False
        elif quote:
            if c == '\\':
                esc = True
            elif c == quote:
                quote = None
        elif c in '"\'`':
            quote = c
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return html[m.end():i]
        i += 1
    return None


def parse_entries(block):
    """key -> string value, for "..." / '...' / `...` literals."""
    out = {}
    i = 0
    n = len(block)
    while i < n:
        m = re.compile(r'([A-Za-z_$][\w$]*)\s*:\s*').match(block, i)
        if not m:
            i += 1
            continue
        i = m.end()
        if i >= n or block[i] not in '"\'`':
            continue
        quote = block[i]
        i += 1
        buf = []
        while i < n:
            c = block[i]
            if c == '\\':
                buf.append(block[i:i + 2])
                i += 2
                continue
            if c == quote:
                i += 1
                break
            buf.append(c)
            i += 1
        out[m.group(1)] = ''.join(buf)
    return out


EMPTY_EL = re.compile(
    r'(<(?P<tag>[a-zA-Z][\w-]*)(?P<attrs>[^>]*\bdata-i18n="(?P<key>[^"]+)"[^>]*)>)'
    r'(?P<inner>\s*)'
    r'(</(?P=tag)>)'
)


def prerender(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    block = find_en_block(html)
    if block is None:
        return None, 'no inline en dictionary'
    strings = parse_entries(block)
    if not strings:
        return None, 'en dictionary parsed empty'

    filled = []
    missing = []

    def repl(m):
        key = m.group('key')
        if m.group('inner').strip():
            return m.group(0)
        val = strings.get(key)
        if val is None:
            missing.append(key)
            return m.group(0)
        filled.append(key)
        return m.group(1) + val + m.group(6)

    new = EMPTY_EL.sub(repl, html)

    if new != html:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(new)
    return (filled, missing), None


def main():
    total = 0
    for name in PAGES:
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            print(f'[skip] {name} (not found)')
            continue
        result, err = prerender(path)
        if err:
            print(f'[skip] {name}: {err}')
            continue
        filled, missing = result
        total += len(filled)
        print(f'[ok]   {name}: filled {len(filled)}'
              + (f', no string for {sorted(set(missing))}' if missing else ''))
    print(f'Done. {total} elements prerendered.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
