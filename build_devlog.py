# -*- coding: utf-8 -*-
"""
Crystl Labs // Dev log extractor

Reads the real git history of every app listed in apps_data.json and writes
devlog_data.json, which build_apps.py renders into each app page.

Nothing here is written by hand: every entry is a commit that exists, on the
date it was made. Noise commits ("updates", "fixes", merges, build chores) are
dropped so the log reads as a history rather than a reflog dump.

The per-app `intro` paragraphs live in devlog_intros.json and are the only
prose; this script never overwrites them.

Run:  python build_devlog.py
"""

import os
import re
import json
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'devlog_data.json')
INTROS = os.path.join(ROOT, 'devlog_intros.json')

# Commit subjects that carry no information for a reader
NOISE = re.compile(
    r'^(updates?|fixes?|big work|wip|misc|cleanup|test|tests?|'
    r'merge\b.*|update \S+\.xml|build: mark gradlew executable.*|'
    r'.*\bdeploymentTargetSelector\b.*)$', re.I)

# Subjects that are pure bookkeeping rather than product change
CHORE = re.compile(r'^(docs?|doc|chore|build|ci)\b[:\s]', re.I)


def git(sd, *args):
    try:
        r = subprocess.run(['git', '-C', sd] + list(args), capture_output=True,
                           text=True, encoding='utf-8', errors='replace', timeout=60)
        return r.stdout.strip()
    except Exception:
        return ''


def repo_for(sd):
    """Return (repo_root, path_within_repo).

    Not every project owns its repository. The web tools live in a folder inside
    the `sites` monorepo, so the log has to be taken at the repo root and scoped
    to the subdirectory, or the project looks like it has no history at all.
    """
    sd = os.path.abspath(sd)
    cur = sd
    while True:
        if os.path.isdir(os.path.join(cur, '.git')):
            rel = os.path.relpath(sd, cur).replace(os.sep, '/')
            return cur, ('' if rel == '.' else rel)
        parent = os.path.dirname(cur)
        if parent == cur:
            return None, ''
        cur = parent


def history(sd):
    root, sub = repo_for(sd)
    if not root:
        return []
    scope = ['--', sub] if sub else []
    raw = git(root, 'log', '--no-merges', '--format=%ad\x1f%s', '--date=short', *scope)
    rows = []
    for line in raw.split('\n'):
        if '\x1f' not in line:
            continue
        day, subj = line.split('\x1f', 1)
        subj = subj.strip()
        if not subj or NOISE.match(subj):
            continue
        rows.append({'date': day, 'subject': subj})
    return rows


def stats(sd, rows):
    days = sorted({r['date'] for r in rows})
    version = ''
    # versionName lives in the Gradle file for the Android builds
    for name in ('app/build.gradle.kts', 'app/build.gradle', 'build.gradle.kts'):
        p = os.path.join(sd, name)
        if not os.path.exists(p):
            continue
        try:
            txt = open(p, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        m = re.search(r'versionName\s*=?\s*"([^"]+)"', txt)
        if m:
            version = m.group(1)
            break
    root, sub = repo_for(sd)
    scope = ['--', sub] if sub else []
    return {
        'commits': int(git(root, 'rev-list', '--count', 'HEAD', *scope) or 0) if root else 0,
        'activeDays': len(days),
        'firstDay': days[0] if days else '',
        'lastDay': days[-1] if days else '',
        'version': version,
        'tags': [t for t in git(sd, 'tag', '--sort=-v:refname').split('\n') if t][:5],
    }


def main():
    apps = json.load(open(os.path.join(ROOT, 'apps_data.json'), encoding='utf-8'))['apps']
    intros = json.load(open(INTROS, encoding='utf-8')) if os.path.exists(INTROS) else {}

    out = {}
    for a in apps:
        sd = a.get('sourceDir') or ''
        if not sd or not os.path.isdir(sd) or not repo_for(sd)[0]:
            print(f"[LOG]  skip {a['slug']} (no repo at {sd})")
            continue
        rows = history(sd)
        if not rows:
            print(f"[LOG]  skip {a['slug']} (no usable commits)")
            continue
        # Product changes first; chores kept but marked so the page can de-emphasise them
        for r in rows:
            r['chore'] = bool(CHORE.match(r['subject']))
        out[a['slug']] = {
            'stats': stats(sd, rows),
            'intro': intros.get(a['slug'], ''),
            'entries': rows,
        }
        s = out[a['slug']]['stats']
        print(f"[LOG]  {a['slug']:26s} {len(rows):4d} entries  "
              f"{s['firstDay']} -> {s['lastDay']}  v{s['version'] or '?'}")

    with open(OUT, 'w', encoding='utf-8', newline='') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f'[LOG]  devlog_data.json ({len(out)} apps)')


if __name__ == '__main__':
    main()
