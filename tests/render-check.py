#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renderelési ellenőrzés — azt nézi, amit a böngésző TÉNYLEG előállít.

A tests/audit.py a fájlokat olvassa szövegként. Ez az ellenőrzés megnyitja
mindkét oldalt egy igazi böngészőben, és a renderelt DOM-ot vizsgálja.

Miért kell: 2026-08-29-én hét hiba került elő, amelyek hetek óta bent voltak,
és amelyeket szövegből elvileg nem lehet meglátni — a HTML forrás mindegyiknél
helyes volt, a kimenet nem:

  · az angol oldal lang="hu"-t kapott futásidőben
  · 36 alt-szöveg magyarul jelent meg az angol oldalon
  · a honeypot mező eltűnt a generált angol űrlapról
  · az étlapképek billentyűzettel nem voltak megnyithatók
  · a szűrő szöveggé alakította az adatvédelmi tájékoztató linkjét

Ez az ellenőrzés mind a hetet elkapta volna.

Futtatás:  python3 tests/render-check.py                       (helyi site/ mappa)
           python3 tests/render-check.py https://khrawpakthai.com  (az élő oldal)

Az élő futtatás azt fogja meg, amit a helyi nem: elrontott deployt, elmozdult
Netlify-beállítást, lejárt fejléceket. Hetente fut a CI-ban.

Telepítés: python3 -m venv .venv && .venv/bin/pip install playwright
           && .venv/bin/playwright install chromium
"""

import http.server
import os
import re
import socket
import socketserver
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

GREEN, RED, YELLOW, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[0m"
passes = 0
failures = []


def check(name, ok, detail=""):
    global passes
    if ok:
        passes += 1
        print(f"  {GREEN}✓{RESET} {name}")
    else:
        failures.append((name, detail))
        print(f"  {RED}✗{RESET} {name}" + (f" — {detail}" if detail else ""))


def section(title):
    print(f"\n{title}")


# ---------------------------------------------------------------- helyi szerver
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=SITE, **kw)

    def log_message(self, *a):
        pass


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def serve():
    port = free_port()
    httpd = socketserver.TCPServer(("127.0.0.1", port), QuietHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{port}"


# ---------------------------------------------------------------- ellenőrzések
HU_CHARS = re.compile(r"[őűáéíóúöüÁÉÍÓÚÖÜŐŰ]")


def check_page(page, base, path, lang, privacy_href):
    """Egy oldal renderelt állapotának ellenőrzése."""
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base + path, wait_until="networkidle")

    section(f"{path}  — renderelt állapot")

    check("nincs konzolhiba", not errors, "; ".join(errors[:2]))

    # Ugrólink: a fejléc mögé eddig csak végigtabolással lehetett eljutni.
    # A legelső Tabbal kell mérni, még mielőtt bármi máshoz hozzányúlnánk.
    page.keyboard.press("Tab")
    skip = page.evaluate("""(()=>{const a=document.activeElement;
        return a && a.classList.contains('skip-link')
          ? {href:a.getAttribute('href'), onscreen:a.getBoundingClientRect().left >= 0} : null;})()""")
    check("az oldal első Tabja az ugrólinkra visz, és az láthatóvá válik",
          bool(skip and skip["onscreen"]), str(skip))
    check("az ugrólink létező <main> elemre mutat",
          bool(skip) and page.evaluate(
              "!!document.querySelector('main' + %r)" % skip["href"]))
    check(f'a dokumentum nyelve lang="{lang}"',
          page.evaluate("document.documentElement.lang") == lang,
          f'kapott: {page.evaluate("document.documentElement.lang")}')

    # A böngészőben semmit nem tárolunk — se sütit, se helyi tárolót.
    cookies = page.context.cookies()
    check("nem tesz le sütit", not cookies, f"{len(cookies)} süti")
    check("nem ír a helyi tárolóba",
          page.evaluate("(()=>{try{return localStorage.length}catch(e){return 0}})()") == 0)

    # A térkép csak kattintásra tölt — addig egyetlen iframe sincs.
    check("betöltéskor nincs iframe (a térkép csak kérésre tölt)",
          page.evaluate("document.querySelectorAll('iframe').length") == 0)

    # Minden kép betöltődött.
    broken = page.evaluate(
        "[...document.images].filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.getAttribute('src'))")
    check("minden kép betöltődött", not broken, ", ".join(broken[:3]))

    # Az adatvédelmi tájékoztató linkje a gyűjtés pontján — ezt ette meg a szűrő.
    hrefs = page.evaluate("[...document.querySelectorAll('.ef-note a')].map(a=>a.getAttribute('href'))")
    check("az űrlapnál ott az adatvédelmi link", privacy_href in hrefs, f"talált: {hrefs}")

    imprint = page.evaluate("[...document.querySelectorAll('.imprint a')].map(a=>a.getAttribute('href'))")
    check("az impresszum linkjei élnek", len([h for h in imprint if h and h.startswith("mailto:")]) >= 2,
          f"talált: {imprint}")

    # Az űrlap épsége — a honeypot egyszer már elveszett a generált oldalról.
    fields = page.evaluate("document.querySelectorAll('form input, form select, form textarea').length")
    check("az űrlapon 9 mező van", fields == 9, f"{fields} mező")
    hp = page.evaluate("""(()=>{const i=document.querySelector('input[name=\"bot-field\"]');
        if(!i) return null; const p=i.closest('.hp');
        return {tabindex:i.getAttribute('tabindex'), hidden:p&&p.getAttribute('aria-hidden')};})()""")
    check("a honeypot megvan és rejtett a képernyőolvasónak",
          hp and hp["tabindex"] == "-1" and hp["hidden"] == "true", str(hp))

    # Nincs vélemény-idézet, csak az értékelés.
    check("nincs átmásolt vélemény-szöveg",
          page.evaluate("document.querySelectorAll('blockquote.review').length") == 0)
    check("az értékelés-panel megjelenik",
          page.evaluate("!!document.querySelector('.rating-panel')"))

    # Az étlapképek billentyűzetről is megnyithatók.
    kb = page.evaluate("""(()=>{const t=document.querySelector('.mi-thumb');
        return t ? {role:t.getAttribute('role'), tab:t.getAttribute('tabindex'), full:!!t.getAttribute('data-full')} : null;})()""")
    check("az étlapképek billentyűzettel elérhetők",
          kb and kb["role"] == "button" and kb["tab"] == "0", str(kb))
    check("a bélyegkép a teljes méretű képre mutat (data-full)", kb and kb["full"])

    # Enter megnyitja, Escape bezárja, és a fókusz visszatér.
    page.focus(".mi-thumb")
    page.keyboard.press("Enter")
    page.wait_for_timeout(250)
    opened = page.evaluate("""(()=>{const lb=document.getElementById('lightbox');
        return {open:lb.classList.contains('open'), role:lb.getAttribute('role'),
                modal:lb.getAttribute('aria-modal'), inside:lb.contains(document.activeElement),
                src:lb.querySelector('img').getAttribute('src')};})()""")
    check("Enterre megnyílik a nagyító, párbeszédpanelként",
          opened["open"] and opened["role"] == "dialog" and opened["modal"] == "true" and opened["inside"],
          str({k: v for k, v in opened.items() if k != "src"}))
    check("a nagyító a teljes méretű képet tölti",
          "/thumb/" not in (opened["src"] or ""), opened["src"])
    page.keyboard.press("Escape")
    page.wait_for_timeout(250)
    check("Escape-re bezárul és a fókusz visszatér a bélyegképre",
          page.evaluate("""!document.getElementById('lightbox').classList.contains('open')
                           && document.activeElement.classList.contains('mi-thumb')"""))

    # ── akadálymentesség (a 2026-09-05-i sweep megerősített találatai) ──
    check("pontosan egy <main> tereptárgy van",
          page.evaluate("document.querySelectorAll('main').length") == 1)

    # A címsorszint a renderelt DOM-ban sem ugorhat (h1 után négy h3 állt).
    jump = page.evaluate("""(()=>{const l=[...document.querySelectorAll('h1,h2,h3,h4,h5,h6')]
        .map(h=>+h.tagName[1]); const bad=[];
        for(let i=1;i<l.length;i++) if(l[i]>l[i-1]+1) bad.push('h'+l[i-1]+'→h'+l[i]);
        return bad;})()""")
    check("a renderelt címsorszintek nem ugranak", not jump, "; ".join(jump[:3]))

    # A fülsor tab szerepet hirdet — a billentyűzetnek is így kell viselkednie.
    stops = page.evaluate("[...document.querySelectorAll('.menu-tab')].filter(t=>t.tabIndex===0).length")
    check("a fülsorban egyetlen tabstop van", stops == 1, f"{stops} db")
    page.focus(".menu-tab[aria-selected='true']")
    page.keyboard.press("ArrowRight")
    page.wait_for_timeout(150)
    arrow = page.evaluate("""(()=>{const t=document.activeElement;
        if(!t.classList.contains('menu-tab')) return null;
        const p=document.getElementById(t.getAttribute('aria-controls'));
        return {sel:t.getAttribute('aria-selected'), idx:[...document.querySelectorAll('.menu-tab')].indexOf(t),
                panel:!!p, shown:p&&p.classList.contains('is-active'),
                role:p&&p.getAttribute('role')};})()""")
    check("a nyílbillentyű lépteti a füleket, és a panel követi",
          arrow and arrow["idx"] == 1 and arrow["sel"] == "true"
          and arrow["shown"] and arrow["role"] == "tabpanel", str(arrow))
    page.keyboard.press("ArrowLeft")

    # Vízszintes túlcsordulás a három mérethatáron.
    for w, h in ((320, 720), (390, 844), (1280, 800)):
        page.set_viewport_size({"width": w, "height": h})
        page.wait_for_timeout(150)
        over = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        check(f"nincs vízszintes túlcsordulás {w} px-en", over <= 0, f"{over} px túllóg")
    page.set_viewport_size({"width": 1280, "height": 800})


def check_english_attributes(page, base):
    """Az angol oldalon egyetlen magyar alt vagy aria-label sem maradhat."""
    page.goto(base + "/en/", wait_until="networkidle")
    section("/en/  — maradt-e magyar szöveg")

    vals = page.evaluate("""(()=>{const out=[];
        document.querySelectorAll('[alt],[aria-label]').forEach(el=>{
          if(el.classList.contains('lang-toggle')) return;   // szándékosan kétnyelvű
          ['alt','aria-label'].forEach(a=>{const v=el.getAttribute(a);
            if(v && v.trim()) out.push(a+'='+v);});});
        return out;})()""")
    # A "soufflé" és társai ékezetesek, de angolul is így írjuk — szavakra szűrünk.
    HU_WORDS = re.compile(
        r"\b(logó|leves|saláta|sült|rizs|hús|szelet|menü|falatok|galuska|burgonya|"
        r"tekercs|marhahús|zöldségek|halsaláta|burgerek|sajt|szuflé|"
        r"váltás|bezárás|nyelvváltás|mobil|élménybeszámoló|az 5-ből)\b", re.I)
    hu = [v for v in vals if HU_WORDS.search(v)]
    check(f"mind a {len(vals)} alt/aria-label angol", not hu, "; ".join(hu[:3]))

    # A nagyító felirata az alt-ból jön — annak is angolnak kell lennie.
    page.focus(".mi-thumb")
    page.keyboard.press("Enter")
    page.wait_for_timeout(250)
    cap = page.evaluate("document.querySelector('#lightbox .lb-cap').textContent")
    check("a nagyító felirata angol", not HU_WORDS.search(cap or ""), cap)
    page.keyboard.press("Escape")


def check_map_on_request(page, base):
    """A térkép csak kattintásra tölt, és sandboxban fut."""
    page.goto(base + "/", wait_until="networkidle")
    section("Térkép — csak kérésre")

    check("kattintás előtt nincs iframe",
          page.evaluate("document.querySelectorAll('iframe').length") == 0)
    page.click("#mapLoad")
    page.wait_for_timeout(600)
    frame = page.evaluate("""(()=>{const f=document.querySelector('iframe');
        return f ? {sandbox:f.getAttribute('sandbox'), src:(f.getAttribute('src')||'').slice(0,32)} : null;})()""")
    check("kattintás után betölt a térkép", frame is not None)
    check("a térkép sandboxban fut", frame and "allow-scripts" in (frame["sandbox"] or ""),
          str(frame))


def check_reduced_motion(page, base):
    """Akinek a rendszere kevesebb mozgást kér, annak nem mozgatunk semmit."""
    page.emulate_media(reduced_motion="reduce")
    page.goto(base + "/", wait_until="networkidle")
    section("Mozgásérzékenység — prefers-reduced-motion")

    worst = page.evaluate("""(()=>{let max=0;
        document.querySelectorAll('a,button,img,summary,.dish-card,.mi-thumb').forEach(el=>{
          const cs=getComputedStyle(el);
          [cs.transitionDuration, cs.animationDuration].forEach(v=>{
            (v||'').split(',').forEach(d=>{d=d.trim();
              const n=d.endsWith('ms')?parseFloat(d):parseFloat(d)*1000;
              if(!isNaN(n) && n>max) max=n;});});});
        return max;})()""")
    check("a mozgáscsökkentést kérőknek nincs futó átmenet", worst < 50, f"{worst} ms")
    page.emulate_media(reduced_motion="no-preference")


# ---------------------------------------------------------------- futtatás
def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(f"{RED}HIBA:{RESET} a playwright nincs telepítve.\n"
              f"  {YELLOW}python3 -m venv .venv{RESET}\n"
              f"  {YELLOW}.venv/bin/pip install playwright{RESET}\n"
              f"  {YELLOW}.venv/bin/playwright install chromium{RESET}\n"
              f"  {YELLOW}.venv/bin/python tests/render-check.py{RESET}")
        return 2

    # Argumentumként megadott URL esetén az élő oldalt nézzük, helyi szerver nélkül.
    external = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else None
    httpd = None
    if external:
        base = external
        print(f"Renderelési ellenőrzés — {base} (ÉLES)")
    else:
        httpd, base = serve()
        print(f"Renderelési ellenőrzés — {base} (helyi site/)")
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            ctx = browser.new_context(viewport={"width": 1280, "height": 800})
            page = ctx.new_page()
            check_page(page, base, "/", "hu", "/adatvedelem/")
            check_page(page, base, "/en/", "en", "/en/privacy/")
            check_english_attributes(page, base)
            check_map_on_request(page, base)
            check_reduced_motion(page, base)
            browser.close()
    finally:
        if httpd:
            httpd.shutdown()

    print("\n" + "─" * 52)
    if failures:
        print(f"{RED}BUKOTT: {len(failures)}{RESET}  |  sikeres: {passes}")
        for name, detail in failures:
            print(f"  • {name}" + (f" — {detail}" if detail else ""))
        return 1
    print(f"{GREEN}Minden renderelési ellenőrzés sikeres ({passes} db){RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
