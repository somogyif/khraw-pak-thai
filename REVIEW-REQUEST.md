# Peer review request — Khraw Pak Thai restaurant website

**I am asking you to find what is wrong with this project.** Please be adversarial rather than encouraging. I have already had one AI assistant build and audit this; I want a second and third opinion specifically to catch what that process missed. Praise is not useful to me here — disagreement is.

If you think a decision below is wrong, say so directly and say why. If you are uncertain, say you are uncertain rather than guessing confidently. If something is fine, one line is enough; spend your effort on the problems.

---

## 1. What this is

The public website of **Khraw Pak Thai**, a Thai–Hungarian fusion restaurant in Budapest, next to Heroes' Square (a UNESCO site with heavy tourist traffic). It is live at **khrawpakthai.com**.

Business context that shapes every decision:

- A single-location restaurant. The goal is more guests walking in, ordering on Wolt, and enquiring about events.
- Two audiences: Hungarian locals, and English-speaking tourists.
- 4.2★ / 76 Google reviews. Thai SELECT certified (a Royal Thai Government authenticity mark).
- The operator is a Hungarian company (Felba Food Kft.), so **EU law applies** — GDPR, ePrivacy.
- It replaced a page-builder one-pager whose `<title>` was the placeholder `Weboldal HU`.

**The site takes no payments, has no user accounts, no database, and no backend of our own.** It is a marketing site.

---

## 2. Stack and constraints

- **Static HTML/CSS/JS.** No framework, no build step at deploy time, no npm dependencies, no bundler. Deliberate: I wanted something a non-developer could still open and understand in three years.
- **Hosting:** Netlify free tier, deployed from GitHub on push. ~20 production deploys/month budget (credit model).
- **Forms:** Netlify Forms, honeypot only.
- **Analytics:** Simple Analytics (cookieless).
- **Fonts:** self-hosted WOFF2 (Poppins + Karla).
- **Built by directing Claude Code.** I am not a developer. I owned the brand positioning, content, native-Hungarian copy quality and architecture decisions; the AI wrote the code.

Sizes: `index.html` 766 lines, `styles.css` 396, `script.js` 146, `build-en.py` 178, `audit.py` 215. Total deployed weight **7.4 MB**, of which **7.0 MB is images** (14 photos + 48 menu thumbnails) and 180 KB fonts.

---

## 3. Architecture decisions I want challenged

### 3.1 Bilingual: one Hungarian source, generated English

Hungarian lives at `/`, English at `/en/`. Every translatable element in the Hungarian HTML carries a `data-en` attribute:

```html
<h3 data-en="Daily menu">Napi menü</h3>
<span class="mi-name" data-en="Beef stew">Marhapörkölt</span>
```

`scripts/build-en.py` reads the Hungarian file, lifts every `data-en` value into the visible text, drops the attribute, rewrites relative asset paths to root-relative (because `/en/` is a subdirectory), swaps the meta/OG/canonical for English, turns the language toggle into a link back to `/`, and **rebuilds the FAQ JSON-LD from the translated questions**. CI fails if the committed English page differs from what the generator produces (`--check`).

Reciprocal hreflang on both pages:

```html
<link rel="canonical" href="https://khrawpakthai.com/">
<link rel="alternate" hreflang="hu" href="https://khrawpakthai.com/">
<link rel="alternate" hreflang="en" href="https://khrawpakthai.com/en/">
<link rel="alternate" hreflang="x-default" href="https://khrawpakthai.com/">
```

**Questions for you:** Is a generated second language sane for a site this size, or is it cleverness that will rot? The regex-based HTML rewriting in `build-en.py` is the part I trust least — where does that break? Is the `data-en` attribute approach doubling my HTML payload for no good reason? Does the toggle still make sense as a link now that the pages are separate documents?

### 3.2 The sanitiser

The language toggle used to do `el.innerHTML = el.getAttribute('data-en')`. It now parses inside an inert `<template>` and filters against allowlists:

```js
var ALLOWED_TAGS = { BR:1, EM:1, STRONG:1, SMALL:1, SPAN:1, B:1, I:1 };
var ALLOWED_ATTRS = { class:1 };
// parse in <template>, walk the tree, unwrap disallowed elements to text,
// strip every attribute not in the allowlist, then replaceChildren()
```

The content it processes is entirely author-written (my own `data-en` attributes). **Is this security theatre on a static site with no user-generated content, or justified defence in depth?** I added it partly because a future feature (pulling in reviews) would have fed external text through the same path — but that feature has since been removed (see 3.5).

### 3.3 Structured data

`Restaurant` (address, geo, opening hours, price range, cuisines, award), `FAQPage`, plus `AggregateRating`, `OrderAction` and `ReserveAction`.

**I know `AggregateRating` on your own site can never produce star snippets** — Google's review snippet documentation says self-serving reviews are ineligible. I left it in anyway because the rating is genuinely displayed on the page. **Is leaving it actively harmful (spam signal risk), merely useless, or fine?** Same question for `ReserveAction` pointing at an on-page anchor rather than a real Actions Center integration.

### 3.4 Map loaded on request

The Google Maps iframe used to load on page view, setting Google cookies before any consent. It is now a styled placeholder with a button; the iframe is injected on click. Measured on a fresh load: **zero cookies, zero iframes**, the only browser storage is `localStorage['kpt-lang']` holding the language choice.

My conclusion was that **no cookie banner is required**, because the only storage falls under the ePrivacy Art. 5(3) "strictly necessary" exemption (remembering a user-selected language). **Is that reading correct?** Note the CSP still contains `frame-src https://www.google.com` for the post-click case.

### 3.5 A feature I built and then deleted

I built a scheduled GitHub Action that pulled fresh Google reviews via the Places API, filtered for 5★ and minimum length, escaped them, and published them. It worked end to end.

Then I read the terms properly: Maps Platform Terms §3.2.3(a)(iii) names "user reviews" among content that must not be copied or stored, and the Places API Service Specific Terms allow caching only `place_id` and coordinates. So I deleted the script, disabled the workflow, and wrote the reason into the repo's rules file.

**The four reviews currently on the page were copied from Google Maps by hand, with attribution.** That is not an API cache, but it is still someone else's text on my site. **Is the manual version actually clean, or am I drawing a distinction that does not hold?** What would the correct approach be for a small restaurant that wants social proof on its own page?

### 3.6 Security headers

```
Content-Security-Policy: default-src 'self'; script-src 'self' https://scripts.simpleanalyticscdn.com;
  style-src 'self'; font-src 'self'; img-src 'self' data: https://queue.simpleanalyticscdn.com;
  connect-src 'self' https://queue.simpleanalyticscdn.com; frame-src https://www.google.com;
  form-action 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'self';
  upgrade-insecure-requests
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
X-Frame-Options: SAMEORIGIN
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), magnetometer=(), gyroscope=()
```

No HSTS. `form-action 'self'` with Netlify Forms posting to the same origin. **What is wrong or missing here?** Is `frame-ancestors 'self'` plus `X-Frame-Options` redundant in a way that matters?

### 3.7 The DNS cutover

The domain's DNS stayed at the existing registrar. Only the apex and `www` A records were repointed to Netlify's load balancer (`75.2.60.5`); every mail record (Google Workspace MX, SPF, and the `mail`/`webmail`/`smtp`/`imap`/`pop3`/`autodiscover` entries) was left untouched, rather than accepting Netlify's offer to take over the nameservers.

**Was declining Netlify DNS the right call, or did I trade a real benefit (ALIAS/ANAME, CDN behaviour on the apex) for a risk I was overestimating?** Netlify's own dashboard warned that an apex primary domain does not get the full CDN advantage.

---

## 4. Quality gates in place

- **46 automated checks** in `tests/audit.py`, dependency-free, run in CI on every push: broken internal anchors, every referenced image existing and carrying alt text, JSON-LD parsing, phone-number consistency across the page, form integrity (hidden `form-name` + honeypot), hreflang reciprocity, English page freshness, repo-wide secret scan, and a regression guard asserting the sanitiser is still wired in.
- **Pre-commit hook** blocking commits that carry a secret or fail the audit (tested with a planted fake key).
- **Weekly live smoke test** (`tests/live-check.sh`): status codes, redirects, security headers, sitemap, robots, favicon.
- **`CLAUDE.md`** recording architecture rules so future changes inherit them.

**Where are the gaps?** There are no unit tests for `build-en.py` or the sanitiser, no HTML validation, no broken-external-link check, no Lighthouse budget, and no accessibility automation beyond hand-measured contrast. Which of those actually matter at this scale, and which would be busywork?

---

## 5. Compliance position

- **Imprint** in the footer of every page: company name, registered seat, company registration number, VAT number, email, phone.
- **Privacy notice** at `/adatvedelem/` and `/en/privacy/`, linked from the footer and directly under the form's submit button. Covers: controller identity, what the form collects, legal basis (Art. 6(1)(b) pre-contractual steps, falling back to 6(1)(f) legitimate interest), retention (1 year for enquiries, 8 years for accounting records), processors (Netlify under SCCs, Google Workspace, Simple Analytics), data subject rights, and NAIH for complaints.
- The form **does not ask** for allergies or dietary needs, and the notice explicitly asks people not to put health data in the free-text field — to avoid processing Art. 9 special category data.
- **Google Fonts self-hosted** after the 2022 Munich ruling (LG München I, 3 O 17493/20) on passing visitor IPs to Google.
- **Allergen information** signposted on the menu per Regulation 1169/2011 ("ask our chefs").

**Where is this thin?** I am specifically unsure about: the 1-year retention figure (I picked it, it is not derived from anything), whether Netlify Forms in the US is adequately covered by "SCCs" as a one-line claim, whether the health-data disclaimer actually protects me if someone types an allergy anyway, and whether a restaurant taking event enquiries needs booking terms and a Consumer Rights Directive Art. 16(l) withdrawal-exemption statement even when no money changes hands on the site.

---

## 6. What I already know is imperfect

Do not spend effort on these unless you think I am wrong about them:

- **7 MB of images.** Everything is JPEG/PNG; no WebP or AVIF, no `srcset`. Lazy-loaded below the fold, `fetchpriority="high"` on the hero, intrinsic `width`/`height` everywhere so there is no layout shift. I know converting to modern formats is the obvious next win.
- **`llms.txt` exists and probably does nothing.** Google has said publicly it does not support it. It is harmless; I left it.
- **No field performance data.** The site almost certainly has too little traffic for CrUX, so Core Web Vitals are unverified in the wild — only lab-tested.
- **Deploy budget.** The Netlify free tier ran out after a day of many small commits. Now batching.
- **19 commits are waiting to deploy** as of writing, because of that budget.

---

## 7. What I want from you

1. **The biggest thing we got wrong.** One item, argued.
2. **Anything actually broken or risky** — security, legal, or correctness — that the 46 checks would not catch.
3. **Where I over-engineered.** This is a restaurant website; which parts are complexity I will regret?
4. **Where I under-engineered.** What is missing that a paying client would rightly expect?
5. **The commercial view.** Given the goal is more guests through the door, what would move that needle more than anything in this repo? Be blunt if the answer is "none of this — go do Google Business Profile work instead".

The live site is at **khrawpakthai.com** (Hungarian) and **khrawpakthai.com/en/** (English) if you can browse. The code is public at **github.com/somogyif/khraw-pak-thai**.
