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
2. **No `innerHTML`, ever.** There is no runtime templating left in `script.js` —
   the two pages are generated, not translated in the browser — so nothing needs
   to assign HTML. Any future dynamic content goes through `textContent` or
   `createElement`. The audit fails on any `.innerHTML =` in the file. A sanitiser
   used to guard this path and silently ate the privacy-notice link for weeks; the
   path is gone now, and it should stay gone.

3. **Every `<img>` needs a meaningful `alt`.** Menu thumbnails also need `loading="lazy"`.
4. **Bilingual by default.** New user-facing copy needs a `data-en` attribute.
   Hungarian is the base language in the markup.
   **`data-en` replaces the element's whole contents, not just its text** — put it
   on a `<span>` around the text, never on an element that also holds a field, an
   image or a nested element. Attributes need `data-en-alt` / `data-en-aria-label`.
   Three separate bugs came from this; the audit now enforces it. See `MISTAKES.md`.
5. **Hungarian copy must read as native Hungarian**, not as a translation of the
   English. No truncated fragments as headings, no clumsy word repetition.
6. **Two test layers, and both must pass.**
   - `python3 tests/audit.py` — 55 checks, no dependencies, runs in a second,
     wired into the pre-commit hook. Reads the files as text.
   - `tests/render-check.py` — 45 checks in a real browser, in CI on every push.
     Reads what the browser actually *produces*.

   The live site gets the same browser pass weekly in CI
   (`tests/render-check.py https://khrawpakthai.com`), which is what catches a bad
   deploy or a drifted Netlify setting.

   Quarterly — or before a campaign, or when the law moves — run the agent sweep:
   `.claude/workflows/site-sweep.js`. Five lenses (external listings, legal, Hungarian
   copy, security surface, accessibility), each finding adversarially refuted before it
   reaches anyone. **Every confirmed finding becomes a check in one of the two layers
   above**, or the same sweep will keep rediscovering it forever. Not weekly: agents
   cost money and produce false positives; the two test layers are free and do not.

   The second layer exists because the first one cannot see rendering bugs by
   construction. Seven of them lived here for three weeks: the English page
   relabelled itself Hungarian, 36 alt texts stayed Hungarian, a form field
   vanished, the menu photos were unreachable by keyboard, and the sanitiser
   quietly ate the privacy-notice link. Every HTML source was correct. **If a bug
   can only be seen in the rendered page, it belongs in `render-check.py`.**
7. **No review text on the site — the rating only.** Between
   `<!-- REVIEWS:START -->` and `<!-- REVIEWS:END -->` goes the Google rating and a
   link, never review text: not from an API, not copied by hand, never a
   translation. Any one of these is sufficient on its own:
   - Maps Platform Terms §3.2.3(a)(iii) forbid copying or storing user reviews;
     only `place_id` and coordinates may be cached. A Places-API updater was built
     and removed on 2026-08-25 for this. **Do not rebuild it.**
   - The reviewer holds the copyright; an English translation of a Hungarian
     review is a derivative work (Szjt. 29. §) we may not publish.
   - It earns little — people check ratings on Google anyway.

   If automation is ever wanted, the sanctioned route is the Google Business
   Profile API (a business reading its own reviews): OAuth, separate approval.

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

## Errors: fail loud, never fake

Preference order when something cannot be done: it really works → a **visible**
fallback that says it is degraded → a clear error somebody can fix → **never**
silent degradation that looks fine and is not.

A signalled fallback is fine; a hidden one costs an afternoon three days later.
No empty `catch {}`, no invented data standing in for a failed fetch, no reporting
a step as done when it fell back.

## Mistakes log

`MISTAKES.md` records what broke silently or broke twice: what happened, the root
cause, and what now prevents it. Newest first. When the same pattern appears
repeatedly, distil it into a one-line rule above — the log keeps the reasoning so
the rule does not get undone later by someone who has forgotten why it exists.

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

## Out of scope

Do not add analytics beyond the existing privacy-friendly setup, tracking pixels,
cookie-based personalisation, chat widgets, or third-party embeds that load
scripts — each one costs performance and privacy. The Google Maps embed and
Google Fonts are the accepted exceptions.
