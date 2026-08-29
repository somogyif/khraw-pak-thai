# Third-round review — commercial and real-world — Khraw Pak Thai, Budapest

**Be blunt. I want disagreement, not encouragement.** You reviewed this project once before and your best finding had nothing to do with code: you found an abandoned Foodora listing, still live and indexed, showing the restaurant as **ZÁRVA** (closed) with an 18-item stale menu and outdated prices — while we actually only deliver via Wolt. That was worth more than any code review, because it was a real thing losing us real customers, and it was outside the repository where nobody was looking.

**This round I want more of exactly that.** Use your live web access. Go and look.

A parallel prompt is going to a different model for the code, architecture and legal text. **Do not spend your effort there.** Your job is the world outside the repository: what a hungry person in Budapest actually sees, and what is broken in it.

---

## ⚠️ One caveat before you browse

**khrawpakthai.com currently serves an old build.** 22 commits are pushed to GitHub but undeployed — Netlify's free-tier deploy credits ran out and the cycle has not renewed. Verified today:

```
/                 200   (old build)
/en/              404      /adatvedelem/   404
/404.html         404      /llms.txt       404
No CSP header. Live HTML still loads Google Fonts from Google's CDN
and fires a Maps iframe on page load.
```

So: **judging the current live HTML as a product is judging something already replaced.** But there is a version of this that IS your business, and I want it:

- What the old build has done to **indexing** while it sat there. Is Google indexing `/`? Is there anything stale in the index — old titles, the previous page-builder one-pager, the placeholder `Weboldal HU` title, orphaned URLs?
- Whether anything **links to URLs that will 404 or change** when the new build ships.
- Whether the delay itself has cost anything measurable.

---

## The business, in one paragraph

**Khraw Pak Thai** — a Thai–Hungarian fusion restaurant at **1068 Budapest, Dózsa György út 88**, next to Heroes' Square, a UNESCO site with heavy tourist footfall. Moved to this location in February 2026. Thai SELECT certified (a Royal Thai Government authenticity mark). Roughly 4.2★ on Google. Operated by Felba Food Kft. Delivery is **Wolt only** — we are not on Foodora and do not want to be. The pitch is deliberate: proper Thai food **and** Hungarian classics on one menu, so a mixed group — a Thai-curious local with a parent who wants pörkölt, or a tourist couple where one will not eat spicy — can all eat at the same table.

Two audiences: Hungarian locals, and English-speaking tourists coming off Heroes' Square and Andrássy út.

**The goal is more people through the door, more Wolt orders, more event enquiries.** Nothing else on this page matters more than that.

---

## What I want you to actually go and check

### 1. Did the Foodora listing die?

I started the removal process after your last review. **Is it gone?** Search for it. If it is still there, is it still saying ZÁRVA? If it is gone, is anything cached — Google's index, a screenshot in a directory, an aggregator that scraped it?

### 2. Every other listing of this restaurant that I do not know about

This is the highest-value thing you can do. The Foodora catch proves the pattern: listings exist that I have never seen, created by aggregators, scraped from each other, and they are wrong. Go find them.

Google Maps, TripAdvisor, Yelp, Foursquare, Facebook, Instagram, Wolt, `etterem.hu`, `programturizmus.hu`, Budapest tourism sites, Thai-restaurant roundups, `funzine.hu`, `welovebudapest.com`, expat forums, Reddit, aggregator junk sites — anywhere.

For each one, tell me: **is the address right, are the hours right, is the phone right, is the menu current, does it link to the website, and does it say we are open?** The old address before February 2026 is the specific poison here.

### 3. The Google Business Profile

Both previous reviewers ended with "stop polishing the repo, go do Google Business Profile work". Fine. **So tell me exactly what to do.** Look at the actual listing and tell me what is weak: categories, attributes, photos, Q&A, posts, the menu link, the ordering link, the description, the hours including holidays. Which specific field, changed, moves the needle most?

Also: we have ~76 reviews at 4.2★. **What do the bad ones say?** Read them. Is there a pattern I should fix in the restaurant rather than on the website? Be honest even if the answer is unflattering.

### 4. What do people actually search for?

I do not have real keyword data. What does someone in Budapest type when they want this restaurant's food — in Hungarian and in English? "thai étterem budapest", "thai food near Heroes' Square", "pad thai budapest", something else entirely? **Who currently ranks for those, and why them and not us?**

Name the actual competitors near Hősök tere and along Andrássy. What are they doing that we are not?

### 5. Is the positioning right, commercially?

The site leads with fusion — Thai plus Hungarian classics, one table, everyone eats. I believe in it. **But is it a liability?** A tourist searching "authentic Thai Budapest" may read "and we also do pörkölt" as a warning sign that neither is serious. Thai SELECT certification is the counter-evidence, but it sits below the fold.

**Is this positioning helping or hurting?** If it is hurting, what is the version that keeps the real commercial advantage — mixed groups can actually eat here — without diluting the authenticity signal? Be specific about what should be above the fold.

### 6. Thai SELECT — am I underusing it?

It is a Royal Thai Government authenticity certification. Very few Hungarian restaurants have it. On the site it is a section and a JSON-LD `award`. **Is there a directory, a Thai embassy listing, a Thai tourism site, a certified-restaurant register we should be listed on and are not?** That is free, high-trust traffic if it exists.

### 7. The reviews-on-the-page decision I still have not made

Four Google reviews are quoted on the page with reviewer names and a link to the listing. I deleted an API automation once the Maps Platform Terms turned out to forbid caching review text. Both previous reviewers said: drop the quotes, show the rating with a link.

**Commercially — not legally, the other model is handling legal — how much does quoted social proof on your own page actually convert, versus a rating and a link?** Does anyone believe testimonials on a restaurant's own site? If the answer is "nobody reads them, they go to Google anyway", say so and I will drop them today.

### 8. What is the single highest-value hour I could spend?

Not on the website. On the business. Assume the site is done and shipping this week. **Given a restaurant next to Heroes' Square that needs more covers — what is the one thing?** Getting into a Budapest listicle? Photos? A specific aggregator? Something on the street? Something with the Thai embassy? Something seasonal I am missing because it is the end of August and tourist season is turning?

Rank your answer. I will do the top one.

---

## What I do not want

- Code review. Another model has that.
- Generic marketing advice I could have got from a blog post. "Post consistently on Instagram" is not an answer. If you say Instagram, say what to post, why it works for this restaurant, and what the realistic outcome is.
- Encouragement. If something is fine, one line.
- Anything you cannot verify. If you are guessing, say you are guessing. A confident wrong answer about a listing that does not exist costs me an afternoon.
