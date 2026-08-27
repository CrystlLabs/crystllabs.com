# -*- coding: utf-8 -*-
"""
Crystl Labs // Static page compiler

Pages that are hand-written prose but need the same chrome as everything else.
Shares HEAD / NAV / sidebar with build_blog.py so the nav never drifts.

Run:  python build_pages.py
"""

import os
import json

from build_blog import HEAD, TAIL, sidebar, SITE

ROOT = os.path.dirname(os.path.abspath(__file__))

EMAIL = 'dev@crystllabs.com'


def render_contact():
    ld = json.dumps({
        '@context': 'https://schema.org',
        '@type': 'Organization',
        'name': 'Crystl Labs',
        'url': SITE,
        'logo': f'{SITE}/crystl1.png',
        'email': EMAIL,
        'foundingDate': '2026',
        'address': {'@type': 'PostalAddress', 'addressLocality': 'Siheung-si',
                    'addressRegion': 'Gyeonggi-do', 'addressCountry': 'KR'},
        'contactPoint': [{'@type': 'ContactPoint', 'contactType': 'customer support',
                          'email': EMAIL, 'availableLanguage': ['en', 'ko']}],
        'sameAs': ['https://x.com/crystllabs', 'https://t.me/crystllabsTG'],
    }, ensure_ascii=False)

    head = HEAD.format(
        title='Contact | Crystl Labs',
        desc='How to reach Crystl Labs: support email, bug reports, press, privacy and '
             'data deletion requests, and the response times you should expect.',
        canonical=f'{SITE}/contact.html',
        ogtype='website',
        root='',
        sidebar=sidebar('', 'contact.html'),
        extra_head=f'    <script type="application/ld+json">{ld}</script>\n',
    )

    def card(title, body, accent='brandBlue'):
        return f'''
                    <div class="rounded-2xl border border-white/10 bg-panelBg/60 p-5 md:p-6 shadow-lg shadow-black/20">
                        <h2 class="font-mono text-[11px] uppercase tracking-widest text-{accent}/90 mb-3">{title}</h2>
                        <div class="text-sm text-gray-300 leading-relaxed space-y-3">{body}</div>
                    </div>'''

    mail = (f'<a href="mailto:{EMAIL}" class="text-brandBlue hover:text-brandPink underline '
            f'underline-offset-2 transition-colors">{EMAIL}</a>')

    return head + f'''            <div class="max-w-3xl mx-auto">
                <header class="mb-8">
                    <h1 class="text-3xl md:text-5xl font-extrabold text-white">Contact</h1>
                    <p class="mt-3 text-gray-400 text-sm md:text-base leading-relaxed">Crystl Labs is a one-person studio in Siheung-si, Gyeonggi-do, South Korea. There is no support desk and no ticket queue &mdash; mail goes straight to the person who wrote the code.</p>
                </header>

                <div class="grid gap-4 md:grid-cols-2">{card('Support and bug reports', f"""
                            <p>Something broken, a crash, a save file that will not load: {mail}</p>
                            <p class="text-gray-400">Tell us the app name, your device and Android version, and what you did right before it broke. A screenshot beats a description. Replies usually go out within two business days (KST).</p>""", 'brandGreen')}{card('Privacy and your data', f"""
                            <p>Deletion requests, access requests and questions about what an app stores: {mail} with <span class="font-mono text-gray-200">DATA</span> in the subject.</p>
                            <p class="text-gray-400">Most Crystl Labs apps keep everything on your device and we hold no copy to delete. The <a href="privacy.html" class="text-brandBlue hover:text-brandPink underline underline-offset-2 transition-colors">privacy policy</a> says which is which, and <a href="data-deletion.html" class="text-brandBlue hover:text-brandPink underline underline-offset-2 transition-colors">data deletion</a> has the step-by-step.</p>""", 'brandPink')}{card('Press and business', f"""
                            <p>Review copies, interviews, partnership and licensing: {mail} with <span class="font-mono text-gray-200">PRESS</span> in the subject.</p>
                            <p class="text-gray-400">Promo codes for anything on Google Play are available on request. Icons, screenshots and feature graphics can be pulled straight from the <a href="projects.html" class="text-brandBlue hover:text-brandPink underline underline-offset-2 transition-colors">project pages</a>.</p>""")}{card('Corrections', f"""
                            <p>Found a mistake in a <a href="blogs.html" class="text-brandBlue hover:text-brandPink underline underline-offset-2 transition-colors">blog post</a>? Say so: {mail} with <span class="font-mono text-gray-200">CORRECTION</span> in the subject.</p>
                            <p class="text-gray-400">Every number published here comes from a run that was actually made. If one of them is wrong we would rather fix it than keep it, and the post gets a dated note saying what changed.</p>""")}
                </div>

                <div class="mt-6 rounded-2xl border border-white/10 bg-panelBg/40 p-5 md:p-6">
                    <h2 class="font-mono text-[11px] uppercase tracking-widest text-gray-500 mb-3">Elsewhere</h2>
                    <div class="flex flex-wrap gap-2.5 font-mono text-xs">
                        <a href="https://t.me/crystllabsTG" class="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-gray-300 hover:text-white hover:border-brandPink/40 transition-colors">Telegram &mdash; community</a>
                        <a href="https://x.com/crystllabs" class="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-gray-300 hover:text-white hover:border-brandPink/40 transition-colors">X &mdash; @crystllabs</a>
                        <a href="https://x.com/ap39ap39" class="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-gray-300 hover:text-white hover:border-brandPink/40 transition-colors">X &mdash; @ap39ap39 (dev)</a>
                        <a href="https://ap39.crystllabs.com/" class="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-gray-300 hover:text-white hover:border-brandPink/40 transition-colors">ap39 &mdash; personal site</a>
                    </div>
                    <p class="mt-4 text-xs text-gray-500 leading-relaxed">Mail is the only channel that is checked every day. Social replies are best-effort. We do not accept unsolicited game pitches, and we do not buy backlinks, guest posts or sponsored placements &mdash; those mails are deleted unread.</p>
                </div>
            </div>
''' + TAIL


REDIRECT = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="robots" content="noindex">
<!-- {why} -->
<meta http-equiv="refresh" content="0; url={to}">
<link rel="canonical" href="{canonical}">
<style>
  body{{background:#0a0a12;color:#e8e8ef;font:16px/1.6 system-ui,-apple-system,Segoe UI,sans-serif;
       display:flex;align-items:center;justify-content:center;height:100vh;margin:0;text-align:center}}
  a{{color:#3B82F6}}
</style>
</head>
<body>
  <p>This page moved.<br><a href="{to}">Continue to {label}.</a></p>
  <script>location.replace("{to}");</script>
</body>
</html>
'''


def main():
    out = os.path.join(ROOT, 'contact.html')
    with open(out, 'w', encoding='utf-8', newline='') as f:
        f.write(render_contact())
    print('[PAGE] contact.html')

    # ceo-blog.html shipped one placeholder post ("Untitled Dispatch") whose only
    # link was a 404 to ceo/ceo_template.html. An orphan page with no content and
    # a dead link is exactly what a policy review penalises, so it now forwards to
    # the real blog instead of being indexed.
    with open(os.path.join(ROOT, 'ceo-blog.html'), 'w', encoding='utf-8', newline='') as f:
        f.write(REDIRECT.format(
            title='Crystl Labs', to='blogs.html', label='the blog',
            canonical=f'{SITE}/blogs.html',
            why='Placeholder CEO page retired; its only post was never written.'))
    print('[PAGE] ceo-blog.html -> redirect to blogs.html')


if __name__ == '__main__':
    main()
