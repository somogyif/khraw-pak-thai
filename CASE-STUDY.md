# Rebuilding a Restaurant Website — Khraw Pak Thai 🇹🇭🍜

*A case study on turning a good-looking but underperforming restaurant page into a fast, bilingual, conversion-ready website — built as a human + AI collaboration.*

---

## TL;DR

I took **Khraw Pak Thai**, an authentic Thai bistro (with Hungarian classics) at Heroes' Square in Budapest, and rebuilt its website from the ground up. The original looked nice but was missing the essentials a hungry guest actually needs — a real menu, opening hours, reviews, and a reason to click "order."

The result: a **bilingual (HU/EN), SEO-ready, fully responsive** site — plain HTML, CSS and JavaScript, no page builder and no framework — with the complete menu, the live Google rating, dish photography, and a clear brand story — ready to deploy in one drag-and-drop.

I want to be transparent about *how* it was made: I drove the vision, the decisions, the content and the brand voice — and I did it **in collaboration with an AI coding assistant (Claude Code)** that handled the research, the code, the image processing and the fast iteration. Modern building, modern tools.

---

## Where we started

The restaurant already had a website. Visually it was on-brand — a strong deep-green & gold palette, a nice logo, appetising food photos. But under the surface it was a classic "page-builder one-pager" with real gaps:

- 🏷️ The browser/Google title was the default placeholder **"Weboldal HU"** ("Website HU").
- 📋 **No real menu** on the site — the "Menu" link opened an external Canva design.
- 🕐 Opening hours said **"Coming soon."**
- 📞 The phone number was **plain text**, not tappable.
- 🛒 **No online ordering or reservation** path.
- 🔍 Weak SEO foundation: no proper meta description in places, **no structured data**, no semantic headings, images with **no alt text**, broken social-share previews.
- 🐌 Slow initial load (a blank screen for several seconds).

Good bones, but leaving guests — and search engines — without answers.

## What we worked from

Rather than inventing anything, we built on **real source material**:

- The **existing live site** (audited for UX, SEO and conversion gaps).
- The restaurant's **official menu PDF** — 20 pages, bilingual, ~35 MB, with a photo for nearly every dish.
- The **Google Business profile** — rating, review count, opening hours, address, phone.
- **Owner-provided photos** of the new terrace and Hungarian dishes.
- **Company & location details** for a proper legal footer.

## How we did it

1. **Audit first.** Started with an honest breakdown of what was helping and what was hurting — SEO, usability, and the conversion funnel.
2. **Rebuilt from scratch** as plain HTML / CSS / JavaScript instead of a page builder — for speed, control and clean SEO. Written with Claude Code, directed decision by decision.
3. **Structured the full menu** from the PDF into a fast, on-page, category-tabbed menu with prices — Thai, Hungarian, sides, desserts and drinks.
4. **Pulled live data from Google** — real opening hours, the 4.2★ rating, and genuine guest reviews (with attribution).
5. **Processed 60+ dish photos** extracted from the print-ready PDF — converting them from print colour (CMYK) to web colour (sRGB), then resizing and optimising them so the page stays fast. Added click-to-zoom thumbnails only where they help the guest (the unfamiliar Thai dishes), keeping the page light.
6. **Built bilingual HU/EN** as two separately indexable pages — Hungarian at `/`, English generated at `/en/` — with reciprocal hreflang and a plain link between them.
7. **Laid a real SEO foundation** — descriptive title & meta, Open Graph for social sharing, canonical URL, `Restaurant` + review structured data, semantic headings, alt text, sitemap and robots.
8. **Sharpened the brand story.** Repositioned the narrative around a genuine strength: the restaurant's **Thai SELECT** certification — an official mark from the Royal Thai Government that guarantees authentic Thai cuisine — paired with the honest, welcoming idea that Hungarian classics sit right beside the Thai dishes, so *any* group can share one table.
9. **Iterated on real feedback** — menu ordering, photography, framing, bilingual details — until it was right.

## What we shipped

A modern restaurant website that actually does its job:

- ✅ **Complete, searchable menu** with prices and selective dish photography
- ✅ **Bilingual on two indexable URLs** — Hungarian at `/`, English at `/en/`, with reciprocal hreflang; the English page is generated from the Hungarian so they cannot drift
- ✅ **Accessible** — keyboard focus rings, WCAG-checked contrast, no layout shift
- ✅ **Self-hosted fonts** and a branded 404 page
- ✅ **Live "open now / closed"** indicator based on Budapest time
- ✅ **Real Google reviews** and 4.2★ social proof
- ✅ **Tappable phone, embedded map, directions**, and a clear brand story
- ✅ **SEO-ready**: structured data, social previews, semantic markup, sitemap
- ✅ **Fast & fully responsive** — no framework, image-optimised, mobile-first
- ✅ **One-drag deploy** (Netlify-ready static build)
- ✅ **Audited, not just shipped** — two test layers: 74 checks reading the source, and 62 checks driving a real browser. The second layer exists because seven bugs survived three weeks and three external reviews with perfectly correct HTML
- ✅ **Compliance-checked** — bilingual privacy notice, full imprint, fonts self-hosted for GDPR, and a map that loads only when asked, so no cookie banner is needed
- ✅ **Externally reviewed** — three independent AI models were asked to attack the work across three rounds. Roughly ten real findings were acted on, and six false ones were measured and rejected — including a claim that the menu was images-only when it is text, and that images lacked dimensions when every one has them

From a pretty placeholder to a page that answers every question a guest has — and gives them a reason to come in.

---

## The honest bit 🤝

This wasn't done solo, and it wasn't done by an AI alone either. I set the direction, made the calls on brand, content and priorities, supplied the real materials, and reviewed every iteration. The **AI assistant (Claude Code)** did the heavy lifting I pointed it at — research, coding, image processing, and rapid iteration — turning decisions into a finished, working site in a fraction of the usual time.

That's the point I'd actually make on LinkedIn: **this is what one person + the right AI tooling can build now.** Faster, cheaper, and genuinely good.

*#WebDesign #SmallBusiness #AI #BuildInPublic #Budapest #Restaurant*
