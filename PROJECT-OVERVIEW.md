# Project Overview — Khraw Pak Thai Restaurant Website

> A complete, from-scratch rebuild of a Budapest restaurant's website: bilingual, SEO-ready, fully responsive, live on a custom domain with continuous deployment. Delivered as a human-directed, AI-assisted build.
>
> **Live:** https://khrawpakthai.com · **Repo:** github.com/somogyif/khraw-pak-thai · **Stack:** static HTML/CSS/JS (no framework, zero dependencies), Netlify, GitHub CI/CD

---

## 1. Context

**Khraw Pak Thai** is an authentic Thai restaurant in Budapest that, after moving next to Heroes' Square (Hősök tere) in early 2026, expanded its offering with Hungarian classics — becoming a Thai–Hungarian fusion kitchen. It holds the **Thai SELECT** certification (an official mark of authentic Thai cuisine awarded by the Royal Thai Government) and a 4.2★ Google rating.

The restaurant already had a website, but it was a page-builder one-pager that undersold the business and worked against it in search and on social. The goal of this project was to **rebuild it into a site that actually converts visitors into guests** — and to bring more customers.

---

## 2. Starting point — audit of the old site

The existing site looked on-brand but had serious gaps, surfaced in an initial audit:

- **Placeholder page title** — the browser/Google title was literally *"Weboldal HU"* ("Website HU").
- **No real menu** — the "Menu" link opened an external Canva design.
- **Opening hours: "Coming soon."**
- **Phone number** was plain text, not tappable.
- **No online ordering or reservation** path.
- **Weak SEO** — missing/placeholder metadata, **no structured data**, no semantic headings, **13 images with no alt text**, broken social-share previews.
- **Slow first paint** (blank screen for several seconds) and a **Canva default favicon**.

Good branding, but leaving both guests and search engines without answers.

---

## 3. Objectives

1. Rebuild from scratch as a fast, hand-coded, SEO-first static site.
2. Put the **full menu with prices** on the site itself.
3. Make it **bilingual (Hungarian / English)**.
4. Sharpen the brand story around a real strength: **authentic Thai (Thai SELECT) + Hungarian classics = something for every group**.
5. Add real conversion paths: **online ordering, events inquiry form, tappable phone, map, live opening status**.
6. Ship it **live on the real domain** with **continuous deployment**.

---

## 4. Approach & process

The project was run as a tight, iterative loop: **direct → build → review on real screenshots → refine**. Content was sourced from real material rather than invented:

| Source | What was extracted | How |
|---|---|---|
| Restaurant's **menu PDF** (20 pages, bilingual, ~35 MB, Canva export) | Full menu structure + prices; **60+ dish photos** | `pdftotext`, `pdfimages`, `pdftoppm` (poppler); Python/Pillow for **CMYK→sRGB** conversion and web optimization |
| **Google Business Profile** | Live rating, review count, opening hours (11:00–22:00 daily), address, phone, **real guest reviews** | Browser automation of Google Maps (incl. cookie-consent handling, sort-by-newest, "view original" for translated reviews) |
| **Owner's terrace photos** (HEIC) | Hungarian dish shots (pörkölt, rántott hús) | `sips` HEIC→JPEG (worked around a macOS Photos-library privacy/TCC block) |
| **Web research** | What Thai SELECT means and why it matters | `WebSearch` / `WebFetch` |
| **Company registry + hotel page** | Legal impresszum (operator, tax no.); building & neighbourhood context | `WebFetch` |

A notable content-quality detail: a new 5★ review was written in **Swedish**; instead of trusting Google's Hungarian auto-translation, the **original Swedish text was pulled and translated accurately** into both HU and EN.

---

## 5. What was built (features)

A single-page site with these sections and capabilities:

- **Hero** — headline, lead, rating badge, Thai SELECT badge, "overlooking Heroes' Square" badge, and an appetizing dish image with a caption chip.
- **Bilingual HU/EN** — a lightweight `data-en` attribute i18n system with a header toggle, `localStorage` persistence, and `<html lang>` switching. Reviews, form labels, and the live open/closed indicator all localize.
- **Thai SELECT section** — explains the government certification as proof of authenticity.
- **Daily lunch menu** — highlighted section (weekdays 11:00–14:00, 3 490 Ft), starter/soup + main.
- **Story** — Thai roots → move next to Heroes' Square → the fusion narrative.
- **"Bold flavours & familiar favourites"** — frames adventurous Thai alongside familiar Hungarian comfort food, with real terrace photos, so mixed groups can share one table.
- **Popular Thai dishes** — image cards.
- **Full menu** — category tabs (Thai / Hungarian / Sides / Desserts / Drinks), prices, **selective lazy-loaded dish thumbnails with a click-to-zoom lightbox** (added only to the less-familiar dishes to reassure guests without bloating the page). Multi-protein prices reordered **ascending** (vegetable → chicken → pork → beef → shrimp) for a clean, consistent look.
- **Reviews** — curated real Google reviews with attribution, HU + EN.
- **Events / catering inquiry form** — a **Netlify Forms** form (name, email, phone, date, guests, type, message) with honeypot spam protection; submissions email the restaurant.
- **FAQ** — with **FAQPage** structured data.
- **Contact** — opening hours with a **live "open now / closed" indicator computed in Budapest time**, tappable phone (`tel:`), Google Maps embed, directions, and a tasteful description of the setting (a 19th-century domed villa overlooking the UNESCO-listed Heroes' Square, steps from Andrássy Avenue, City Park and the Széchenyi Baths).
- **Footer** — legal impresszum (operator Felba Food Kft., seat, tax number).
- **Branded favicon** — built by extracting the Thai temple emblem from the logo and compositing it on the brand green (replacing the old Canva icon).

---

## 6. SEO foundation

- Descriptive `<title>` and meta description; `canonical`.
- **Open Graph + Twitter Card** with a branded `og:image` (fixed the broken social preview; re-scraped via the Facebook Sharing Debugger).
- **JSON-LD structured data**: `Restaurant` (address, geo, hours, price range, cuisines, `acceptsReservations`, award) + `AggregateRating` + `FAQPage`.
- Semantic headings, descriptive `alt` text throughout.
- `sitemap.xml`, `robots.txt`, and a **Google Search Console** verification file.
- Performance-minded: lazy-loaded images, sized/compressed assets, `fetchpriority` on the hero image.

---

## 7. Deployment & infrastructure

- **Repository structured as a showcase repo**: the deployable site lives in `site/`, with docs (README, case study) at the root and a `netlify.toml` (`publish = "site"`).
- **Hosting:** Netlify. First shipped via drag-and-drop for an instant preview, then migrated to **GitHub → Netlify continuous deployment** — every `git push` now auto-deploys.
- **Custom domain** `khrawpakthai.com` connected via DNS at the registrar (Websupport): apex + `www` A records repointed to Netlify (`75.2.60.5`) **without touching the email MX/SPF/mail records** — a careful, email-safe cutover, deliberately keeping DNS external rather than migrating it.
- **HTTPS** via automatic Let's Encrypt; HTTP→HTTPS and `www`→apex redirects.
- Diagnosed and fixed a **"Private → Public" project-visibility** issue (401 "Login Redirect") and verified propagation with `dig` / `curl`.
- Post-launch: Netlify Forms email notifications, SimpleAnalytics (privacy-friendly), and Search Console sitemap submission.

---

## 8. Brand & copywriting

- **Repositioning:** rather than hiding the Hungarian dishes, the site frames them as a strength — *authentic Thai for the adventurous, familiar Hungarian comfort food for the play-it-safe, so any group can share one table.* Authenticity is anchored to the **Thai SELECT** government certification ("we don't just claim to be authentic — the Thai government verifies it").
- **Native-quality Hungarian** — copy was written and iterated to read like a native Hungarian copywriter, not a translation (fixing truncated fragments and awkward repetition based on native-speaker review).
- **Tone:** direct and friendly, proud of the fusion kitchen, the Thai background, and the location — without over-claiming or promoting the neighbouring hotel.

---

## 9. Challenges solved

- **CMYK print images** from the menu PDF rendered with inverted colors in the browser → converted to sRGB (with the CMYK inversion fix) and web-optimized.
- **macOS privacy (TCC) block** on the Photos library → routed around it using the accessible copies and PDF-sourced imagery.
- **Long multi-price rows** overflowing horizontally on mobile → prices wrap onto their own line, indented to align with the dish text; verified zero horizontal overflow.
- **Desktop hero dead space** → the hero image was being rendered at natural height; switched to a stretch layout so the image matches the copy height, removing the gap.
- **Stale caches everywhere** (browser favicon, Google index, Facebook OG, DNS) → handled each with the right tool (cache-busting filenames, re-scrape, Request Indexing, propagation checks).

---

## 10. Outcome

A modern restaurant website that does its job:

- ✅ Live on `https://khrawpakthai.com` with valid HTTPS
- ✅ Bilingual, fully responsive, fast, hand-coded
- ✅ Complete on-page menu with prices and photography
- ✅ Real conversion paths: ordering, events form, tappable phone, map, live open status
- ✅ SEO-ready: structured data, social previews, sitemap, Search Console
- ✅ Continuous deployment — every change goes live with one `git push`
- ✅ Sanitised rendering layer — the language switch never injects raw HTML
- ✅ 39 automated checks in CI on every push, plus a pre-commit gate
- ✅ Self-hosted fonts (GDPR), tightened CSP, hand-maintained review block

From a placeholder-titled builder page to a genuine, conversion-focused restaurant site — grounded in the restaurant's real menu, real reviews, real photos, and a real brand story.

---

## 10b. Engineering discipline

The project deliberately answers the usual criticism of AI-assisted builds — that they
ship fast and then collapse in production:

- **Static by design.** No database, no accounts, no payments, no secrets in the
  codebase, zero npm dependencies. Most of the attack surface simply does not exist.
- **Sanitised rendering.** The bilingual switch parses content inside an inert
  `<template>` and filters it against tag and attribute allowlists — verified end to
  end with an XSS fixture, from the data source through to the rendered page.
- **Automated verification.** 39 checks (structure, images, SEO, structured data,
  form integrity, repo-wide secret scan, and a regression guard on the sanitiser) run
  in CI on every push, with a weekly smoke test against the live site.
- **A pre-commit gate** blocks any commit carrying a secret or failing the audit.
- **A written rules file** (`CLAUDE.md`) records the architecture decisions so future
  changes inherit them instead of drifting.

## 11. Skills & tools demonstrated

**Direction & product:** auditing an existing site, defining objectives, brand positioning, content strategy, native-language copy quality control, and iterative review on real screenshots.

**Engineering:** hand-coded semantic HTML/CSS/JS; responsive/mobile-first layout; a small i18n system; interactive components (tabs, lightbox, language toggle, live status); structured data & technical SEO.

**Content pipeline:** PDF text/image extraction (poppler), image processing and color-space conversion (Python/Pillow), HEIC conversion (sips), and browser-automation data gathering from Google Maps.

**DevOps:** Git, GitHub, Netlify continuous deployment, custom-domain DNS cutover (email-safe), HTTPS, and end-to-end verification with `dig`/`curl`.

**Research & integrations:** web research (Thai SELECT, company/legal, location), Netlify Forms, SimpleAnalytics, Google Search Console, and social-preview (Open Graph) setup.

---

*Built collaboratively: the vision, decisions, brand voice, source material, and native-language quality control were human-led; an AI coding assistant handled the research, code, image processing, deployment steps, and rapid iteration. The point of the project — and of this overview — is what one person plus the right AI tooling can ship end-to-end: a real, live, professional product.*
