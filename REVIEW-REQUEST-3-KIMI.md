# Third-round review — Khraw Pak Thai restaurant website

**Be adversarial. I want disagreement, not encouragement.** This project has now been reviewed by two other AI models across three rounds. I acted on almost everything. You are the third opinion in this round, and you are being asked deliberately *after* the other two have reported — so the most useful thing you can do is find what **all of them missed**, and tell me where **their advice was wrong**.

I will list their findings below, including the ones I rejected and the ones I discovered were mistaken. Attack those too.

---

## ⚠️ The live site is not the thing under review

**khrawpakthai.com still serves an old build.** 23 commits are pushed to GitHub but undeployed — Netlify's free-tier deploy credits ran out and the billing cycle has not renewed. Verified today:

```
/  200 (old build)   /en/  404   /adatvedelem/  404   /404.html  404   /llms.txt  404
No CSP header. Live HTML still loads Google Fonts from Google's CDN
and fires a Maps iframe on page load.
```

All of that is fixed in the repo and none of it is deployed. A previous reviewer wasted most of an answer on this gap. **Do not repeat it.** The code is public: **github.com/somogyif/khraw-pak-thai**

---

## The project

Static website for a Thai–Hungarian fusion restaurant in Budapest, next to Heroes' Square. Plain HTML/CSS/JS, no framework, no build step at deploy, zero npm dependencies. Hungarian company (Felba Food Kft.), so GDPR and ePrivacy apply. No payments, no accounts, no database. Hungarian at `/`, English at `/en/` — the English page is **generated** from the Hungarian source by a Python script. Netlify hosting, GitHub Actions CI. Built by directing an AI coding assistant; I am not a developer, but I owned every architecture and content decision.

Measured today:

| | |
|---|---|
| `site/index.html` | 785 lines, 62 `<img>`, 277 `data-en` attributes |
| `site/en/index.html` | generated, 55 KB |
| `site/styles.css` / `site/script.js` | 396 / 158 lines |
| `scripts/build-en.py` / `tests/audit.py` | 205 / 275 lines, **50 checks**, all green |
| Deployed weight | 4.5 MB, of which 2.9 MB is 48 lazy-loaded menu thumbnails |
| **Initial image load** | **564 KB** (56 of 62 images are lazy) |

---

## Architecture

**Bilingual.** Hungarian is the source of truth. Every translatable element carries `data-en`, and every translatable *attribute* carries `data-en-alt` / `data-en-aria-label`:

```html
<span class="mi-name" data-en="Beef stew">Marhapörkölt</span>
<img src="..." alt="Gulyásleves" data-en-alt="Goulash soup">
```

`scripts/build-en.py` reads the Hungarian HTML and, **with regexes**, lifts each `data-en` into the visible text, writes each `data-en-<attr>` into that attribute, drops both, rewrites relative asset paths to root-relative, swaps meta/OG/canonical to English, converts the language toggle into a link back to `/`, and rebuilds the FAQ JSON-LD. CI fails if the committed English page differs from what the generator produces.

Reciprocal `hreflang` (hu/en/x-default), self-referencing canonicals, mirrored in the sitemap.

**A quirk I want you to judge.** The Hungarian page *also* has a runtime language toggle (a button) that translates the page in place via `data-en`, without navigating. The English page has no button — its toggle is a link back to `/`. So English content can appear at **two** URLs: `/en/` (generated, canonical English) and `/` (toggled in the browser, canonical Hungarian). I discovered this today and have not decided what to do. See open question 1.

**Privacy.** Fonts self-hosted. Google Maps replaced with a click-to-load placeholder, and the injected iframe is now `sandbox`ed. Analytics is Simple Analytics (cookieless, EU-stored). Measured on a fresh load: zero cookies, zero iframes. The only browser storage is `localStorage['kpt-lang']`, written **only** on the page that has the toggle. Conclusion: no cookie banner required.

**Headers.** `default-src 'self'`; Simple Analytics allowed for script/img/connect; `frame-src https://www.google.com` for the post-click map; `form-action 'self'`; `object-src 'none'`; `base-uri 'self'`; `frame-ancestors 'self'`; HSTS with `includeSubDomains`; nosniff; `Referrer-Policy: strict-origin-when-cross-origin`; `X-Frame-Options: SAMEORIGIN`; `Permissions-Policy` locking camera/mic/geolocation/payment. Verified: zero inline scripts, zero inline event handlers, zero inline `style` attributes, so `script-src 'self'` and `style-src 'self'` hold without `'unsafe-inline'`.

**Structured data.** `Restaurant`, `FAQPage`, `OrderAction` → Wolt. `aggregateRating` and `ReserveAction` were removed after round one.

**Form.** Netlify Forms, honeypot only, no CAPTCHA. Name, email, phone, date, guest count, event type, free-text message. Submissions land in a Google Workspace mailbox.

**Legal.** Imprint on every page including the hosting provider (added today, per Ekertv. 4. § h)). Bilingual privacy notice at `/adatvedelem/` and `/en/privacy/`: controller, what the form collects, legal basis (Art. 6(1)(b) pre-contractual, falling back to 6(1)(f)), retention (12 months from last correspondence, seasonality-justified; 8 years for accounting records only), processors (Netlify under the EU–US DPF, Google Ireland Limited, Simple Analytics), rights, NAIH.

---

## What the other two reviewers said this round, and what happened

Attack any row where you think I or they got it wrong.

| Finding | Source | What I did |
|---|---|---|
| **"By sending this form you accept our privacy notice" is an illegal consent pattern** — a notice under Art. 13 is information, not a contract, and acceptance wording implies Art. 6(1)(a) consent, contradicting the stated 6(1)(b) basis | I found it, the other model confirmed | **Fixed.** Now a plain pointer with no acceptance language |
| **The regex generator corrupts nested same-tag elements** — the lazy `.*?` stops at the first closing tag, leaving a dangling one | Reviewer | **Verified true.** I reproduced it: `<div data-en="A">x <div>y</div></div>` → `<div>A</div></div>`. Zero such elements exist today. I added a CI check that fails if one is ever introduced, plus a tag-balance assertion on the generated page — rather than rewriting the generator |
| **`--check` locks in corruption rather than catching it** | Reviewer | **Correct**, and that is exactly why I added the two checks above instead of trusting it |
| **Hungarian imprint must name the hosting provider** (Ekertv. 4. § h)) | Reviewer | **Verified true** — I doubted it and was wrong. Added Netlify's name, address and contact to every page's imprint |
| **The privacy notice omits Netlify and Google as processors** | Reviewer | **False** — both were already listed. I refined "Google Workspace" to "Google Ireland Limited" |
| **7 MB of images destroys your LCP** | Reviewer | **Overstated.** 56 of 62 images are lazy; real initial image load was 564 KB. I still cut the total from 7.0 MB to 4.5 MB — three photos were stored as **PNG** (1.46 MB), and the Hungarian dishes were 1400×2489 for a 1:1 cropped card. Hero: 432 KB → 188 KB |
| **The client-side sanitiser is dead weight / security theatre** | Three reviewers now | **Rejected — and I think all three are wrong.** 23 of the `data-en` values contain markup (`<em>`, `<br>`). `textContent` would render those as literal text, so the sanitiser is the *rendering path for a feature in use*, not decoration. Removing it means either losing the markup or going back to raw `innerHTML`. **Tell me if I am wrong** |
| **Drop the quoted Google reviews** | Both reviewers, converging | **Done.** The decisive argument was one nobody raised in earlier rounds: translating a Hungarian review into English is a derivative work (Szjt. 29. §) I have no right to publish. Commercially they also convert weakly. The page now shows the rating and links to the listing |
| **A zombie Foodora listing shows the restaurant as CLOSED at the old address** | Reviewer, live-web | **Verified live today** — page still up, `CLOSED`, stale menu. We no longer have a Foodora contract at all, which makes it a removal demand rather than a partner-portal task |
| **The Google listing shows the restaurant nested under "Mirage Medic Hotel"** | Reviewer, live-web | **Real and unwanted** — the restaurant rents the ground-floor space, is independent, and has its own entrance. Being displayed as part of a hotel is actively wrong |
| **Lead with Thai SELECT + location, push "fusion" language lower** | Reviewer | **Undecided.** It conflicts with an explicit decision to emphasise fusion. See open question 3 |

**And one thing all three reviewers missed, which I found while verifying their claims:** on the English page, `document.documentElement.lang` was being overwritten to `"hu"` by a `localStorage` language preference, and the opening-hours indicator rendered in Hungarian. Separately, **36 of 60 `alt` texts and 7 of 8 `aria-label`s were still Hungarian on the English page**, because the generator translated element bodies but not attributes. For a blind English-speaking visitor the entire image layer was in Hungarian. Both fixed today, with a CI check that fails if any Hungarian `alt`/`aria-label` lacks a translation.

---

## Open questions

**1. The two-URL English problem.** English content can appear at `/en/` (canonical) and at `/` (runtime toggle). Options: (a) make the Hungarian toggle a plain link to `/en/`, deleting the runtime translation machinery entirely — which also makes the sanitiser genuinely dead and removes the only browser storage; (b) keep the instant toggle and accept the duplication; (c) something else. **Which, and what is the actual SEO and UX cost of each?**

**2. What did all three of us miss?** Two rounds and three models have now gone over this. The `lang` bug and the untranslated `alt` texts were found by *verifying reviewer claims*, not by any reviewer. Assume more of that class remains. Where would you look?

**3. Positioning.** The site leads with fusion — Thai plus Hungarian classics, one table, everyone eats. A reviewer argues this reads as a dilution flag to anyone searching "authentic Thai Budapest", and that Thai SELECT certification plus proximity to Heroes' Square should come first instead. The restaurant's owner deliberately chose to emphasise fusion. **Who is right, and is there a framing that serves both?**

**4. The 48 menu thumbnails are 2.9 MB** and serve double duty: a 62 px thumbnail and a click-to-open lightbox at up to 720 px. `sips` re-encoding made them *larger*, so they are already efficiently compressed. Without a build pipeline: leave them, or commit downscaled derivatives? **They are lazy-loaded — does this matter at all?**

**5. Retention.** 12 months from last correspondence, justified by the seasonality of event enquiries. **Is a seasonality argument a defensible Art. 5(1)(e) justification, or post-hoc rationalisation of a number I picked?**

**6. Commercially.** Both previous reviewers said: stop polishing the repo, go do Google Business Profile work. I accept that. **Is anything left in the website itself worth doing before I stop?**

---

## What I do not want

- Advice to add a framework, npm, a CMS, or a build step. Zero dependencies is deliberate and I will not trade it without an argument that survives "a non-developer must be able to open this in three years".
- Advice about the live site's old build. See the warning at the top.
- Agreement with the other reviewers for its own sake. Where you think they were wrong, say so.
- Encouragement. If a section is fine, one line.
