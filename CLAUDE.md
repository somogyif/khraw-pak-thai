# Working rules for this repository

Context for any AI assistant (and for me) working on this codebase.
Read this before making changes.

---

## What this is

The public website of **Khraw Pak Thai**, a Thai–Hungarian fusion restaurant next to
Heroes' Square, Budapest. Live at https://khrawpakthai.com

It is a **marketing site, not an application**. It has no users, no accounts,
no database and no payments. Keep it that way unless there is a clear reason not to.

## Architecture (do not drift from this)

- **Static files only** — `site/index.html`, `site/styles.css`, `site/script.js`
- **No build step, no framework, no npm dependencies.** If a change seems to need
  one, stop and ask first. "Zero dependencies" is a deliberate property, not an accident.
- Hosting: Netlify, deployed from `main` via GitHub. `site/` is the publish directory.
- The contact/events form is handled by Netlify Forms — there is no backend of ours.

## Hard rules

1. **Never commit secrets.** No API keys, tokens or credentials in the repo, in
   client-side code, or in git history. Anything sensitive belongs in a GitHub
   Actions secret or a Netlify environment variable, used server-side only.
2. **Never insert untrusted content as raw HTML.** The HU/EN switch in `script.js`
   routes everything through `sanitizeToFragment()` — an inert `<template>` parse
   plus a tag allowlist (`br em strong small span b i`) and an attribute allowlist
   (`class`). Any future dynamic content (e.g. Google reviews pulled from an API)
   must go through the same path, or through `textContent`.
3. **Every `<img>` needs a meaningful `alt`.** Menu thumbnails also need `loading="lazy"`.
4. **Bilingual by default.** New user-facing copy needs a `data-en` attribute.
   Hungarian is the base language in the markup.
5. **Hungarian copy must read as native Hungarian**, not as a translation of the
   English. No truncated fragments as headings, no clumsy word repetition.
6. **Run `python3 tests/audit.py` before committing.** It must pass.
7. **The review block is generated.** Everything between `<!-- REVIEWS:START -->`
   and `<!-- REVIEWS:END -->` in `site/index.html` is maintained by
   `scripts/update-reviews.py`. Edit the script, not the block — manual edits get
   overwritten on the next scheduled run. Reviews appear in the language they
   were written in — Google's API selects language-appropriate reviews rather
   than translating them. That is deliberate, not a bug.

8. **Keep the project documents current.** When a change alters what the site
   *is* — a new page, a new capability, a removed feature, a compliance decision —
   update `PROJEKT-OSSZEFOGLALO.md`, `PROJECT-OVERVIEW.md` and `CASE-STUDY.md` in
   the same commit. They are used for showcasing the work, so a stale document is
   worse than none. Routine tweaks (copy edits, spacing, a bug fix) do not need it.

## Style

- Match the existing code: plain ES5-compatible JavaScript in one IIFE, CSS custom
  properties for the palette, Hungarian comments.
- Brand palette lives in `:root` in `styles.css`. Deep green `#14402a`, gold `#d8b45c`,
  cream `#f6efdf`. Do not introduce new accent colours casually.
- Avoid the generic AI look: no purple gradients, no glassmorphism, no bento grids.
  The design follows the restaurant's own logo, colours and food photography.

## Workflow

- **Small, single-purpose commits.** One feature or fix per commit.
- **Batch pushes — the deploy budget is the real constraint.** Every push to `main`
  triggers a Netlify production deploy, and on the free plan a deploy costs 15 of the
  300 monthly credits: roughly **20 deploys per month**. The budget ran out on
  2026-08-25 after a day of many small pushes (20 deploys = 300 credits). Commit
  freely, but push related work together rather than one commit at a time. If deploys
  are paused the work is safe on GitHub and ships when the cycle renews. The scheduled
  review update also spends from this budget, but only when it finds something new.
- Review the whole diff before committing — understand every change.
- After a change, verify in the browser at 320 / 390 / 1280 px in **both languages**,
  and check the console is clean.
- `bash tests/live-check.sh` smoke-tests the deployed site after a release.

7. **Never cache Google review text.** The Maps Platform Terms §3.2.3(a)(iii)
   explicitly name "user reviews" among the content that must not be copied or
   stored, and the Places API Service Specific Terms permit caching only
   `place_id` and coordinates. An automated Places-API review updater was built
   and then removed on 2026-08-25 for exactly this reason — do not rebuild it.
   The review block in `site/index.html` is maintained by hand. If the
   restaurant ever wants automation, the sanctioned route is the Google
   Business Profile API (a business accessing its own reviews), which requires
   OAuth and separate Google approval.

## Out of scope

Do not add analytics beyond the existing privacy-friendly setup, tracking pixels,
cookie-based personalisation, chat widgets, or third-party embeds that load
scripts — each one costs performance and privacy. The Google Maps embed and
Google Fonts are the accepted exceptions.
