# Third-round review — technical and legal — Khraw Pak Thai restaurant website

**Be adversarial. I want disagreement, not encouragement.** This project has been reviewed twice by AI models (you were one of them). I acted on almost everything. This third round has two jobs:

1. Catch what is still wrong after those fixes.
2. Tell me if any of the fixes were **wrong or incomplete** — a bad fix is worse than no fix, because it looks closed.

A parallel prompt is going to a different model focused on the commercial and live-web side. **Your focus is code, architecture, legal text and correctness.** Do not spend your effort on marketing advice.

---

## ⚠️ Read this first: the live site is NOT the thing under review

**khrawpakthai.com still serves an old build.** 22 commits are on GitHub, committed and pushed, but undeployed — Netlify's free tier deploy credits ran out and the billing cycle has not renewed. I verified this an hour ago:

```
/                 200   (old build)
/en/              404
/adatvedelem/     404
/en/privacy/      404
/404.html         404
/llms.txt         404
Headers: HSTS, nosniff, Referrer-Policy, X-Frame-Options present — no CSP
Live HTML still contains: fonts.googleapis.com, an auto-loading Maps iframe
```

**All of that is fixed in the repository and none of it is deployed.** Round one wasted most of an answer on this gap. Please do not repeat it. Review what is described below and what is in the repo — that is what goes live the moment credits return.

Code is public: **github.com/somogyif/khraw-pak-thai**

---

## The project in one paragraph

Static website for a Thai–Hungarian fusion restaurant in Budapest, next to Heroes' Square. Hand-written HTML/CSS/JS, no framework, no build step at deploy, zero npm dependencies. Hungarian company (Felba Food Kft.), so GDPR and ePrivacy apply. No payments, no accounts, no database, no backend of ours. Hungarian at `/`, English at `/en/`. Netlify hosting, GitHub Actions CI. Built by directing an AI coding assistant; I am not a developer, but I owned every architecture and content decision.

**Current measurements** (taken today, not from memory):

| | |
|---|---|
| `site/index.html` | 785 lines, 62 `<img>`, 277 `data-en` attributes |
| `site/en/index.html` | 816 lines, generated |
| `site/styles.css` | 396 lines |
| `site/script.js` | 146 lines |
| `scripts/build-en.py` | 178 lines |
| `tests/audit.py` | 245 lines, 47 checks, all green |
| Deployed weight | 7.4 MB, of which 7.0 MB images, 180 KB fonts |

---

## What changed after round two

| Change | Driven by |
|---|---|
| **Pushed 13 local commits.** The sharpest finding of round two was about process, not code: Netlify's credit limit blocks *deploys*, not `git push`. Work was sitting on a laptop where neither CI nor a reviewer could see it. | Reviewer catch |
| **Retention rewritten from a bare number to a criterion:** "12 months from the last correspondence, where no contract follows", justified in the notice by the seasonality of event enquiries (an enquiry often returns for the same period next year). The 8-year accounting rule is now scoped to accounting records only, not the whole email thread. | Round-two question 4 |
| **Allergies reframed** from "please do not write them here" to "let's take allergies and dietary needs by phone, so we record them accurately". Same effect on Art. 9 data — we do not solicit it — without sounding like a restaurant that does not want to hear about your allergy. | Round-two question 3 |
| **Removed `aggregateRating` and `ReserveAction`** from the JSON-LD. `OrderAction` → Wolt stays; that one is real. | Round one |
| **HSTS stated explicitly** with `includeSubDomains` rather than relying on the platform default. | Round one |
| **US transfer basis named properly:** EU–US Data Privacy Framework adequacy decision, SCCs as fallback. | Round one |
| **Dropped three CI checks** that only asserted a symbol still existed in `script.js` — tests that could not fail for a real reason. The one that catches actual regression (no raw `innerHTML` assignment outside the inert template parse) stays. | Round-two question 2 |
| **Documentation drift now fails the build.** This is the second time the project documents fell behind the code, so a written rule was evidently not enough. CI now asserts that the check count quoted in the docs matches reality, and that no document references something removed from the code unless the sentence says it was removed. It caught two stale claims on its first run. | My own finding |
| **`format-detection` meta** so iOS stops rewriting numbers around `tel:` links. | Round two |
| **Verified rather than assumed:** the 12% service charge is disclosed on the menu, and `og:image` is a correct 1200×630. Two flagged concerns that were already fine. | Round two |

---

## Current architecture

### Bilingual: one Hungarian source, generated English

Hungarian is the source of truth. Every translatable element carries a `data-en` attribute:

```html
<span class="mi-name" data-en="Beef stew">Marhapörkölt</span>
```

`scripts/build-en.py` reads the Hungarian HTML and, with a **regex**, lifts each `data-en` value into the visible text, drops the attribute, rewrites relative asset paths to root-relative (because `/en/` is a subdirectory), swaps meta/OG/canonical to English, converts the language toggle into a link back to `/`, and rebuilds the FAQ JSON-LD from the translated questions. The core is:

```python
pattern = re.compile(
    r'<(?P<tag>[a-zA-Z0-9]+)(?P<before>[^>]*?)\sdata-en="(?P<en>[^"]*)"(?P<after>[^>]*)>'
    r'(?P<body>.*?)</(?P=tag)>', re.S)
for _ in range(12):
    page, n = pattern.subn(repl, page)
    if not n: break
```

CI fails if the committed English page differs from what the generator produces (`--check`). Reciprocal `hreflang` (hu / en / x-default) plus self-referencing canonicals on both pages, mirrored in the sitemap.

### The sanitiser

The language toggle used to do `el.innerHTML = el.getAttribute('data-en')`. It now parses inside an inert `<template>` and filters against allowlists — `BR EM STRONG SMALL SPAN B I` for tags, `class` for attributes — unwrapping disallowed elements to text before `replaceChildren()`. All content it processes is author-written.

### Privacy posture

Fonts self-hosted (14 WOFF2, latin + latin-ext). Google Maps replaced with a click-to-load placeholder. Analytics is Simple Analytics (cookieless, EU-stored). Measured on a fresh load: **zero cookies, zero iframes**; the only browser storage is `localStorage['kpt-lang']` holding the language choice, which I treat as ePrivacy Art. 5(3) strictly necessary. Conclusion: no cookie banner required.

### Headers (`netlify.toml`)

```
Content-Security-Policy: default-src 'self'; script-src 'self' https://scripts.simpleanalyticscdn.com;
  style-src 'self'; font-src 'self'; img-src 'self' data: https://queue.simpleanalyticscdn.com;
  connect-src 'self' https://queue.simpleanalyticscdn.com; frame-src https://www.google.com;
  form-action 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'self'; upgrade-insecure-requests
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
X-Frame-Options: SAMEORIGIN
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), magnetometer=(), gyroscope=()
Cache-Control: public, max-age=31536000, immutable   (on /assets/* and /assets/fonts/*)
```

### Structured data

`Restaurant` (address, geo, opening hours, price range, cuisines, Thai SELECT award), `FAQPage` (5 Q&A), `OrderAction` → Wolt. Nothing else.

### The form

Netlify Forms, honeypot only, no CAPTCHA. Fields: name (required), email (required), phone, event date, guest count, event type (select), free-text message. Posts to the same origin. Submissions arrive in a Google Workspace mailbox.

### Quality gates

47 dependency-free Python checks in CI on every push: broken internal anchors, every referenced image existing and carrying alt text, JSON-LD parsing, phone-number consistency, form integrity (hidden `form-name` + honeypot), hreflang reciprocity, English page freshness, repo-wide secret scan, sanitiser regression guard, documentation-drift guard. Pre-commit hook blocking secrets and audit failures, tested with a planted fake key. Weekly live smoke test.

### Accessibility

Contrast measured across the palette (worst case 5.9:1 against a 4.5 requirement), `:focus-visible` rings, intrinsic `width`/`height` on every image, `loading="lazy"` on menu thumbnails, `fetchpriority="high"` on the hero.

---

## Specific things I want you to attack

### 1. A consent-wording problem I found myself — am I right, and what is the correct fix?

Under the form's submit button, the Hungarian reads:

> „A küldéssel elfogadod az adatkezelési tájékoztatónkat."
> *(By sending this you accept our privacy notice.)*

I think this is wrong. A privacy notice under Art. 13 is **information you are given**, not a document you *accept*. Wording it as acceptance implies consent (Art. 6(1)(a)) as the legal basis — which **contradicts** the notice itself, where the stated basis is Art. 6(1)(b) pre-contractual steps falling back to 6(1)(f). It also manufactures a consent that was never freely given, since the form cannot be sent without it.

My instinct is to change it to a plain pointer — "how we handle your data: privacy notice" — with no acceptance language at all. **Is that right? Is there a case for keeping acceptance wording? Is there a Hungarian-practice reason (NAIH guidance, common local drafting) that cuts the other way?** Give me the exact wording you would use, in Hungarian and English.

### 2. The generator — replace it or keep it?

Regex-based HTML rewriting is the part I trust least. Round two split on this. Concretely: **construct an input that breaks it.** Nested identical tags, a `data-en` containing `>` or a quote, an element with `data-en` whose body contains the same tag name, attribute order, self-closing elements. Then tell me whether the `--check` CI freshness guard actually catches such a break or merely locks in the corrupted output.

If it should be replaced: with what, given no npm and no build step at deploy? A Python templating engine run locally with committed output is the obvious answer — but that splits content out of the HTML into data files, which makes the site harder for a non-developer to edit in three years. **Which trade-off is correct at 277 translatable strings?**

### 3. The CSP

`frame-src https://www.google.com` exists solely for the post-click map. `style-src 'self'` with no `'unsafe-inline'` — verify that is actually consistent with the site working (are there inline styles or a `style="..."` attribute anywhere that would break?). Is `frame-ancestors 'self'` plus `X-Frame-Options` redundant in a way that matters? What is missing — `form-action` is set, but should `frame-src` be `child-src`-scoped, or the map moved to a sandboxed iframe? Is `img-src data:` a real weakness here?

### 4. Retention and the notice text

The retention criterion is now "12 months from last correspondence, where no contract follows", justified by seasonality. **Is a seasonality argument a defensible Art. 5(1)(e) storage-limitation justification, or is it post-hoc rationalisation of a number I picked?** What would a Hungarian DPO actually write?

Separately: is "Netlify under the EU–US Data Privacy Framework adequacy decision, SCCs as fallback" **accurate**? Netlify's own DPA terms are what matter — check whether Netlify, Inc. is actually on the DPF list, and tell me if the fallback framing is legally coherent or just belt-and-braces noise.

### 5. Reviews on the page — still undecided

Four Google reviews are quoted on the page with the reviewer's name, a link to the listing, and a visible line saying where they come from. Three are Hungarian originals with my English translations in `data-en`; one is English originally.

I built and then **deleted** a Places API automation once the Maps Platform Terms turned out to forbid caching review text (§3.2.3(a)(iii) names "user reviews" among content that must not be copied or stored; the Service Specific Terms permit caching only `place_id` and coordinates).

Both previous reviewers said drop the quotes and show only the rating with a link. **I have not decided.** Arguments I want tested: (a) is hand-copying meaningfully different from API caching under those terms, or is that a distinction that does not hold? (b) the reviewer owns the copyright to their words regardless of Google's terms — does short quotation with attribution survive that? (c) **does translating a Hungarian review into English make it worse** — is that a derivative work I have no right to make? This last one nobody has addressed and I suspect it is the strongest argument against.

### 6. Images — 7 MB, and I keep deferring it

62 images, no WebP/AVIF, no `srcset`. Lazy-loaded below the fold, intrinsic dimensions everywhere so no layout shift. Without a build pipeline the options are: commit WebP derivatives and hand-write `<picture>`, generate them with another local script (see question 2), or just re-compress the JPEGs harder.

**What is the actual threshold where this stops mattering for a restaurant site?** Give me a number — a real LCP target on a Hungarian 4G connection — not "smaller is better". And tell me which of the three options you would pick.

### 7. What is missing that I have not thought of at all?

Assume I have tunnel vision from weeks on this. This is the question I most want answered, and the one two rounds of review have answered least well.

---

## What I do not want

- Advice to add a framework, npm, a CMS or a build step. Zero dependencies is a deliberate property, and I will not trade it without an argument that survives "a non-developer must be able to open this in three years".
- Advice about the live site's old build. See the warning at the top.
- Encouragement. If a section is fine, one line: "fine". Spend the words on what is broken.
