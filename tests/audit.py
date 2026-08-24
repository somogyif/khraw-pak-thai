#!/usr/bin/env python3
"""
Khraw Pak Thai — automatizált oldal-audit.

Futtatás:  python3 tests/audit.py
Kilépési kód: 0 = minden rendben, 1 = van bukott ellenőrzés.

Külső függőség nélkül fut (csak Python standard library).
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

failures = []
passes = 0


def check(name, ok, detail=""):
    global passes
    if ok:
        passes += 1
        print(f"  \033[32m✓\033[0m {name}")
    else:
        failures.append((name, detail))
        print(f"  \033[31m✗\033[0m {name}" + (f" — {detail}" if detail else ""))


def read(rel):
    with open(os.path.join(SITE, rel), encoding="utf-8") as f:
        return f.read()


html = read("index.html")
css = read("styles.css")
js = read("script.js")

# ---------------------------------------------------------------- szerkezet
print("\nSzerkezet")

ids = re.findall(r'id="([^"]+)"', html)
dupes = sorted({i for i in ids if ids.count(i) > 1})
check("nincs duplikált id", not dupes, ", ".join(dupes))

anchors = {a for a in re.findall(r'href="#([^"]+)"', html) if a}
broken = sorted(anchors - set(ids))
check("minden belső horgony létező elemre mutat", not broken, ", ".join(broken))

check("pontosan egy <h1> van", len(re.findall(r"<h1[\s>]", html)) == 1)

# ---------------------------------------------------------------- képek
print("\nKépek")

srcs = re.findall(r'src="(assets/[^"]+)"', html)
missing = sorted({s for s in srcs if not os.path.exists(os.path.join(SITE, s))})
check(f"mind a {len(set(srcs))} hivatkozott kép létezik", not missing, ", ".join(missing))

imgs = re.findall(r"<img\b[^>]*>", html)
no_alt = [i for i in imgs if " alt=" not in i]
check(f"mind a {len(imgs)} <img> tagen van alt attribútum", not no_alt, f"{len(no_alt)} hiányzik")

no_lazy = [i for i in imgs if "assets/img/menu/" in i and 'loading="lazy"' not in i]
check("az étlap-bélyegképek lazy-load módban töltenek", not no_lazy, f"{len(no_lazy)} kivétel")

# ---------------------------------------------------------------- SEO / meta
print("\nSEO és meta")

for label, pattern in [
    ("<title> kitöltve", r"<title>[^<]{20,}</title>"),
    ("meta description", r'<meta name="description" content="[^"]{50,}"'),
    ("canonical URL", r'<link rel="canonical"'),
    ("viewport", r'<meta name="viewport"'),
    ("og:title", r'<meta property="og:title"'),
    ("og:image", r'<meta property="og:image"'),
]:
    check(label, re.search(pattern, html) is not None)

blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
types = []
valid = True
for b in blocks:
    try:
        types.append(json.loads(b).get("@type"))
    except json.JSONDecodeError as exc:
        valid = False
        types.append(f"HIBÁS ({exc})")
check("a JSON-LD blokkok érvényes JSON-ok", valid, ", ".join(map(str, types)))
check("van Restaurant strukturált adat", "Restaurant" in types)
check("van FAQPage strukturált adat", "FAQPage" in types)

for f in ("sitemap.xml", "robots.txt"):
    check(f"{f} létezik", os.path.exists(os.path.join(SITE, f)))
try:
    ET.parse(os.path.join(SITE, "sitemap.xml"))
    check("a sitemap.xml jól formált XML", True)
except Exception as exc:  # noqa: BLE001
    check("a sitemap.xml jól formált XML", False, str(exc))

# ---------------------------------------------------------------- tartalom
print("\nTartalom")

phones = set(re.findall(r"tel:\+?\d+", html))
check("egyetlen, egységes telefonszám", len(phones) == 1, ", ".join(phones))

descs_total = len(re.findall(r'<span class="mi-desc"', html))
descs_en = len(re.findall(r'<span class="mi-desc" data-en', html))
check(f"minden étlap-leírás fordítható ({descs_en}/{descs_total})", descs_total == descs_en)

junk = [w for w in ("lorem", "Weboldal HU", "TODO", "FIXME", "undefined") if w.lower() in html.lower()]
check("nincs placeholder vagy maradék szöveg", not junk, ", ".join(junk))

# ---------------------------------------------------------------- űrlap
print("\nŰrlap")

form = re.search(r'<form[^>]*name="rendezveny".*?</form>', html, re.S)
check("megvan a rendezvény-űrlap", form is not None)
if form:
    f = form.group(0)
    check("Netlify űrlap-felismerés bekapcsolva", 'data-netlify="true"' in f)
    check("rejtett form-name mező", 'name="form-name"' in f)
    check("honeypot spam-védelem", 'name="bot-field"' in f)
    check("kötelező mezők vannak", f.count("required") >= 2)

# ---------------------------------------------------------------- biztonság
print("\nBiztonság")

secret_pat = r"(api[_-]?key|secret|passwd|password)\s*[:=]\s*['\"][^'\"]{8,}|sk_live_|AIza[0-9A-Za-z_-]{20,}"
hits = [p for p in ("index.html", "styles.css", "script.js")
        if re.search(secret_pat, read(p), re.I)]
check("nincs beégetett titok vagy API-kulcs", not hits, ", ".join(hits))

check("nincs npm függőség (nincs package.json)",
      not os.path.exists(os.path.join(ROOT, "package.json")))
check("nincs eval() vagy document.write()",
      not re.search(r"\beval\(|document\.write\(", js))

# a nyelvváltó nem szúrhat be nyers markupot — csak szűrve
check("a fordítás szűrőn megy át (sanitizeToFragment)", "sanitizeToFragment" in js)
check("tag-engedélyezőlista létezik", "ALLOWED_TAGS" in js)
check("attribútum-engedélyezőlista létezik", "ALLOWED_ATTR" in js)
# innerHTML értékadás csak a <template> elemre megengedett: az inert parsing
# (nem futtat scriptet, nem tölt be külső erőforrást) a sanitizer alapja.
assigns = re.findall(r"(\w+)\.innerHTML\s*=", js)
unsafe = [a for a in assigns if a != "tpl"]
check("nincs nyers innerHTML értékadás (a template inert parsing kivételével)",
      not unsafe, ", ".join(unsafe))

# ---------------------------------------------------------------- kód
print("\nKód")

check("a CSS zárójelei kiegyensúlyozottak", css.count("{") == css.count("}"),
      f"{css.count('{')} nyitó / {css.count('}')} záró")
for name, src in (("index.html", html), ("script.js", js)):
    check(f"{name} nem üres", len(src) > 500)

# ---------------------------------------------------------------- összegzés
print("\n" + "─" * 52)
if failures:
    print(f"\033[31mBUKOTT: {len(failures)}\033[0m  |  sikeres: {passes}")
    for name, detail in failures:
        print(f"  • {name}" + (f" — {detail}" if detail else ""))
    sys.exit(1)

print(f"\033[32mMinden ellenőrzés sikeres ({passes} db)\033[0m")
sys.exit(0)
