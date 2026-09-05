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
- **Térkép csak kérésre** — a Google-térkép nem töltődik be magától: egy márkás helyőrző áll a helyén, és csak kattintásra kerül be az iframe. Így a Google addig semmilyen adatot nem kap a látogatóról, és **nincs szükség süti-elfogadó ablakra**: friss betöltéskor mérve nulla süti, nulla iframe, és **semmi a helyi tárolóban** — a nyelvválasztás 2026-08-30 óta két külön webcím (`/` és `/en/`), nem böngészőben tárolt beállítás.
- **Vélemények: csak az értékelés, szöveg nélkül** — épült egy heti, Places API-alapú automatizmus, de 2026-08-25-én leszereltük: a Maps Platform feltételei nevesítve tiltják a vélemény-szöveg mentését. A kézzel átmásolt idézetek 2026-08-29-én kerültek le: a vélemény szövege a szerzőjéé, a magyar vélemény angol fordítása pedig származékos mű (Szjt. 29. §). Az oldal az értékelést mutatja és a Google-listára linkel.

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

## 8b. Külső szakmai ellenőrzés — három kör, három modell

A saját auditunk után a projektet **három független AI-modellel (Gemini, Grok, Kimi) néztük át**, három körben, kifejezetten hibakeresésre kérve őket, nem visszajelzésre.

**Amit hoztak, és elfogadtuk:**
- **A legfontosabb találat nem kódhiba volt.** A Netlify kredit-korlát a *deployt* blokkolja, nem a `git push`-t — 13 commit feleslegesen ült a gépen, ahol sem a CI nem futott rájuk, sem külső szem nem látta őket.
- **Egy elhagyott Foodora-listázás** még élt és indexelt volt, „ZÁRVA" állapottal és a költözés előtti címmel. Ez többet ártott a megtalálhatóságnak, mint bármi a repóban.
- **A Google-listázás a szomszédos szálloda alatt** jelenítette meg az éttermet, holott az önálló, saját bejárattal.
- **Az űrlap „elfogadod a tájékoztatót" szövege jogilag hibás volt:** a tájékoztató a GDPR 13. cikk szerint információ, nem szerződés; az elfogadás hozzájárulást sugall, miközben a jogalap szerződéskötést megelőző lépés. Sima utalásra cserélve.
- **Az impresszumból hiányzott a tárhelyszolgáltató**, amit az Ekertv. 4. § h) 2014 óta kötelezővé tesz. Kételkedtünk benne, utánanéztünk a jogszabálynak, és az értékelőnek volt igaza.
- **A vélemény-idézetek lekerültek.** A döntő érv olyan volt, amit két korábbi kör nem hozott fel: egy magyar vélemény angol fordítása származékos mű (Szjt. 29. §), amit nincs jogunk közzétenni.
- **Akadálymentességi hibák:** a 48 étlapfotó billentyűzettel megnyithatatlan volt, a honeypot mező pedig képernyőolvasóval elérhető.
- **Teljesítmény:** három fotó PNG-ként volt tárolva, a bélyegképek pedig 720 px-esek egy 62 px-es helyre. A teljes oldal képsúlya ~3,5 MB-ról **717 KB-ra** csökkent.

**Amit elutasítottunk, méréssel:** hat állítás tényszerűen hamisnak bizonyult — hogy hiányoznak a képméretek (mind a 62-n rajta vannak), hogy az étlap csak kép (61 ételnév és ár szövegként), hogy nincs `autocomplete` (van, mindhárom releváns mezőn), hogy a JSON-LD törékeny (mindkét oldalon érvényes), és két túlzás a teljesítményről.

**A legfontosabb tanulság viszont nem az értékelőktől jött.** A két legsúlyosabb hibát az találta meg, hogy *ellenőriztük az állításaikat* — és hetet az, hogy egyszer csak megnyitottuk az oldalt egy böngészőben. Három modell vitatkozott arról, hogy a szűrt renderelési réteg „biztonsági színház"-e; **egyik sem vette észre, hogy közben hetek óta szöveggé alakítja az adatvédelmi tájékoztató linkjét.** Ez vezetett a második tesztréteghez (l. 9. pont) és az architektúra egyszerűsítéséhez (l. 9b).

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

- **`tests/audit.py` — 74 ellenőrzés** külső függőség nélkül, másodperc alatt lefut, a pre-commit kapuban is: szerkezet, képek és alt-szövegek, SEO és meta, strukturált adatok érvényessége, űrlap (honeypot, rejtett mező), titok-szivárgás a teljes repóban, és a kétnyelvűség szerkezeti őrei.
- **`tests/render-check.py` — 62 ellenőrzés igazi böngészőben**, CI-ban minden push-ra. Ez azt nézi, amit a böngésző *előállít*, nem amit a fájl tartalmaz: a dokumentum nyelvét, a maradék magyar `alt`-okat az angol oldalon, az űrlap épségét, a billentyűzetes elérést, a fókuszkezelést, a nulla sütit és a vízszintes túlcsordulást 320/390/1280 px-en. 2026-08-29-én hét olyan hiba került elő, amit szöveges ellenőrzés elvileg nem láthat — ez a réteg mind a hetet elkapta volna.
- **`tests/live-check.sh`** — az élesített oldal füstpróbája: HTTP/HTTPS, biztonsági fejlécek, sitemap, robots, favicon, átirányítás.
- **CI** — minden pusholásnál lefut mindkét tesztréteg. Hetente egyszer ugyanaz a böngészős kör **az élesített oldalon** is végigmegy (`tests/render-check.py https://khrawpakthai.com`) — ez fogja meg az elrontott deployt vagy az elmozdult Netlify-beállítást, amit a helyi futás soha nem látna.
- **Negyedéves ügynök-sweep** (`.claude/workflows/site-sweep.js`) — arra, amit teszt elvileg nem tud: külső listázások elcsúszása a valóságtól, jogszabályváltozás, fordításízű magyar szöveg. Öt független szemüveg, és minden találat elé odaáll egy szkeptikus, akinek a dolga megcáfolni. Nem hetente: lemérve, három külső értékelő tíz valós mellett hat téves állítást tett, és mindet le kellett mérni. **Minden megerősített találatból teszt lesz** valamelyik fenti rétegben — különben a sweep örökké ugyanazt hozná vissza.
- **Pre-commit kapu** — a commit leáll, ha titok kerülne a kódba vagy bukna az audit. Hamis API-kulccsal tesztelve: blokkolt.
- **`CLAUDE.md`** — a projekt szabályfájlja: architektúra-döntések és kemény szabályok, hogy minden jövőbeli változtatás örökölje őket.

**Biztonsági alapállás:** az oldal *tervezetten statikus* — nincs adatbázis, nincs felhasználói fiók, nincs titok a kódban, nulla npm függőség. Ez eleve kizárja a dinamikus alkalmazások támadási felületének nagy részét.

---

## 9b. Architektúra-egyszerűsítés (2026-08-30)

Kiderült, hogy **ugyanazt a fordítást két mechanizmus végezte**: a generátor build-időben előállította az `/en/` oldalt, a `setLang()` pedig futásidőben, a böngészőben újra lefordította ugyanazt. Két gépezet, két hibakészlet — és a hét kétnyelvű hibából mind a futásidejűből jött.

A magyar oldal nyelvváltó gombja **sima link lett** `/en/`-re, ahogy az angol oldalon már eddig is az volt visszafelé. Amit ez törölt:

- `setLang()` és a teljes futásidejű fordítási ág
- a szűrt renderelési réteg, ami *kizárólag* ezt az ágat szolgálta ki — és amiről kiderült, hogy közben minden oldalbetöltéskor szöveggé alakította az adatvédelmi link és az impresszum e-mail linkjeit
- a `data-hu` árnyékattribútumok és a `localStorage` — mindkettő teljesen kikerült

`script.js`: **200 sor → 117 sor.** A `data-en` attribútumok maradtak, de tisztán build-idejű bemenetként.

**Két következmény, ami számít.** Az oldal mostantól **semmit nem tárol a látogató böngészőjében** — se sütit, se helyi tárolót —, tehát a tájékoztatónak már nem kell azzal érvelnie, hogy a nyelvválasztás „feltétlenül szükséges" az ePrivacy 5. cikk (3) szerint; egyszerűen nincs mit indokolni. És angol tartalom többé nem jelenhet meg a magyar URL-en, tehát a canonical és a hreflang azt írja le, amit a látogató lát.

A `CLAUDE.md` 2. szabálya ennek megfelelően szigorodott: **`innerHTML` értékadás egyáltalán nincs**, és az audit bukik, ha valaki visszaírja. Ez erősebb garancia a szűrésnél, mert nincs mit szűrni.

**`MISTAKES.md`** — hibanapló, ami azt rögzíti, ami *némán* romlott el vagy *másodszor* fordult elő: mi történt, mi a gyökérok, mi akadályozza meg a megismétlődést. Ha ugyanaz a minta többször előjön, egysoros szabállyá desztilláljuk a `CLAUDE.md`-be — a napló őrzi meg, *miért* született a szabály, hogy később ne írja felül valaki, aki már elfelejtette.

---

## 10. Eredmény

- ✅ Élő oldal a **https://khrawpakthai.com** címen, érvényes HTTPS-sel
- ✅ Kétnyelvű (magyar/angol), teljesen reszponzív, gyors — keretrendszer és build lépés nélkül
- ✅ Teljes étlap árakkal és ételfotókkal az oldalon
- ✅ Valódi konverziós pontok: Wolt-rendelés, rendezvény-űrlap, kattintható telefon, térkép, élő nyitvatartás-jelzés
- ✅ SEO-kész: strukturált adat, közösségi előnézet, sitemap, Search Console
- ✅ Automatikus élesítés: egy `git push` — és pár perc múlva élesben
- ✅ Két tesztréteg: 74 szöveges és 62 böngészős ellenőrzés, plusz pre-commit kapu
- ✅ Saját fontok (GDPR), szigorított CSP, értékelés link nélkül átmásolt vélemény-szöveg nélkül
- ✅ Nulla süti, nulla helyi tároló, nincs süti-banner — mert nincs mit engedélyezni

**Számokban:** 50+ commit · ~1 300 sor saját kód (HTML/CSS/JS) · 48 étlap-bélyegkép · 2 nyelv · 74 + 62 automatizált ellenőrzés · 0 függőség a kiszállított oldalon · 717 KB a teljes oldal képsúlya.

---

## 11. Nyitott tételek — mind a repón kívül

A weboldal munkája le van zárva. Ami hátra van, az mind külső, és mind az üzemeltető feladata:

1. **E-mail-hitelesítés** *(a legfontosabb, mert láthatatlanul kerül pénzbe)*. A levelezés a Google Workspace-en van, de az SPF a régi szolgáltatót engedélyezi (`include:_spf.m1.websupport.sk`), nincs DKIM és nincs DMARC. Amikor az étterem **válaszol** egy ajánlatkérésre, a levél hitelesítetlenül megy ki, és spambe kerülhet — egy elveszett árajánlatról sosem derül ki, hogy elveszett.
   - SPF: `v=spf1 a mx include:_spf.google.com include:_spf.m1.websupport.sk ~all`
   - DMARC (új TXT `_dmarc` néven): `v=DMARC1; p=none; rua=mailto:flexnfresh2023@gmail.com`
   - DKIM: `admin.google.com` → Apps → Google Workspace → Gmail → Authenticate email
2. **A Foodora-listázás törlése.** Nincs szerződés, tehát nincs partnerportál sem — ez ügyfélszolgálati/jogi megkeresés. Az oldal él, `CLOSED` státusszal és a 2026 februári költözés előtti címmel.
3. **A Google cégprofil leválasztása a szomszédos szállodáról** (a cím szerkesztésénél a „Located in" mező), és friss fotók feltöltése — utcakép a Hősök terével, enteriőr, tálalt ételek, a Thai SELECT tanúsítvány. Turistaforgalmú helyen ez a legnagyobb ingyenes nyereség.

**Későbbre, ha van rá igény:** csípősség-skála és diétás jelölések az étlapon; galéria a teraszos és enteriőr fotókból.

**Amit *ne* csináljunk:** Foodora-listázás visszaállítása (nincs szerződés, és a Wolt a működő csatorna); vélemény-szöveg bármilyen formában az oldalra (l. `CLAUDE.md` 7. pont); Places API-alapú vélemény-automatizmus újraépítése.

---

*A projekt emberi irányítással, AI-asszisztenciával készült: a vízió, a döntések, a márkahang, a forrásanyagok és az anyanyelvi minőségellenőrzés emberi oldalról érkezett; az AI a kutatást, a kódolást, a képfeldolgozást, az élesítési lépéseket és a gyors iterációt vitte. A lényeg, amit a projekt megmutat: egy ember a megfelelő AI-eszközökkel végponttól végpontig le tud szállítani egy valódi, élő, profi terméket.*
