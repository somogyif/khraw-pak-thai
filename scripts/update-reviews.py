#!/usr/bin/env python3
"""
Friss Google-értékelések beemelése az oldalra.

  python3 scripts/update-reviews.py                 # éles futás (kulcs kell)
  python3 scripts/update-reviews.py --dry-run       # nem ír fájlba, csak mutatja
  python3 scripts/update-reviews.py --fixture f.json --dry-run   # teszt API nélkül

Az API-kulcs KIZÁRÓLAG a GOOGLE_MAPS_API_KEY környezeti változóból jön
(GitHub Actions secret). Soha ne kerüljön a kódba vagy a repóba.

A Google Places API hívásonként legfeljebb 5 véleményt ad vissza — ezek mindig
a legrelevánsabb/legfrissebb értékelések. A blokk tehát rotál, nem archivál.

Nyelvekről (2026-08 méréssel megállapítva): a languageCode paraméter NEM fordítja
le a véleményeket, hanem az adott nyelvhez illő véleményeket válogatja ki. A hu és
az en hívás így két különböző halmazt ad — összesen ~10 véleményt 5 helyett.
Ezért a vélemények az eredeti nyelvükön jelennek meg mindkét nézetben, ahogy a
Google Maps is mutatja őket. Ez tudatos döntés, nem hiba: ne próbáljuk "javítani"
ismételt fordítási kísérletekkel.
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "site", "index.html")

PLACE_NAME = "Khraw Pak Thai restaurant, Dózsa György út 88, Budapest"
API = "https://places.googleapis.com/v1"

MIN_RATING = 5          # csak ötcsillagos vélemények kerülnek ki
MIN_LEN = 40            # a túl rövid ("Finom volt") értékelés nem mond semmit
MAX_LEN = 260           # ennél hosszabbat levágunk mondathatáron
MAX_REVIEWS = 4         # ennyi fér el a rácsban

START = "<!-- REVIEWS:START"
END = "<!-- REVIEWS:END -->"


def api_get(url, key, params):
    req = urllib.request.Request(
        url + "?" + urllib.parse.urlencode(params),
        headers={"X-Goog-Api-Key": key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def find_place_id(key):
    req = urllib.request.Request(
        API + "/places:searchText",
        data=json.dumps({"textQuery": PLACE_NAME}).encode(),
        headers={
            "X-Goog-Api-Key": key,
            "Content-Type": "application/json",
            "X-Goog-FieldMask": "places.id,places.displayName",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    places = data.get("places", [])
    if not places:
        sys.exit("Nem található a hely a megadott névvel.")
    return places[0]["id"]


def fetch(key, place_id, lang):
    return api_get(
        f"{API}/places/{place_id}",
        key,
        {"fields": "reviews,rating,userRatingCount", "languageCode": lang},
    )


def trim(text):
    """Hosszú vélemény levágása mondathatáron, hogy a kártyák egyformák maradjanak."""
    text = " ".join((text or "").split())
    if len(text) <= MAX_LEN:
        return text
    cut = text[:MAX_LEN]
    stop = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
    return (cut[: stop + 1] if stop > MIN_LEN else cut.rstrip() + "…")


def collect(data_hu, data_en):
    """A HU és EN válasz párosítása szerző + időbélyeg alapján."""
    by_key = {}
    for lang, data in (("hu", data_hu), ("en", data_en)):
        for r in data.get("reviews", []):
            author = (r.get("authorAttribution") or {}).get("displayName", "").strip()
            key = (author, r.get("publishTime", ""))
            entry = by_key.setdefault(
                key,
                {"author": author, "rating": r.get("rating", 0), "text": {}, "got": {}},
            )
            body = r.get("text") or {}
            entry["text"][lang] = trim(body.get("text", ""))
            entry["got"][lang] = body.get("languageCode", "?")

    out = []
    print(f"a Google {len(by_key)} véleményt adott vissza:")
    for entry in by_key.values():
        hu, en = entry["text"].get("hu", ""), entry["text"].get("en", "")
        # ha az egyik nyelven nincs szöveg (a Google nem fordított),
        # a meglévőt használjuk mindkét helyen — jobb, mint kihagyni
        if hu and not en:
            en = hu
        elif en and not hu:
            hu = en

        author = entry["author"] or "?"
        why = None
        if not entry["author"]:
            why = "nincs szerző"
        elif entry["rating"] < MIN_RATING:
            why = f"{entry['rating']}★ (min. {MIN_RATING})"
        elif len(hu) < MIN_LEN:
            why = f"túl rövid ({len(hu)} karakter, min. {MIN_LEN})"

        if why:
            print(f"  – {author}: kihagyva — {why}")
            continue

        got = entry.get("got", {})
        langs = f"hu→{got.get('hu', '-')}, en→{got.get('en', '-')}"
        same = " [HU és EN azonos]" if hu == en else ""
        print(f"  + {author}: {entry['rating']}★, {len(hu)} karakter ({langs}){same}")
        out.append({"author": entry["author"], "hu": hu, "en": en})
    return out[:MAX_REVIEWS]


def render(reviews):
    """HTML előállítása — minden külső szöveg escape-elve megy be."""
    cards = []
    for r in reviews:
        author = html.escape(r["author"], quote=True)
        hu = html.escape(r["hu"], quote=True)
        en = html.escape(r["en"], quote=True)
        cards.append(
            '      <blockquote class="review">\n'
            '        <div class="rstars" aria-label="5">★★★★★</div>\n'
            f'        <p data-en="&#8220;{en}&#8221;">&#8222;{hu}&#8221;</p>\n'
            f"        <cite>{author}</cite>\n"
            "      </blockquote>"
        )
    return "\n".join(cards)


def splice(markup):
    with open(INDEX, encoding="utf-8") as f:
        page = f.read()
    a, b = page.find(START), page.find(END)
    if a == -1 or b == -1:
        sys.exit("Nem találhatók a REVIEWS jelölők az index.html-ben.")
    head_end = page.find("-->", a) + 3
    return page[:head_end] + "\n" + markup + "\n      " + page[b:], page


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fixture", help="teszt JSON API-hívás helyett")
    args = ap.parse_args()

    if args.fixture:
        with open(args.fixture, encoding="utf-8") as f:
            fx = json.load(f)
        data_hu, data_en = fx["hu"], fx["en"]
    else:
        key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
        if not key:
            print("GOOGLE_MAPS_API_KEY nincs beállítva — kihagyva.")
            return 0
        place_id = os.environ.get("GOOGLE_PLACE_ID", "").strip() or find_place_id(key)
        print(f"place id: {place_id}")
        try:
            data_hu = fetch(key, place_id, "hu")
            data_en = fetch(key, place_id, "en")
        except urllib.error.HTTPError as exc:
            sys.exit(f"API hiba: {exc.code} {exc.read().decode(errors='replace')[:300]}")
        print(f"értékelés: {data_hu.get('rating')} ★ / {data_hu.get('userRatingCount')} db")

    reviews = collect(data_hu, data_en)
    if not reviews:
        print("Nincs a szűrőnek megfelelő vélemény — az oldal változatlan marad.")
        return 0

    print(f"{len(reviews)} vélemény kerül ki:")
    for r in reviews:
        print(f"  • {r['author']}: {r['hu'][:60]}…")

    updated, original = splice(render(reviews))
    if updated == original:
        print("Nincs változás.")
        return 0
    if args.dry_run:
        print("\n[dry-run] a fájl nem módosult.")
        return 0

    with open(INDEX, "w", encoding="utf-8") as f:
        f.write(updated)
    print("site/index.html frissítve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
