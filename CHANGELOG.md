# Changelog

All notable changes to the Crystl Labs website are documented here.

## 2026-08-22

### Added
- **Three more apps are live on Google Play**: Bent FC: Soccer Club Chairman
  (`com.crystllabs.corruptfm`), DORK: Blind Text Adventure (`com.crystllabs.dork`)
  and Mise: Recipe Book & Timers (`com.crystllabs.cooking`). All three were
  carrying an "In playtest" badge and no store link; they now carry the Live badge,
  the store button and their release date. Store links verified against the Play
  developer listing, which is the same ten titles plus Cage of Glory, whose page
  is US-visible but not distributed to Korea.

### Changed
- **The dev logs are a highlight reel, not a reflog.** `build_devlog.py` now drops
  everything that only made sense from inside the work: phase numbers, audit
  rounds, TODO and PLAN ids, notes to self, test and chore commits, code
  identifiers, pixel-level layout tweaks, and any subject with a narrative
  ", and ..." tail. Runs of commits on the same topic collapse to the newest one.
  Every surviving line is still the commit exactly as written, only its
  conventional-commit prefix (`fix:`, `feat(scope):`) is stripped. Across the
  portfolio that is 2,165 raw entries down to 391 kept, of which each page shows
  the newest 12 rather than 40.
- **The per-app intros are shorter.** Seventeen of them ran to a full paragraph or
  more and several pointed at entries the filter now removes; they are two
  sentences each. The DORK intro described the wrong game and has been rewritten.
- **A page earns indexing on its commit count, not its visible log length.** With
  the log filtered, a long-running project with a terse commit style would have
  failed a line-count test while plainly deserving a page.

## 2026-08-16

AdSense rejected the site on 2026-08-14 for **"Low value content."** It was
correct: there were no articles on the domain, 21 near-identical app pages of
roughly 120 words each, and the privacy policy was the longest page on the site.
This release addresses the cause. Indexable surface went from 16 pages / 7,636
words to 43 pages / 39,057 words.

### Added
- **A blog.** 11 posts, 17,430 words, at `blog/<slug>.html`, compiled by the new
  `build_blog.py` from `blog_src/*.json`. Four were already published on the
  `ap39` subdomain and are republished here; that copy now carries a canonical
  pointing at this domain, since the two share a root domain and would otherwise
  read as duplicate content. Seven were recovered from Print-To-PDF exports whose
  Markdown sources no longer exist and whose glyphs had been flattened to vector
  outlines, leaving no text layer to extract.
- **Dev logs on every app page.** `build_devlog.py` reads each project's real git
  history into `devlog_data.json`; `build_apps.py` renders it. Every dated line is
  a commit that exists. Merge commits and noise are dropped, chores are marked and
  hidden. Only the per-app intro in `devlog_intros.json` is written by hand.
- **`contact.html`** — support, privacy, press and corrections, with the response
  times we actually keep, plus Organization JSON-LD.
- **Six projects**: Zero Cool, Bent FC: Tournament Edition, Rug Pull, Office
  Politics, Rich Man Poor Man and Crystl Suite. The first and the last two were
  previously teaser cards in the Frontier and Sites rows; those cards now link
  into full pages.
- A **Writing** section on the home page carrying the three newest posts, so an
  article is reachable from the front page rather than the sidebar alone.
- `build_pages.py` and `patch_chrome.py`, which keep the hand-maintained pages
  from drifting out of sync with the generated ones.

### Changed
- **`personnel.html` is a real About page**, 63 → 309 words, in all three
  languages: what the studio is, how it builds, where your data goes, why it
  writes.
- **Indexing is earned, not assumed.** A page is indexed when it is shipped, or
  its dev log is long enough to read, or its description stands on its own.
  Three pages meet none of those and carry `noindex`. `sitemap.xml` agrees with
  the tags instead of contradicting them.
- The AdSense loader is on **every** page. It used to be on `index.html` alone.
- Store buttons follow the platform. A browser game reads "Play in your browser"
  rather than claiming to be on Google Play, and a finished web tool waiting on
  DNS reads "Coming soon" rather than "In development".
- `ads.txt` gained the nine `subdomain=` declarations it was missing. Without
  them Google does not crawl a subdomain's ads.txt, so that inventory counted as
  unauthorised.

### Fixed
- `ceo-blog.html` shipped a single placeholder post whose only link was a 404 to
  `ceo/ceo_template.html`. It now redirects to the blog and is `noindex`.
- Removed the empty `_posts/ceo` and `_posts/dev` directories.

## 2026-07-31

### Added
- Live-app support in the project data model. `apps_data.json` entries now accept
  `status`, `storeUrl` and `screenshots`; `build_apps.py` turns those into a green
  **Live** badge, a real Google Play button (replacing the dead "In development" chip),
  and a horizontal screenshot strip. Apps without those fields render exactly as before.
- Water Polo Smash is the first live app: store link, Live badge, and 5 screenshots at
  `apps/shots/water-polo-smash/` — the same shots used on the Play listing, resized to
  540px wide JPEG.
- `store_live` i18n string in EN/KO/JA on `index.html` and `projects.html`.

### Changed
- Water Polo Smash moved to first position in Latest Projects. The front-page carousel
  renders only the first 9 of 10 apps, so at its old 9th slot it was the last card shown.
- Water Polo Smash tagline and description rewritten in all three languages. The old copy
  described swimming and passing, which the shipped game does not have — it is a
  drag-to-shoot game.
- Homepage section order: **Sites** now sits above **Frontier**.
- Homepage spacing: the middle section carries `md:mb-12` so the gap under it matches the
  gap under Latest Projects. Previously the second and third sections were both `md:mb-10`.

## 2026-07-05

### Fixed
- Broken logo/favicon references — pages linked to `crystl1.jpg` / `favicon.jpg` but only the `.png` files existed, so the logo and favicon never loaded.
- Non-functional language selector on the blog listing pages (called `switchLang()`, which wasn't defined there).
- Sidebar ("Explorer" panel) was inconsistent across pages — different widths, missing blog links on the legal pages, and the ">> Explorer" label was missing its `>>` prefix on several pages.
- Generated CEO blog posts incorrectly highlighted "dev_senior.log" as the active sidebar item instead of "ceo_executive.log".

### Changed
- Full visual redesign: replaced the retro pixel-art theme (`Press Start 2P`, thick comic borders, hard drop-shadows, neon-everywhere) with a cleaner, modern dark-IDE aesthetic — thin borders, soft shadows, glass panels, and `JetBrains Mono` + `Inter` typography, while keeping the file-explorer/terminal concept and brand accent colors.
- Homepage hero: now reads "Crystl Labs" (large, gradient) with the tagline "Elegant worlds, deeply simulated." underneath.
- Removed the "Core_Logic" section (Data Science / Building Apps cards) from the homepage.
- Removed the footer, top nav "File / Edit / View" items, and the blurb paragraph from the homepage for a cleaner layout; "Run_Tasks" status renamed to "CONNECTED".
- Data deletion page redesigned to match the layout/typography of the Privacy and Terms pages, instead of its own boxed red-bordered treatment.
- Unified typography scale and spacing across all pages (page titles, section headings, body copy) and added the same ambient background glow used on the blog pages to every page.
- Mobile layout overhauled: sidebar is now a collapsible slide-in drawer (hamburger toggle) instead of a stacked full-width block; the menu button stays fixed on screen while scrolling instead of scrolling away with the top bar.
- `publish.py`'s page generator updated to match the new design system so future blog posts inherit it automatically.

### Removed
- Dead/unused i18n dictionary keys left over after content removal (nav labels, footer strings, old hero copy).

### Fixed (later same day)
- Inter's 800 (extrabold) weight wasn't loaded on 5 of the 8 pages (Privacy, Terms, Data Deletion, and the two generated post pages), even though their titles use `font-extrabold` — those titles were rendering as browser-faked bold instead of the true typeface weight. All pages now request the same font weights.

### Changed (later same day)
- Homepage hero simplified again: dropped the three-line "Complex logic. / Elegant worlds. / Deeply simulated." headline in favor of "Crystl Labs" (large, gradient) with "Elegant worlds, deeply simulated." as a single-line tagline underneath; title later sized up further and nudged in slightly from the left edge on desktop.
- Removed the "Explorer" sidebar label entirely (was showing inconsistently across pages before removal) on every page.
- Homepage section labels renamed: "Live_Deployments" → "Projects //", "Transmission_Logs" → "Logs //"; vertical space between the hero tagline and "Projects //" cut in half.
- Header formatting unified across every non-homepage page: dropped the leading `#` on Privacy/Terms/Data Deletion titles and standardized all page and post titles (including blog listings and generated posts) to a trailing `//` — e.g. "Privacy Policy //", "CEO Executive Transmissions //".
- Removed the descriptive blurb paragraph under the title on both blog listing pages (CEO and Dev logs).
- `publish.py` updated again to match: title format, dropped Explorer heading, correct font weights — so future generated posts stay in sync.
