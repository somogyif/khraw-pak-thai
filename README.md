<div align="center">

# 🍜 Khraw Pak Thai — Restaurant Website

**A fast, bilingual, SEO-ready website for an authentic Thai + Hungarian fusion restaurant at Heroes' Square, Budapest.**

Hand-coded · No frameworks · Deploy-ready

![Website preview](docs/preview.png)

</div>

---

## ✨ What this is

A complete rebuild of a restaurant's website — from a good-looking but empty page-builder page into a site that actually helps guests decide and walk in.

Built as a **human + AI collaboration** (see the full story in [`CASE-STUDY.md`](CASE-STUDY.md)): the direction, brand, content and decisions are mine; the research, coding, image processing and iteration were done together with an AI coding assistant.

## 🧩 Features

- 🌐 **Bilingual (HU / EN)** — one-click language toggle across the whole site, with translated menu categories, copy and reviews
- 📋 **Full on-page menu** — Thai, Hungarian, sides, desserts and drinks, with prices, category tabs and click-to-zoom dish photos
- 🏅 **Thai SELECT story** — the Royal Thai Government's authenticity certification, explained
- ⭐ **Real Google reviews** and 4.2★ social proof
- 🕐 **Live "open / closed"** indicator based on Budapest time
- 📅 **Events & catering request form** (Netlify Forms)
- ❓ **FAQ** section
- 🗺️ **Embedded map, tappable phone, directions, Wolt ordering**
- 🔍 **SEO-ready** — descriptive meta, Open Graph, canonical, `Restaurant` + review structured data, semantic HTML, `sitemap.xml`, `robots.txt`
- 📱 **Fully responsive & fast** — mobile-first, optimised images, lazy loading

## 🛠️ Tech

Plain **HTML + CSS + JavaScript** — no build step, no framework, no dependencies. Just open and it runs.

- Google Fonts (Poppins + Inter)
- Google Maps embed
- Netlify Forms (event enquiries)
- SimpleAnalytics (privacy-friendly, cookie-free)

## 📁 Structure

```
.
├── site/                 # the deployed website (Netlify publish dir)
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   ├── robots.txt
│   ├── sitemap.xml
│   └── assets/img/       # logo, dish photos, menu thumbnails
├── docs/preview.png      # screenshot for this README
├── netlify.toml          # deploy config (publish = "site")
├── CASE-STUDY.md         # the story behind the build
└── README.md
```

## 🚀 Run it locally

```bash
cd site
python3 -m http.server 8765
# then open http://localhost:8765
```

## 🌍 Deploy

**Netlify (recommended):** connect this repo in Netlify — `netlify.toml` already sets the publish directory to `site/`. Every push then deploys automatically. Add the custom domain and Netlify issues HTTPS for free.

Prefer drag-and-drop? Drop the contents of `site/` onto [app.netlify.com/drop](https://app.netlify.com/drop).

---

<div align="center">
<sub>Built with care in Budapest · Restaurant operated by Felba Food Kft.</sub>
</div>
