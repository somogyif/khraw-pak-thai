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

# a data-full a nagyítóban megnyíló teljes méretű kép — annak is léteznie kell
srcs = (re.findall(r'src="(assets/[^"]+)"', html)
        + re.findall(r'data-full="(assets/[^"]+)"', html))
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

check("megvannak a vélemény-blokk jelölői (automatikus frissítéshez)",
      "REVIEWS:START" in html and "REVIEWS:END" in html)

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

    # Az angol űrlap generált — a fenti mezőknek ott is meg kell lenniük.
    # A honeypot input egyszer már elveszett, mert a data-en a <label> teljes
    # törzsét lecserélte, és ezt csak a magyar oldalt néző ellenőrzés nem látta.
    _en_path = os.path.join(SITE, "en", "index.html")
    _en_src = open(_en_path, encoding="utf-8").read() if os.path.exists(_en_path) else ""
    _enf = re.search(r"<form\b.*?</form>", _en_src, re.S)
    _enf = _enf.group(0) if _enf else ""
    check("az angol űrlapon is ott a form-name", 'name="form-name"' in _enf)
    check("az angol űrlapon is ott a honeypot", 'name="bot-field"' in _enf)
    check("az angol űrlapon is ott minden mező",
          _enf.count("<input") == f.count("<input"),
          f"angol {_enf.count('<input')} / magyar {f.count('<input')}")

# ---------------------------------------------------------------- biztonság
print("\nBiztonság")

# a teljes verziókövetett tartalmat nézzük, nem csak a három fő fájlt
secret_pat = (r"(api[_-]?key|apikey|secret|passwd|password|private[_-]?key|access[_-]?token)"
              r"\s*[:=]\s*['\"][^'\"]{8,}"
              r"|sk_live_[0-9a-zA-Z]{10,}|AIza[0-9A-Za-z_-]{30,}|ghp_[0-9a-zA-Z]{30,}"
              r"|-----BEGIN [A-Z ]*PRIVATE KEY-----")
# önmagát és a szabályfájlt kihagyjuk: azok szándékosan tartalmazzák a mintákat
skip = {"tests/audit.py", "CLAUDE.md", ".githooks/pre-commit"}
scanned, hits = 0, []
for dirpath, dirnames, filenames in os.walk(ROOT):
    # A .venv a fejlesztői böngésző-függőség; nem a mi kódunk, és a pip saját
    # forrásában szerepelnek a keresett minták. A repóba amúgy sem kerül be.
    dirnames[:] = [d for d in dirnames
                   if d not in {".git", "node_modules", "__pycache__", ".venv", ".pytest_cache"}]
    for fn in filenames:
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, ROOT)
        if rel in skip or os.path.splitext(fn)[1].lower() in {
                ".png", ".jpg", ".jpeg", ".ico", ".webp", ".zip", ".pdf"}:
            continue
        try:
            with open(full, encoding="utf-8") as fh:
                content = fh.read()
        except (UnicodeDecodeError, OSError):
            continue
        scanned += 1
        if re.search(secret_pat, content, re.I):
            hits.append(rel)
check(f"nincs beégetett titok a repóban ({scanned} fájl átvizsgálva)", not hits, ", ".join(hits))
check("a pre-commit ellenőrzés verziókövetett",
      os.path.exists(os.path.join(ROOT, ".githooks", "pre-commit")))
check("van projektszintű szabályfájl (CLAUDE.md)",
      os.path.exists(os.path.join(ROOT, "CLAUDE.md")))

# ── kétnyelvűség ──────────────────────────────────────────────────────────
print("\nKétnyelvűség")
en_path = os.path.join(ROOT, "site", "en", "index.html")
check("létezik az angol oldal (/en/)", os.path.exists(en_path))
if os.path.exists(en_path):
    en = open(en_path, encoding="utf-8").read()
    hu = read("index.html")
    for name, page, canon in (("magyar", hu, "https://khrawpakthai.com/"),
                              ("angol", en, "https://khrawpakthai.com/en/")):
        alts = re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', page)
        langs = {a[0] for a in alts}
        check(f"{name} oldal: hreflang hu+en+x-default",
              langs == {"hu", "en", "x-default"}, str(langs))
        check(f"{name} oldal: saját canonical",
              f'rel="canonical" href="{canon}"' in page)
    check("az angol oldal lang=en", '<html lang="en">' in en)
    check("az angol oldal generált (nem kézzel írt)", "GENERÁLT FÁJL" in en)
    check("az angol oldalon nem maradt fordítatlan data-en",
          not re.search(r'\sdata-en(?:-[a-z-]+)?="', en),
          f"{len(re.findall(chr(92)+'sdata-en', en))} maradék")

    # A generátor regexe a *legelső* záró taggel fejezi be az elem törzsét, ezért egy
    # azonos nevű beágyazott elem lógó záró taget hagyna a kimenetben. Ma nincs ilyen
    # elem; ez az ellenőrzés gondoskodik róla, hogy ne is kerüljön be észrevétlenül.
    nested = []
    for m in re.finditer(r'<(?P<tag>[a-zA-Z0-9]+)[^>]*?\sdata-en="[^"]*"[^>]*>(?P<body>.*?)</(?P=tag)>',
                         html, re.S):
        if re.search(r"<" + m.group("tag") + r"[\s>]", m.group("body")):
            nested.append(m.group("tag") + ": " + m.group(0)[:60].replace("\n", " "))
    check("nincs azonos nevű beágyazott elem data-en attribútumon belül",
          not nested, "; ".join(nested[:3]))

    # A data-en az elem TELJES törzsét lecseréli, tehát minden benne lévő elem
    # elveszik, hacsak a fordítás vissza nem hozza. Szövegnél ez rendben van,
    # egy <input>-nál viszont némán megszűnik a mező.
    _functional = ("input", "select", "textarea", "button", "iframe", "img", "form")
    swallowed = []
    for m in re.finditer(r'<(?P<tag>[a-zA-Z0-9]+)[^>]*?\sdata-en="(?P<en>[^"]*)"[^>]*>'
                         r'(?P<body>.*?)</(?P=tag)>', html, re.S):
        for f_ in _functional:
            if re.search(r"<" + f_ + r"[\s>/]", m.group("body")) and f_ not in m.group("en"):
                swallowed.append(f"<{m.group('tag')}> elnyeli: <{f_}>")
                break
    check("a data-en nem nyel el funkcionális elemet", not swallowed, "; ".join(swallowed[:3]))


    # Ha a generátor mégis elrontaná a szerkezetet, a lógó tag itt bukik ki:
    _tags = ("div", "section", "span", "p", "li", "ul", "blockquote", "article",
             "main", "footer", "header", "nav", "form", "label", "button", "cite",
             "h1", "h2", "h3", "h4", "em", "strong", "small", "a")
    unbalanced = [f"{t}: {o}/{c}" for t in _tags
                  for o, c in [(len(re.findall(r"<" + t + r"(?=[\s>])", en)),
                                len(re.findall(r"</" + t + r"\s*>", en)))]
                  if o != c]
    check("az angol oldal tagjei kiegyensúlyozottak", not unbalanced, "; ".join(unbalanced))

    # A data-en csak az elemek szövegét fordítja. Az alt és aria-label attribútumban
    # álló magyar szöveg enélkül bennmaradna az angol oldalon — egy képernyőolvasó
    # magyarul mondaná fel az egész képréteget. Ezért mindegyikhez kell data-en-*.
    _huchars = re.compile(r"[őűáéíóúöüÁÉÍÓÚÖÜŐŰ]")
    missing = []
    for tag in re.findall(r"<[a-zA-Z0-9]+[^>]*>", html):
        # A nyelvváltó címkéje szándékosan kétnyelvű („Váltás angolra / Switch to
        # English"), hiszen épp annak szól, aki a másik nyelvet keresi.
        if 'class="lang-toggle"' in tag:
            continue
        for attr in ("alt", "aria-label"):
            m = re.search(r'(?<!-)\b' + attr + r'="([^"]*)"', tag)
            if not m or not m.group(1).strip():
                continue
            if _huchars.search(m.group(1)) and f'data-en-{attr}="' not in tag:
                missing.append(f"{attr}={m.group(1)[:38]}")
    check("minden magyar alt/aria-label kapott data-en-* fordítást",
          not missing, "; ".join(missing[:3]) + (f" (+{len(missing)-3})" if len(missing) > 3 else ""))

check("nincs npm függőség (nincs package.json)",
      not os.path.exists(os.path.join(ROOT, "package.json")))
check("nincs eval() vagy document.write()",
      not re.search(r"\beval\(|document\.write\(", js))

# a nyelvváltó nem szúrhat be nyers markupot — csak szűrve
# A futásidejű fordítás megszűnt, ezért innerHTML-re egyáltalán nincs szükség.
# Ez a legerősebb forma: ha nincs értékadás, nincs mibe HTML-t injektálni.
check("nincs innerHTML értékadás a script.js-ben",
      not re.search(r"\.innerHTML\s*=", js),
      ", ".join(re.findall(r"(\w+)\.innerHTML\s*=", js)))

# ---------------------------------------------------------------- kód
print("\nDokumentáció")
# Kétszer fordult elő, hogy a dokumentumok a kód mögött maradtak — ezért ellenőrzi a CI.
DOCS = ["README.md", "CASE-STUDY.md", "PROJECT-OVERVIEW.md", "PROJEKT-OSSZEFOGLALO.md"]
docs_text = {d: open(os.path.join(ROOT, d), encoding="utf-8").read()
             for d in DOCS if os.path.exists(os.path.join(ROOT, d))}


# ne hivatkozzanak törölt dolgokra
index_html = read("index.html")
script_js = read("script.js")
gone = {
    "update-reviews.py": not os.path.exists(os.path.join(ROOT, "scripts", "update-reviews.py")),
    "AggregateRating": "AggregateRating" not in index_html,
    "ReserveAction": "ReserveAction" not in index_html,
    # A szűrő és a futásidejű nyelvváltó 2026-08-30-án megszűnt. Három dokumentum
    # még napokig úgy írta le a projektet, mintha meglennének.
    "sanitiz": "sanitize" not in script_js,
    "sanitis": "sanitize" not in script_js,
    "localStorage": "localStorage" not in script_js,
}
for name, removed_from_code in gone.items():
    if not removed_from_code:
        continue
    mentions = [d for d, t in docs_text.items()
                if name in t and not any(
                    w in t[max(0, t.find(name) - 260):t.find(name) + 260].lower()
                    # a mondat mondja meg, hogy már nincs — magyarul vagy angolul
                    for w in ("eltávolít", "kikerült", "megszűnt", "törölt", "removed",
                              "used to", "no longer", "silently ate", "was built and"))]
    check(f"nincs elavult hivatkozás erre: {name}", not mentions, ", ".join(mentions))

# Egy tesztfájl, amit egyetlen dokumentum sem említ, olyan teszt, amit senki nem futtat.
# A render-check.py három dokumentumból hiányzott, miközben ő fogja a legtöbb hibát.
readme = docs_text.get("README.md", "")
undocumented = [f for f in sorted(os.listdir(os.path.join(ROOT, "tests")))
                if f.endswith((".py", ".sh")) and f not in readme]
check("a README minden tesztfájlt említ", not undocumented, ", ".join(undocumented))

# Az oldal Claude Code-dal készült, emberi irányítással. A "hand-coded" állítás
# valótlan, és ellentmond a dokumentumok saját záró bekezdésének. Egyszer már
# kikerült, aztán visszakúszott — ezért ellenőrzés, nem emlékezet. L. MISTAKES.md.
_false_claim = re.compile(
    r"hand-?\s?cod|kézzel\s+írt\s+(kód|html|css)|hand-?written\s+(html|css|js|code|site)",
    re.I)
_claims = []
for _f in sorted(f for f in os.listdir(ROOT) if f.endswith(".md")):
    _t = open(os.path.join(ROOT, _f), encoding="utf-8").read()
    # a MISTAKES.md maga rögzíti a hibát, ezért benne szerepelhet
    if _f == "MISTAKES.md":
        continue
    _m = _false_claim.search(_t)
    if _m:
        _claims.append(f"{_f}: „{_m.group(0)}”")
check("egyik dokumentum sem állítja, hogy kézzel írt kód", not _claims, "; ".join(_claims))

print("\nKód")

check("a CSS zárójelei kiegyensúlyozottak", css.count("{") == css.count("}"),
      f"{css.count('{')} nyitó / {css.count('}')} záró")
for name, src in (("index.html", html), ("script.js", js)):
    check(f"{name} nem üres", len(src) > 500)

# a dokumentumokban leírt ellenőrzésszám csak a végén hasonlítható a valódihoz
_total = passes + len(failures) + 1          # +1: ez az ellenőrzés maga
_stale = []
for _d, _t in docs_text.items():
    _nums = [int(m.group(1)) for m in
             re.finditer(r"\b(\d+)\s+(?:automated checks|checks|automatizált ellenőrzés|ellenőrzés)", _t)]
    if _nums and _total not in _nums:
        _stale.append(f"{_d} ({', '.join(map(str, _nums))} ≠ {_total})")
check("a dokumentumok a valódi ellenőrzésszámot írják", not _stale, "; ".join(_stale))

# ---------------------------------------------------------------- összegzés
print("\n" + "─" * 52)
if failures:
    print(f"\033[31mBUKOTT: {len(failures)}\033[0m  |  sikeres: {passes}")
    for name, detail in failures:
        print(f"  • {name}" + (f" — {detail}" if detail else ""))
    sys.exit(1)

print(f"\033[32mMinden ellenőrzés sikeres ({passes} db)\033[0m")
sys.exit(0)
