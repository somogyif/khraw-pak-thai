# Working rules for this repository

Read before changing anything. Rules are short on purpose — the reasoning behind
them lives in `MISTAKES.md`, so this file stays readable.

## What this is

The public website of **Khraw Pak Thai**, a Thai–Hungarian fusion restaurant next to
Heroes' Square, Budapest. Live at https://khrawpakthai.com

A **marketing site, not an application**: no users, no accounts, no database, no
payments. Keep it that way unless there is a clear reason not to.

## Architecture (do not drift from this)

- **Static files only** — `site/index.html`, `site/styles.css`, `site/script.js`
- **No build step, no framework, no npm dependencies.** If a change seems to need
  one, stop and ask. Zero dependencies is a deliberate property.
- Netlify hosting, deployed from `main`. `site/` is the publish directory.
- The events form is Netlify Forms — there is no backend of ours.

## Hard rules

1. **Never commit secrets.** Not in the repo, not in client-side code, not in git
   history. Sensitive values belong in a GitHub Actions secret or a Netlify
   environment variable. The pre-commit hook and the audit both scan for them, with
   no file exclusions.
2. **No `innerHTML`, ever.** Both pages are generated, so nothing needs to assign
   HTML. Future dynamic content goes through `textContent` or `createElement`. The
   audit fails on any `.innerHTML =`.
3. **Every `<img>` needs a meaningful `alt`.** Menu thumbnails also need `loading="lazy"`.
4. **Bilingual by default.** New copy needs `data-en`; Hungarian is the base language.
   **`data-en` replaces the element's whole contents, not just its text** — put it on
   a `<span>` around the text, never on an element that also holds a field, an image
   or a nested element. Attributes need `data-en-alt` / `data-en-aria-label`.
5. **Hungarian copy must read as native Hungarian**, not as a translation. No
   truncated fragments as headings, no clumsy word repetition.
6. **Two test layers, and both must pass.**
   - `python3 tests/audit.py` — 85 checks, dependency-free, in the pre-commit hook.
     Reads the files as text.
   - `tests/render-check.py` — 62 checks in a real browser, in CI on every push, and
     weekly against production. Reads what the browser *produces*.

   **If a bug can only be seen in the rendered page, it belongs in `render-check.py`.**
7. **No review text on the site — the rating only.** Between `<!-- REVIEWS:START -->`
   and `<!-- REVIEWS:END -->` goes the Google rating and a link. Never review text:
   not from an API, not copied by hand, never a translation. Three independent
   reasons, any one sufficient:
   - Maps Platform Terms §3.2.3(a)(iii) forbid copying or storing user reviews. A
     Places-API updater was built and removed on 2026-08-25. **Do not rebuild it.**
   - The reviewer holds the copyright; an English translation is a derivative work
     (Szjt. 29. §) we may not publish.
   - It earns little — people check ratings on Google anyway.

   The only sanctioned automation is the Google Business Profile API (a business
   reading its own reviews): OAuth, separate approval.
8. **Keep the project documents current.** When a change alters what the site *is* —
   a page, a capability, a removed feature, a compliance decision — update
   `PROJEKT-OSSZEFOGLALO.md`, `PROJECT-OVERVIEW.md` and `CASE-STUDY.md` in the same
   commit. Routine tweaks do not need it.
9. **Errors fail loud.** It really works → a **visible** fallback that says it is
   degraded → a clear error somebody can fix → **never** silent degradation that
   looks fine and is not. No empty `catch {}`, no invented data for a failed fetch,
   no reporting a step as done when it fell back.

## Style

- Plain ES5-compatible JavaScript in one IIFE, CSS custom properties, Hungarian comments.
- Palette in `:root`: green `#14402a`, gold `#d8b45c`, cream `#f6efdf`. No new accents casually.
- Avoid the generic AI look: no purple gradients, no glassmorphism, no bento grids.

## Workflow

- **Small, single-purpose commits.** One feature or fix per commit.
- **Batch pushes.** Every push to `main` is a Netlify production deploy, and the free
  plan allows roughly **20 per month**. Commit freely, push related work together.
- Review the whole diff before committing.
- After a change, verify at 320 / 390 / 1280 px in **both languages**, console clean.
- `bash tests/live-check.sh` smoke-tests production after a release.
- Quarterly — or before a campaign, or when the law moves — run
  `.claude/workflows/site-sweep.js`. **Every confirmed finding becomes a check in one
  of the two test layers**, or the sweep rediscovers it forever. Not weekly: agents
  cost money and produce false positives.

## Out of scope

No analytics beyond the current privacy-friendly setup, no tracking pixels, no
cookie-based personalisation, no chat widgets, no third-party script embeds. The
click-to-load Google Maps embed and the self-hosted fonts are the exceptions.

## Mistakes log

`MISTAKES.md` records what broke silently or broke twice: what happened, the root
cause, what prevents it now. Newest first. Repeated patterns graduate into a
one-line rule above; the log keeps the reasoning so the rule is not undone later.
