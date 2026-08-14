# Crystl Labs — Google Play developer page

**Created:** 2026-07-26
**Console location:** Play Console → Developer account → **Developer profile** → Developer page
**Status:** ✅ **UNBLOCKED 2026-07-30** — Water Polo Smash is live. Page not created yet.

---

## ~~Blocker~~ Cleared 2026-07-30

Google requires **at least one published app** before a developer page can be
created. ~~Water Polo Smash was submitted 2026-07-26 and is still in review, so the
page cannot be created yet.~~ **Water Polo Smash published 2026-07-30**, so the gate is
open. Everything below is ready to paste — start at the steps section.

Unlike the app store listing, creating this page does **not** touch the app's
review — it is a separate account-level surface. But it cannot exist first.

**Propagation after saving:** ~1 hour for the page URL to preview, up to **24 hours**
before Play users see it. Later edits: ~1 hour.

---

## Fields

| Field | Spec | Value / file | Ready |
|---|---|---|---|
| Developer icon | 512x512, 32-bit PNG | `../favicon.png` (512x512, 32bpp ARGB) | ✅ meets spec as-is |
| Header image | 4096x2304, JPG or 24-bit PNG, **no alpha** | `dev_header_4096x2304_b.png` | ✅ generated, RGB (no alpha) |
| Promotional text | 140 chars max | see below | ✅ pick one |
| Website | URL | `https://crystllabs.com` | ✅ |
| Featured app | one app | Water Polo Smash | ✅ (only published app) |

### Header image — two variants generated

- **`dev_header_4096x2304_b.png`** — logo + `CRYSTL LABS` wordmark + tagline. **Recommended.**
- `dev_header_4096x2304_a.png` — logo only, atmospheric, no text.

Both are brand-accurate: `#0a0a12` base, the site's `#D946EF → #A78BFA → #3B82F6`
gradient, neon crystal from `favicon.png`. Content sits in the vertical centre so
Play's cropping across form factors cannot cut the lockup.

> Source logo is only 512px, so it is LANCZOS-upscaled with a bloom pass that reads
> as intentional neon glow. If a vector or high-res crystal ever exists, regenerate
> from it — script is at `make_header.py` in the session scratchpad, worth copying
> into this repo if the page gets rebuilt.

### Promotional text (140 max) — pick one

| # | Chars | Text |
|---|---|---|
| A | 118 | Elegant worlds, deeply simulated. An indie studio building sports arcades, detective mysteries and systems-heavy sims. |
| B | 110 | Independent game studio in South Korea. Sports arcades, phone-forensics mysteries and deeply simulated worlds. |
| C | 122 | Small games, deep systems. Swipe-to-score sports, crime mysteries you solve through a victim's phone, and city-scale sims. |
| D | 33 | Elegant worlds, deeply simulated. |

**Recommendation: A.** Leads with the site tagline so the page and crystllabs.com
match, then says concretely what you make. B is the fallback if you would rather
foreground being Korea-based. D is too thin to carry a page on its own.

> Caveat: A and C name detective/crime games that are not published yet. Accurate
> as a studio description, but if you would rather only describe shipped work, use
> B until Murder Phone is live.

---

## Steps (day one after launch)

1. Confirm Water Polo Smash shows **Published** on the Play Console dashboard.
2. Play Console → Developer account → Developer profile → Developer page.
3. Upload `../favicon.png` as the developer icon.
4. Upload `dev_header_4096x2304_b.png` as the header image.
5. Paste promotional text (option A).
6. Website: `https://crystllabs.com`
7. Featured app: Water Polo Smash.
8. Save. Preview the URL after ~1 hour; check public display after 24 hours.
9. Add the developer page URL to crystllabs.com (footer or `personnel.html`).

### Translations
Promotional text supports per-language translations. Korean is worth adding
alongside the KO app listing (see `../../water-polo-strike-android/store-listing/LISTING_TODO.md`).
Not yet drafted.
