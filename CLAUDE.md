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

## Style

- Match the existing code: plain ES5-compatible JavaScript in one IIFE, CSS custom
  properties for the palette, Hungarian comments.
- Brand palette lives in `:root` in `styles.css`. Deep green `#14402a`, gold `#d8b45c`,
  cream `#f6efdf`. Do not introduce new accent colours casually.
- Avoid the generic AI look: no purple gradients, no glassmorphism, no bento grids.
  The design follows the restaurant's own logo, colours and food photography.

## Workflow

- **Small, single-purpose commits.** One feature or fix per commit.
- Review the whole diff before committing — understand every change.
- After a change, verify in the browser at 320 / 390 / 1280 px in **both languages**,
  and check the console is clean.
- `bash tests/live-check.sh` smoke-tests the deployed site after a release.

## Out of scope

Do not add analytics beyond the existing privacy-friendly setup, tracking pixels,
cookie-based personalisation, chat widgets, or third-party embeds that load
scripts — each one costs performance and privacy. The Google Maps embed and
Google Fonts are the accepted exceptions.
