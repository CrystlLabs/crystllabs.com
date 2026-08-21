# -*- coding: utf-8 -*-
"""
Crystl Labs // Dev log extractor

Reads the real git history of every app listed in apps_data.json and writes
devlog_data.json, which build_apps.py renders into each app page.

Nothing here is written by hand: every entry is a commit that exists, on the
date it was made. The raw history is a working log, so most of it is filtered
out: build chores, merges, phase numbers, audit rounds, TODO ids and notes to
self. What is left is the set of commits that describe a change to the app,
said in one sentence.

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

# How many readable entries to keep per app. The page shows fewer still.
KEEP_PER_APP = 30

# Commit subjects that carry no information for a reader
NOISE = re.compile(
    r'^(updates?|fixes?|big work|wip|misc|cleanup|test|tests?|'
    r'merge\b.*|update \S+\.xml|build: mark gradlew executable.*|'
    r'.*\bdeploymentTargetSelector\b.*)$', re.I)

# Subjects that are pure bookkeeping rather than product change
CHORE = re.compile(r'^(docs?|doc|chore|build|ci)\b[:\s]', re.I)

# Commit types that are never product change
DROP_TYPE = re.compile(r'^(test|chore|docs?|build|ci|wip)(\([^)]*\))?\s*:', re.I)

# Conventional-commit prefixes: the scope is internal, the type adds nothing
PREFIX = re.compile(r'^(feat|fix|perf|refactor|style|art|release|ui|ux|audio|game|content)'
                    r'(\([^)]*\))?\s*:\s*', re.I)
LEADING_JUNK = re.compile(r'^[@#*\s]+')

# A subject with an ", and ..." or " -- ..." tail is a second thought about the
# process rather than a headline. Those are dropped whole rather than truncated,
# so every line on the page is still the commit exactly as it was written.
TAIL = re.compile(r',\s+and\s+|\s+[-–—]{1,2}\s+')

# Internal vocabulary: real work, meaningless to somebody reading an app page
INTERNAL = re.compile(r"""
    \b(README|TODO|PLAN|CHANGELOG|HANDOFF|ROADMAP|BUGSFOUND|BUGS|FIXPACK)\b
  | \S+\.(md|txt|json|kts|gradle|ps1|sh|yml|yaml|xml|py|tscn|cfg|properties|log|uid)\b
  | \b(phase|phases)\b
  | \b(audit|audited|handoff|close[-\s]?out|sweep|swept|reconcile[ds]?|adversar\w+)\b
  | \b(gate|gates|gated|harness(es)?|clause[sd]?|fixture[s]?|instrument(ed|ation)?|tuner)\b
  | \b(docs?|doc|changelog|report|records?|answer\s+sheet)\b
  | \bsession\b | \bcheckpoint\b | \bspike\b | \bbackport\b | \bscratch\b
  | \b(round\s+(one|two|three|\d))\b
  | \b[OC]\d{1,3}\b | \b[A-Z]\d{1,2}[a-z]?\b | \b[A-Z]+_V\d+\b | \b[A-Z]\.\d+\b
  | ^\s*\d+(\.\d+)+ | \b\d+\.\d+[A-Z]\b
  | \bcommit(ted|s)?\b | \bgit\b | \bbranch\b | \bversion\s?[Cc]ode\b | \bCrystl'?s?\b
  | \bmy\s+own\b | \bI\b
  | \b(the\s+)?(owner|board)\b
  | \bqueue\b | \bcomments?\b
  | \b(review(ed|s)?|finding[s]?|defect[s]?)\b
  | \b(regression|flake|flaky|negative[-\s]test\w*|smoke\s?test|emulator|infra|QA|debug)\b
  | \b\d+/\d+\s*(green|pass\w*)\b | \bexit\s+0\b
  | \b(agent|agents|sonnet|claude|opus|fable)\b
  | \b[A-Z]{2,}_[A-Z_]{2,}\b
  | \b\w+\.\w+\( | \b\w+_\w+_\w+\b
  | \bcom\.[a-z]+\.[a-z]+\b | \b[a-z0-9-]+-[0-9a-f]{5,}\b
  | ^\s*(record|records|document|note|track|ignore|verify|verified|checkpoint|retract|correct)\b
  | \b(env|environment)\s+details\b | \bdebug-only\b
  | \bdevice\s+pass\b | \btablet\s+pass\b
  | \balmost\b | \baddons?\b
""", re.I | re.X)

# Pixel-pushing: true, tiny, and dull to read
MICRO = re.compile(r'\b\d+\s?(px|dp|pt)\b|\b\d+%\b|\bnudge[ds]?\b|\bhugs?\b'
                   r'|\bsymmetric\w*\b|\bequal-width\b|\bgives?\s+way\b'
                   r'|\bpadding\b|\bmargin\b|\btitle\s+bar\b', re.I)

# Words too common to identify what a line is about
STOP = {'the', 'a', 'an', 'and', 'of', 'to', 'in', 'on', 'for', 'with', 'is', 'it',
        'its', 'that', 'add', 'fix', 'fixes', 'make', 'stop', 'no', 'all', 'every',
        'one', 'two', 'three', 'four', 'now', 'not', 'so', 'but', 'from', 'at', 'by',
        'as', 'into', 'be', 'get', 'gets', 'give', 'gives'}


def tidy(subject):
    """Strip the machine-facing prefix and give the line a capital."""
    s = PREFIX.sub('', LEADING_JUNK.sub('', subject)).strip().rstrip(',:;- ')
    return s[:1].upper() + s[1:] if s else s


def readable(subject):
    if DROP_TYPE.match(subject.strip()):
        return False
    s = tidy(subject)
    if TAIL.search(s) or INTERNAL.search(s) or MICRO.search(s):
        return False
    return len(s) >= 16 and len(s.split()) >= 3


def topic(subject):
    """Two significant words: enough to spot a run of commits on one thing."""
    w = [re.sub(r'[^a-z0-9]', '', t.lower()) for t in tidy(subject).split()]
    w = [t for t in w if t and t not in STOP]
    return ' '.join(w[:2])


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
    """Every commit, before the reader filter, so the stats stay honest."""
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


def highlights(rows):
    """The lines worth reading: no chores, no internals, one per topic."""
    out = []
    seen = set()
    for r in rows:
        if CHORE.match(r['subject']) or not readable(r['subject']):
            continue
        key = topic(r['subject'])
        if key in seen:
            continue
        seen.add(key)
        out.append({'date': r['date'], 'subject': tidy(r['subject'])})
        if len(out) >= KEEP_PER_APP:
            break
    return out


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
        entries = highlights(rows)
        if not entries:
            print(f"[LOG]  skip {a['slug']} (nothing readable in {len(rows)} commits)")
            continue
        out[a['slug']] = {
            'stats': stats(sd, rows),
            'intro': intros.get(a['slug'], ''),
            'entries': entries,
        }
        s = out[a['slug']]['stats']
        print(f"[LOG]  {a['slug']:26s} {len(entries):3d} of {len(rows):4d}  "
              f"{s['firstDay']} -> {s['lastDay']}  v{s['version'] or '?'}")

    with open(OUT, 'w', encoding='utf-8', newline='') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f'[LOG]  devlog_data.json ({len(out)} apps)')


if __name__ == '__main__':
    main()
