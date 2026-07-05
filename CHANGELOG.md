# Changelog

All notable changes to the Crystl Labs website are documented here.

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
