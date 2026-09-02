"""Attach the shared Crystl Labs visual system to every generated/static page.

The operation is idempotent. Run it after any compiler that emits HTML.
"""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
HEAD_MARKER = '<link rel="stylesheet" href="/assets/site-redesign.css">'
SCRIPT_MARKER = '<script src="/assets/site-redesign.js"></script>'
HEAD_ASSETS = f'''    <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
    <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    {HEAD_MARKER}
'''


def sync(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    original = text
    text = re.sub(r'\s*<link rel="icon" type="image/png" href="[^"]*favicon\.png">', '', text)
    if HEAD_MARKER not in text:
        text = text.replace('</head>', f'{HEAD_ASSETS}</head>', 1)
    if SCRIPT_MARKER not in text:
        text = text.replace('</body>', f'    {SCRIPT_MARKER}\n</body>', 1)
    if text == original:
        return False
    path.write_text(text, encoding='utf-8', newline='')
    return True


def main() -> None:
    changed = []
    for path in sorted(ROOT.rglob('*.html')):
        if '.git' in path.parts or 'design-mockups' in path.parts:
            continue
        if sync(path):
            changed.append(path.relative_to(ROOT).as_posix())
    print(f'[DESIGN] synchronized {len(changed)} page(s)')
    for name in changed:
        print(f'  {name}')


if __name__ == '__main__':
    main()
