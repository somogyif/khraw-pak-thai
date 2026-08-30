#!/usr/bin/env python3
"""
Az angol oldal (site/en/index.html) előállítása a magyar forrásból.

  python3 scripts/build-en.py            # generál
  python3 scripts/build-en.py --check    # csak ellenőrzi, hogy naprakész-e (CI)

Miért generált és nem kézzel írt: egyetlen forrás van (site/index.html a
data-en attribútumokkal), így a két nyelv nem tud szétcsúszni. A kimenet
statikus HTML — a Netlify továbbra sem futtat build lépést.

Amit csinál:
  - minden data-en értéket beemel a látható tartalomba, majd az attribútumot eldobja
  - lang="en", angol meta/OG, kölcsönös hreflang + x-default, saját canonical
  - a nyelvváltó gombból link lesz a magyar oldalra (nem JS-váltás)
  - a FAQPage JSON-LD újraépül az angol kérdés-válaszokból
  - a relatív hivatkozások gyökérrelatívvá válnak, hogy /en/ alól is működjenek
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site" / "index.html"
OUT = ROOT / "site" / "en" / "index.html"

BASE = "https://khrawpakthai.com"
HREFLANG = (
    f'<link rel="alternate" hreflang="hu" href="{BASE}/">\n'
    f'<link rel="alternate" hreflang="en" href="{BASE}/en/">\n'
    f'<link rel="alternate" hreflang="x-default" href="{BASE}/">'
)

EN_TITLE = "Khraw Pak Thai – Thai–Hungarian fusion restaurant by Heroes' Square | Budapest"
EN_DESC = ("Khraw Pak Thai – a Thai–Hungarian fusion restaurant by Heroes' Square in Budapest. "
           "Thai SELECT certified authentic Thai cooking alongside real Hungarian classics, "
           "by Thai chefs. Dine in, takeaway or delivery.")
EN_OG_TITLE = "Khraw Pak Thai – Thai–Hungarian fusion restaurant by Heroes' Square"
EN_OG_DESC = ("Thai–Hungarian fusion cooking by Heroes' Square: Thai SELECT certified authentic "
              "Thai dishes and real Hungarian classics. The adventurous and the play-it-safe at one table.")


def apply_translations(page):
    """A data-en értékét a látható tartalomba emeli, majd az attribútumot eldobja."""
    pattern = re.compile(
        r'<(?P<tag>[a-zA-Z0-9]+)(?P<before>[^>]*?)\sdata-en="(?P<en>[^"]*)"(?P<after>[^>]*)>'
        r'(?P<body>.*?)</(?P=tag)>',
        re.S,
    )

    def repl(m):
        en = html.unescape(m.group("en"))
        attrs = (m.group("before") + m.group("after")).rstrip()
        return f'<{m.group("tag")}{attrs}>{en}</{m.group("tag")}>'

    # ismételjük, amíg van mit cserélni (egymásba ágyazott elemek miatt)
    for _ in range(12):
        page, n = pattern.subn(repl, page)
        if not n:
            break
    return apply_attr_translations(page)


def apply_attr_translations(page):
    """A data-en-<attr> értékét a megfelelő attribútumba írja, majd eldobja.

    Az elemek szövegét a data-en fordítja; az attribútumokban (alt, aria-label)
    álló magyar szöveg enélkül bennmaradna az angol oldalon, és a képernyőolvasó
    magyarul mondaná fel az egész képréteget.
    """
    attr_pat = re.compile(r'\sdata-en-(?P<attr>[a-z-]+)="(?P<val>[^"]*)"')
    # Az idézőjeles értékeket át kell ugrani, különben egy attribútumban álló
    # '>' korábban lezárná a tagot, és a fordítás némán elmaradna.
    tag_pat = re.compile(r"""<[a-zA-Z0-9]+(?:"[^"]*"|'[^']*'|[^>"'])*>""")

    def repl_tag(m):
        tag = m.group(0)
        pairs = attr_pat.findall(tag)
        if not pairs:
            return tag
        tag = attr_pat.sub("", tag)
        for attr, val in pairs:
            one = re.compile(r'\s' + re.escape(attr) + r'="[^"]*"')
            if one.search(tag):
                tag = one.sub(f' {attr}="{val}"', tag, count=1)
            else:
                # a záró '>' és az esetleges önzáró '/' elé illesztünk
                inner = tag[1:-1].rstrip()
                selfclose = inner.endswith("/")
                if selfclose:
                    inner = inner[:-1].rstrip()
                tag = f'<{inner} {attr}="{val}"' + ("/>" if selfclose else ">")
        return tag

    page = tag_pat.sub(repl_tag, page)

    # Fail loud: ha bármi fordítatlan maradt, az hiba, nem "majdnem jó".
    leftover = re.findall(r'\sdata-en(?:-[a-z-]+)?="[^"]*"', page)
    if leftover:
        raise SystemExit(
            "HIBA: a generátor nem tudta alkalmazni ezeket a fordításokat "
            f"({len(leftover)} db). Valószínű ok: '<' vagy '>' az attribútum "
            f"értékében. Első: {leftover[0][:90]}"
        )
    return page

def build_faq_jsonld(page):
    """A FAQPage struktúrát az immár angol kérdés-válaszokból építi újra."""
    items = re.findall(
        r'<details class="faq-item">\s*<summary[^>]*>(.*?)</summary>\s*<p[^>]*>(.*?)</p>',
        page, re.S,
    )
    if not items:
        return None
    strip = lambda t: html.unescape(re.sub(r"<[^>]+>", "", t)).strip()
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": strip(q),
             "acceptedAnswer": {"@type": "Answer", "text": strip(a)}}
            for q, a in items
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def generate():
    page = SRC.read_text(encoding="utf-8")

    # 1) a magyar oldalra is kerüljön hreflang (a forrást külön írjuk vissza)
    page = apply_translations(page)

    # 2) fej: nyelv, címek, canonical, hreflang
    page = page.replace('<html lang="hu">', '<html lang="en">', 1)
    page = re.sub(r"<title>.*?</title>", f"<title>{html.escape(EN_TITLE)}</title>", page, count=1, flags=re.S)
    page = re.sub(r'(<meta name="description" content=")[^"]*(")',
                  lambda m: m.group(1) + html.escape(EN_DESC, quote=True) + m.group(2), page, count=1)
    page = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
                  lambda m: m.group(1) + html.escape(EN_OG_TITLE, quote=True) + m.group(2), page, count=1)
    page = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
                  lambda m: m.group(1) + html.escape(EN_OG_DESC, quote=True) + m.group(2), page, count=1)
    page = page.replace('<meta property="og:locale" content="hu_HU">',
                        '<meta property="og:locale" content="en_US">', 1)
    page = page.replace('<meta property="og:locale:alternate" content="en_US">',
                        '<meta property="og:locale:alternate" content="hu_HU">', 1)
    page = page.replace(f'<meta property="og:url" content="{BASE}/">',
                        f'<meta property="og:url" content="{BASE}/en/">', 1)
    # a forrás már tartalmazza a hreflang blokkot — csak a canonicalt cseréljük
    page = page.replace(f'<link rel="canonical" href="{BASE}/">',
                        f'<link rel="canonical" href="{BASE}/en/">', 1)

    # 3) a nyelvváltó gombból link a magyar oldalra
    page = re.sub(
        r'<a class="lang-toggle" href="/en/"[^>]*>.*?</a>',
        '<a class="lang-toggle" href="/" hreflang="hu" aria-label="Váltás magyarra / Switch to Hungarian">HU</a>',
        page, count=1, flags=re.S,
    )

    # 4) relatív hivatkozások gyökérrelatívvá (az /en/ alkönyvtár miatt)
    page = re.sub(r'(\s(?:src|href))="(assets/|favicon\.ico|styles\.css|script\.js)',
                  r'\1="/\2', page)

    # 5) FAQ strukturált adat angolul
    faq = build_faq_jsonld(page)
    if faq:
        page = re.sub(
            r'<script type="application/ld\+json">\s*\{\s*"@context": "https://schema\.org",\s*"@type": "FAQPage".*?</script>',
            f'<script type="application/ld+json">\n{faq}\n</script>',
            page, count=1, flags=re.S,
        )

    # 6) figyelmeztetés a fájl elején, hogy ne szerkessze senki kézzel
    page = page.replace(
        "<!DOCTYPE html>",
        "<!DOCTYPE html>\n<!-- GENERÁLT FÁJL — ne szerkeszd kézzel.\n"
        "     Forrás: site/index.html · Előállítás: python3 scripts/build-en.py -->",
        1,
    )
    return page


def add_hreflang_to_source():
    """A magyar oldalra is felkerül a kölcsönös hreflang (különben a Google nem fogadja el)."""
    page = SRC.read_text(encoding="utf-8")
    if 'hreflang="en"' in page:
        return False
    page = page.replace(f'<link rel="canonical" href="{BASE}/">',
                        f'<link rel="canonical" href="{BASE}/">\n{HREFLANG}', 1)
    SRC.write_text(page, encoding="utf-8")
    return True


def main():
    check = "--check" in sys.argv
    generated = generate()

    if check:
        if not OUT.exists():
            print("✗ site/en/index.html hiányzik — futtasd: python3 scripts/build-en.py")
            return 1
        if OUT.read_text(encoding="utf-8") != generated:
            print("✗ az angol oldal nincs szinkronban a magyarral — futtasd: python3 scripts/build-en.py")
            return 1
        print("✓ az angol oldal naprakész")
        return 0

    if add_hreflang_to_source():
        print("  ✓ hreflang hozzáadva a magyar oldalhoz")
        generated = generate()          # a forrás változott, újragenerálunk

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(generated, encoding="utf-8")
    print(f"  ✓ site/en/index.html ({len(generated):,} byte)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
