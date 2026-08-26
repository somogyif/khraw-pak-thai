# Khraw Pak Thai — weboldal projekt · teljes összefoglaló

**Élő oldal:** https://khrawpakthai.com
**Repó:** github.com/somogyif/khraw-pak-thai
**Állapot:** élesben, működik · GitHub → Netlify automatikus élesítés · CI-ben futó audit
**Utolsó frissítés:** 2026. augusztus

---

## 1. Kontextus — miről szól a projekt

A **Khraw Pak Thai** egy budapesti thai étterem, amely 2026 elején a **Hősök tere mellé** költözött (Dózsa György út 88., egy 19. századi kupolás villában, közvetlen kilátással a térre). Az új helyen kiderült, hogy a vendégek egy része a megszokott hazai ízeket is keresi — így az étlap magyar klasszikusokkal bővült, és **thai–magyar fúziós étteremmé** vált.

Az étterem rendelkezik a **Thai SELECT Casual** minősítéssel — ez a Thai Királyi Kormány Kereskedelmi Minisztériumának hivatalos igazolása arról, hogy a konyha valóban autentikus thai. Google-értékelés: **4,2 ★ / 76 vélemény**.

**A feladat:** a meglévő weboldal helyett egy olyan oldal, ami tényleg vendéget hoz.

---

## 2. Kiindulási állapot — mi volt a baj a régi oldallal

Az induló auditban ezek jöttek elő:

| Probléma | Miért baj |
|---|---|
| Az oldal címe szó szerint **„Weboldal HU"** | Ez jelent meg a böngészőfülön és a Google-találatban is |
| **Nem volt étlap az oldalon** — a „Menü" egy külső Canva-designra vitt | A Google nem indexelte, mobilon rossz élmény, a vendég elnavigál |
| **Nyitvatartás: „Hamarosan!"** | Az egyik legkeresettebb információ hiányzott |
| **A telefonszám sima szöveg** volt | Mobilon nem lehetett egy koppintással hívni |
| **Nem volt rendelés / foglalás** | Hiányzott a fő konverziós pont |
| **Gyenge SEO-alap** | Nincs strukturált adat, nincsenek valódi címsorok, **13 kép alt-szöveg nélkül**, törött közösségi megosztás |
| **Lassú első betöltés**, Canva alapértelmezett favicon | Több másodperc üres képernyő; idegen márkajelzés a fülön |

Az arculat szép volt — de az oldal nem válaszolt a vendégek kérdéseire.

---

## 3. Munkamódszer

A projekt egy szoros, iteratív körben zajlott: **irány kijelölése → megépítés → ellenőrzés valódi képernyőképeken → finomítás**. Semmi nem lett kitalálva: minden tartalom valós forrásból származik.

| Forrás | Mi került ki belőle | Hogyan |
|---|---|---|
| **Étlap-PDF** (20 oldal, kétnyelvű, ~35 MB, Canva-export) | Teljes étlap árakkal + **60+ ételfotó** | `pdftotext`, `pdfimages`, `pdftoppm`; Python/Pillow a **CMYK→sRGB** konverzióhoz és webes optimalizáláshoz |
| **Google cégprofil** | Nyitvatartás (minden nap 11–22), értékelés, cím, telefon, **valódi vendégvélemények** | Böngésző-automatizálás (cookie-kezelés, legújabb szerinti rendezés, eredeti nyelvű szöveg előhívása) |
| **Saját terasz-fotók** (HEIC) | Marhapörkölt, rántott hús a Hősök terénél | `sips` HEIC→JPEG (a macOS Fotók-könyvtár zárolását megkerülve) |
| **Napi menü PDF** | Napi ajánlat kínálata és ára | `pdftotext` |
| **Webkutatás** | Mit jelent a Thai SELECT, és miért erős érv | keresés + oldal-lekérés |
| **Cégadatok, épület-információk** | Impresszum, környék bemutatása | céginformációs oldal + kutatás |

**Külön figyelem a nyelvre:** egy friss 5★-os értékelés eredetileg **svédül** íródott. A Google magyar automata fordítása helyett az **eredeti svéd szöveg** lett előhívva és pontosan lefordítva magyarra és angolra.

---

## 4. Mit tud a kész oldal

**Szerkezet és tartalom**
- **Hero** — headline, bevezető, 4,2★ jelvény, Thai SELECT jelvény, „Kilátással a Hősök térre" jelvény, feliratozott ételfotó
- **Thai SELECT szekció** — elmagyarázza a kormányzati minősítést mint az autentikusság bizonyítékát
- **Napi menü** — kiemelt blokk: hétköznap 11:00–14:00, **3 490 Ft**, előétel/leves + főétel
- **Történet** — thai gyökerek → költözés a Hősök tere mellé → hogyan született a fúziós konyha
- **„Bátor ízek és ismerős kedvencek"** — a magyar fogások nem mentegetőzés, hanem erősség: a felfedezők és a biztosra menők egy asztalnál
- **Legnépszerűbb thai ételek** — képes kártyák
- **Teljes étlap** — kategória-fülek (Thai / Magyar / Köretek / Desszertek / Italok), árakkal, **48 lazy-load bélyegképpel és kattintásra nagyítással** — szándékosan csak a kevésbé ismert fogásoknál, hogy az oldal gyors maradjon
- **Vélemények** — válogatott, valódi Google-értékelések, névvel, két nyelven
- **Rendezvény-ajánlatkérő űrlap** — Netlify Forms, spam-védelemmel; a kérések e-mailben érkeznek
- **GYIK** — strukturált adattal (FAQPage)
- **Kapcsolat** — nyitvatartás **élő „most nyitva / zárva" jelzéssel budapesti idő szerint**, kattintható telefonszám, térkép, útvonalterv, a helyszín bemutatása
- **Lábléc** — teljes impresszum: cégnév, székhely, cégjegyzékszám, adószám, e-mail, telefon; mellette az adatkezelési tájékoztató linkje

**Technikai megoldások**
- **Kétnyelvűség (HU/EN) két külön URL-en** — a magyar a `/`, az angol a `/en/` címen. Az angol oldal **generált**: a `scripts/build-en.py` a magyar forrás `data-en` attribútumaiból építi fel, így a két nyelv nem tud szétcsúszni. Kölcsönös `hreflang` (hu / en / x-default) és saját canonical mindkettőn, a sitemapban is leképezve. A nyelvváltó valódi link a két URL között, nem JS-váltás.
- **Akadálymentesség** — látható fókuszgyűrű billentyűzetes navigációnál (világos szekciókban zöld, sötétben arany, mindkettő a WCAG 3:1 küszöb felett); mért kontrasztok a teljes palettán, a legrosszabb eset 5,9:1 a szükséges 4,5 helyett; minden képen `width`/`height`, hogy ne ugráljon az elrendezés
- **Márkás 404-oldal** — kétnyelvű, a kezdőlapra, az étlapra és a telefonszámra irányítva
- **Saját betűtípusok** — a Poppins és a Karla 14 WOFF2 fájlja a saját domainről (`font-display:swap`, preload a két kritikus vágatra). Kiváltotta a Google Fonts CDN-t: a müncheni bíróság 2022-es ítélete szerint a látogató IP-jének Google felé továbbítása GDPR-sértés, mert a self-hosting elérhető alternatíva.
- **Reszponzív** — mobilon a hero szövege van elöl, a hosszú többáras sorok külön sorba tördelnek
- **Márkás favicon** — a logó thai templom-emblémájából, több méretben (`favicon.ico` + PNG + apple-touch-icon)
- **Szűrt fordítási réteg** — a nyelvváltó soha nem szúr be nyers HTML-t: a tartalom inert `<template>`-ben párszolódik, majd tag- és attribútum-engedélyezőlistán megy át. Eseménykezelők, `style`, `href`, `src` és ismeretlen tagek eltávolítva.
- **Adatkezelési tájékoztató** — kétnyelvű (`/adatvedelem/` és `/en/privacy/`), a láblécből és az űrlap küldés gombja alól linkelve. Tartalmazza az adatkezelő azonosítását, a gyűjtött adatokat, a jogalapot (6. cikk (1) b), majd f) pont), a megőrzési időt kritériummal (12 hónap az utolsó levélváltástól, ha nem lesz szerződés; számviteli bizonylat 8 év), az adatfeldolgozókat és az érintetti jogokat. Allergiát tudatosan **nem kérünk** az űrlapon — telefonon egyeztetjük, így nem tárolunk feleslegesen egészségügyi adatot.
- **Térkép csak kérésre** — a Google-térkép nem töltődik be magától: egy márkás helyőrző áll a helyén, és csak kattintásra kerül be az iframe. Így a Google addig semmilyen adatot nem kap a látogatóról, és **nincs szükség süti-elfogadó ablakra**: friss betöltéskor mérve nulla süti, nulla iframe; az egyetlen tárolt adat a nyelvválasztás a `localStorage`-ban.
- **Vélemények kézi karbantartással** — épült egy heti, Places API-alapú automatizmus, de 2026-08-25-én leszereltük: a Maps Platform feltételei nevesítve tiltják a vélemény-szöveg mentését. A blokk mostantól kézzel frissül, escape-elt tartalommal.

---

## 5. SEO-alap

- Beszédes oldalcím és leírás, canonical URL
- **Open Graph + Twitter Card** márkás megosztási képpel (a törött előnézet javítva, a Facebook gyorsítótára frissítve)
- **Strukturált adat (JSON-LD)**: `Restaurant` (cím, koordináták, nyitvatartás, árkategória, konyha, minősítés), `FAQPage` és `OrderAction` a Wolthoz. Az `AggregateRating` és a `ReserveAction` külső értékelés nyomán kikerült: a saját oldalon közölt értékelés a Google szabályai szerint sosem kap csillagot a találatban, a foglalási akció pedig valódi végpont nélkül nem jelent semmit.
- Valódi címsor-hierarchia (egy `h1`), **minden képnek alt-szövege**
- **Kölcsönös `hreflang`** a magyar és az angol oldal között, `x-default`-tal; a `sitemap.xml` mindkét nyelvet felsorolja `xhtml:link` alternate-ekkel
- `sitemap.xml`, `robots.txt`, **Google Search Console** hitelesítés
- Sebesség: lazy-load képek, méretezett/tömörített fájlok, `fetchpriority` a hero képen

---

## 6. Élesítés és infrastruktúra

- **Repó-struktúra bemutatásra is alkalmas**: a weboldal a `site/` mappában, a dokumentáció a gyökérben, `netlify.toml` konfigurációval (biztonsági fejlécek, kép-cache)
- **Tárhely: Netlify** — először drag & drop előnézet, majd átállás **GitHub → Netlify automatikus élesítésre**: minden `git push` magától élesedik
- **Saját domain** (`khrawpakthai.com`) bekötése a szolgáltatónál: az apex és a `www` A-rekordja átirányítva a Netlify-ra — **az e-mail rekordokhoz (MX, SPF, mail/webmail/smtp/imap) hozzányúlás nélkül**, tudatosan külső DNS-en hagyva
- **HTTPS** automatikus tanúsítvánnyal; HTTP→HTTPS és www→apex átirányítás
- Diagnosztizált és megoldott hibák: **projekt „Private" láthatóság** (401-es „Login Redirect"), DNS-terjedés ellenőrzése `dig`/`curl` eszközökkel
- **Élesítés utáni beállítások:** Netlify Forms e-mail értesítés, SimpleAnalytics (adatvédelmi-barát mérés), Search Console sitemap

---

## 7. Márka és szövegezés

- **Pozicionálás:** a magyar fogások nem elrejtve, hanem erősségként — *autentikus thai a felfedezőknek, ismerős magyar ízek a biztosra menőknek, egy asztalnál.* Az autentikusság a **Thai SELECT** minősítéshez van kötve: „nem mi mondjuk magunkról, hanem a thai kormány igazolja."
- **Hangnem:** közvetlen és barátságos, büszkeséggel a fúziós konyhára, a thai gyökerekre és a helyszínre — túlzás és sznobizmus nélkül
- **Natív magyar szöveg:** anyanyelvi visszajelzés alapján javítva (csonka címek, suta szóismétlés kigyomlálva) — a cél, hogy magyar szövegírótól származzon, ne fordításnak hasson
- **A szomszédos hotel nincs reklámozva** — csak a megtalálhatóság kedvéért van megemlítve

---

## 8. Megoldott nehézségek

| Probléma | Megoldás |
|---|---|
| A PDF nyomdai **CMYK képei** invertált színnel jelentek meg | sRGB konverzió az inverzió javításával + webes optimalizálás |
| A macOS **adatvédelmi zárolása** (Fotók-könyvtár) blokkolta a fotókat | Kerülő út az elérhető másolatokkal és a PDF-ből nyert képekkel |
| **Hosszú többáras sorok kilógtak** mobilon | Az ár külön sorba tördel, a szöveggel egy vonalban; nulla vízszintes túlcsordulás |
| **Üres sáv a desktop hero-ban** | A kép a szöveg magasságához igazítva (stretch elrendezés) |
| **Makacs gyorsítótárak** (favicon, Google-index, Facebook-előnézet, DNS) | Mindegyikre a megfelelő eszköz: új fájlnév, újra-szkennelés, indexelés kérése, terjedés-ellenőrzés |

---

## 8b. Külső szakmai ellenőrzés

A saját auditunk után a projektet **két független AI-modellel (Gemini és Grok) is átnézettük**, kifejezetten hibakeresésre kérve őket, nem visszajelzésre. Amit hoztak:

- **A legfontosabb találat nem kódhiba volt.** A Netlify kredit-korlát a *deployt* blokkolja, nem a `git push`-t — 13 commit feleslegesen ült a gépen, ahol sem a CI nem futott rájuk, sem külső szem nem látta őket. Azonnal javítva.
- **Elfogadott javaslatok:** az `AggregateRating` és a `ReserveAction` kikerült; a megőrzési idő puszta szám helyett indokolt kritériumot kapott; az allergia-kezelés elutasításból pozitív irányítássá vált; `format-detection` meta az iOS-hez; az Egyesült Államokba történő adattovábbítás jogalapja pontosítva (Data Privacy Framework); három gyenge CI-ellenőrzés (puszta szimbólum-létezés) törölve.
- **Megvitatott, de elutasított javaslat:** a szűrt fordítási réteg eltávolítása. Az egyik modell szerint felesleges, a másik szerint indokolt mélységi védelem — a költsége nulla, ezért maradt.
- **Két aggály alaptalannak bizonyult:** a 12%-os szervizdíj fel van tüntetve az étlapon, és az `og:image` pontosan 1200×630.
- **Üzleti tanulság:** mindkét modell ugyanazt mondta — a weboldalon már alig van mit nyerni, a vendégszám a Google Cégprofilon, a Wolton és a budapesti listákon múlik.

Egy találat a kódon kívülről jött: egy **elhagyott Foodora-hirdetés** még élt és indexelt volt, „ZÁRVA" állapottal és elavult árakkal. Ez többet ártott a megtalálhatóságnak, mint bármi a repóban.

---

## 9. Záró audit — teljes átvizsgálás

A projekt végén részletes, automatizált + kézi ellenőrzés futott le.

**Rendben találva:** nincs dupla ID vagy törött belső hivatkozás · mind a 62 kép létezik és van alt-szövege · a strukturált adatok érvényesek · a telefonszám mindenhol egyezik · a külső linkek élnek (Wolt is) · nincs placeholder-maradvány · a CSS és a JavaScript szintaktikailag hibátlan · mind az 5 étlap-fül működik, a képnagyító nyílik és Escape-re zár · az űrlap érvényesít · **konzolhiba: nulla** · **túlcsordulás 320 / 390 / 1280 képpontnál, mindkét nyelven: sehol**

**Megtalált és javított hibák:**
1. Angol nézetben magyar maradt a boroknál („1 790-től" → „from 1 790")
2. A képnagyító üres `src=""` attribútuma (érvénytelen; egyes böngészők emiatt felesleges kérést indítanak) → átlátszó adat-URI
3. Elavult `lastmod` dátum a sitemap-ben → frissítve

Mindhárom javítás élesítve és élőben visszaellenőrizve.

### Az ellenőrzés automatizálása

A kézi átvizsgálás után az egész **beépült a folyamatba**, hogy ne kelljen újra kézzel csinálni:

- **`tests/audit.py` — 47 ellenőrzés** külső függőség nélkül: szerkezet, képek és alt-szövegek, SEO és meta, strukturált adatok érvényessége, űrlap (honeypot, rejtett mező), titok-szivárgás a teljes repóban, valamint regressziós őr a szűrőre — ha valaki visszaírja a nyers beszúrást, a teszt bukik.
- **`tests/live-check.sh`** — az élesített oldal füstpróbája: HTTP/HTTPS, biztonsági fejlécek, sitemap, robots, favicon, átirányítás.
- **CI** — minden pusholásnál lefut az audit, hetente egyszer pedig az élő oldal ellenőrzése.
- **Pre-commit kapu** — a commit leáll, ha titok kerülne a kódba vagy bukna az audit. Hamis API-kulccsal tesztelve: blokkolt.
- **`CLAUDE.md`** — a projekt szabályfájlja: architektúra-döntések és kemény szabályok, hogy minden jövőbeli változtatás örökölje őket.

**Biztonsági alapállás:** az oldal *tervezetten statikus* — nincs adatbázis, nincs felhasználói fiók, nincs titok a kódban, nulla npm függőség. Ez eleve kizárja a dinamikus alkalmazások támadási felületének nagy részét.

---

## 10. Eredmény

- ✅ Élő oldal a **https://khrawpakthai.com** címen, érvényes HTTPS-sel
- ✅ Kétnyelvű (magyar/angol), teljesen reszponzív, gyors, kézzel írt kód
- ✅ Teljes étlap árakkal és ételfotókkal az oldalon
- ✅ Valódi konverziós pontok: Wolt-rendelés, rendezvény-űrlap, kattintható telefon, térkép, élő nyitvatartás-jelzés
- ✅ SEO-kész: strukturált adat, közösségi előnézet, sitemap, Search Console
- ✅ Automatikus élesítés: egy `git push` — és pár perc múlva élesben
- ✅ Szűrt renderelés, pre-commit kapu, 47 automatizált ellenőrzés CI-ben
- ✅ Saját fontok (GDPR), szigorított CSP, kézzel karbantartott vélemény-blokk

**Számokban:** 40+ commit · 1 300+ sor saját kód (HTML/CSS/JS) · 48 étlap-bélyegkép · 2 nyelv · 47 automatizált ellenőrzés · 0 függőség.

---

## 11. Következő lehetséges lépések

- **Galéria** a teraszos és enteriőr fotókból
- **Csípősség-skála és diétás jelölések** az étlapon (🌶️ szintek, vegetáriánus / vegán / gluténmentes)
- **Foodora / további rendelési felületek** kiemelése, ha van

---

*A projekt emberi irányítással, AI-asszisztenciával készült: a vízió, a döntések, a márkahang, a forrásanyagok és az anyanyelvi minőségellenőrzés emberi oldalról érkezett; az AI a kutatást, a kódolást, a képfeldolgozást, az élesítési lépéseket és a gyors iterációt vitte. A lényeg, amit a projekt megmutat: egy ember a megfelelő AI-eszközökkel végponttól végpontig le tud szállítani egy valódi, élő, profi terméket.*
