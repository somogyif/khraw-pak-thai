export const meta = {
  name: 'site-sweep',
  description: 'Negyedéves átvizsgálás öt szemüveggel, adversarial ellenőrzéssel',
  whenToUse: 'Negyedévente, étlapváltás vagy kampány előtt, vagy ha jogszabály mozdult. Nem hetente — a heti CI ingyen elvégzi, amit gép el tud végezni.',
  phases: [
    { title: 'Felderítés', detail: 'öt független szemüveg, párhuzamosan' },
    { title: 'Cáfolat', detail: 'minden találatot megpróbálunk megdönteni' },
    { title: 'Összegzés', detail: 'ami túlélte, rangsorolva és tesztté alakítva' },
  ],
}

// ---------------------------------------------------------------- közös háttér
const CONTEXT = `
A Khraw Pak Thai thai–magyar fúziós étterem nyilvános weboldalát vizsgálod.

TÉNYEK, amiket ne kelljen kitalálnod:
- Élő: https://khrawpakthai.com (magyar) és https://khrawpakthai.com/en/ (angol).
  Kód: github.com/somogyif/khraw-pak-thai
- Étterem: 1068 Budapest, Dózsa György út 88., a Hősök tere mellett. 2026 februárjában
  költöztek ide. Üzemeltető: Felba Food Kft. Thai SELECT Casual minősítés. ~4,2★ Google.
- Kiszállítás KIZÁRÓLAG Wolton. Foodorával nincs szerződés.
- Az étterem a szálloda földszintjét bérli, önálló, saját bejárattal. NEM a szálloda része.
- Statikus HTML/CSS/JS. Nincs backend, adatbázis, felhasználói fiók, fizetés, npm-függőség.
  Netlify tárhely, Netlify Forms (rendezvény-ajánlatkérő űrlap), Simple Analytics (süti nélkül).
- Kétnyelvű: a magyar a forrás, az angol oldal generált. A nyelvváltó sima link.
- A böngészőben SEMMIT nem tárol: nulla süti, nulla localStorage. Nincs süti-banner.

AMI MÁR AUTOMATIKUSAN ELLENŐRZŐTT (ne ezekre pazarold az időt):
- 55 statikus ellenőrzés + 45 renderelési ellenőrzés igazi böngészőben, minden push-ra.
  Ezek nézik: dokumentumnyelv, alt/aria-label fordítottság, adatvédelmi link megléte,
  űrlapmezők száma és honeypot, billentyűzetes elérés, fókuszkezelés, nulla süti,
  térkép csak kattintásra, vízszintes túlcsordulás 320/390/1280 px-en, konzolhibák,
  strukturált adatok érvényessége, titok-szivárgás, hreflang kölcsönösség.

AMIT MÁR ELDÖNTÖTTÜNK, ne hozd fel újra:
- Nincs vélemény-idézet az oldalon, csak az értékelés + link. Ok: a Maps-feltételek
  tiltják a tárolást, a fordítás pedig származékos mű (Szjt. 29. §).
- Nincs süti-banner, mert nincs mit engedélyezni.
- Nulla npm-függőség szándékos. Framework, CMS, build lépés javaslata nem hasznos.
- A magyar a forrásnyelv, az angol generált. Ez marad.

ISMERT, NYITOTT TÉTELEK (ezeket ne "fedezd fel" újra, legfeljebb az állapotukat nézd meg):
- Az SPF a régi szolgáltatót engedélyezi (_spf.m1.websupport.sk), nincs DKIM, nincs DMARC.
- A Foodora-listázás él, CLOSED státusszal, régi címmel.
- A Google-profil a szálloda alatt jeleníti meg az éttermet.

SZABÁLY: minden állításodat mérd vagy forrással támaszd alá. Ha tippelsz, írd oda, hogy
tipp. Egy magabiztos téves állítás egy elveszett délutánt ér — a legutóbbi körben három
külső értékelő hat téves állítást tett, és mindet nekünk kellett lemérni.
`

const FINDINGS_SCHEMA = {
  type: 'object',
  required: ['findings'],
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['title', 'evidence', 'impact', 'confidence'],
        properties: {
          title: { type: 'string', description: 'Egy mondat: mi a baj' },
          evidence: { type: 'string', description: 'Mit mértél vagy melyik forrás mondja. Konkrétan.' },
          impact: { type: 'string', description: 'Mibe kerül, ha nem javítjuk' },
          fix: { type: 'string', description: 'Mit kell tenni' },
          confidence: { type: 'string', enum: ['mért', 'forrással alátámasztott', 'tipp'] },
        },
      },
    },
  },
}

const VERDICT_SCHEMA = {
  type: 'object',
  required: ['verdicts'],
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        required: ['title', 'refuted', 'reason'],
        properties: {
          title: { type: 'string' },
          refuted: { type: 'boolean', description: 'true = megdőlt vagy nem igazolható' },
          reason: { type: 'string', description: 'Miért dőlt meg, vagy mi igazolja' },
          severity: { type: 'string', enum: ['magas', 'közepes', 'alacsony'] },
        },
      },
    },
  },
}

// ---------------------------------------------------------------- öt szemüveg
const LENSES = [
  {
    key: 'listazasok',
    prompt: `${CONTEXT}

SZEMÜVEG: külső listázások és a valóság eltérése.

Keresd meg az étterem MINDEN nyilvános listázását, és nézd meg, egyezik-e a valósággal:
Google Maps, Wolt, Facebook, Instagram, TripAdvisor, Yelp, Foursquare, etterem.hu,
welovebudapest.com, funzine.hu, programturizmus, Thai nagykövetség / Thai Trade Center,
thaiselect.com, budapesti étteremlisták, aggregátor-oldalak, scrape-elt másolatok.

Mindegyiknél nézd: jó-e a cím (a 2026 februári költözés előtti régi cím a méreg),
a nyitvatartás, a telefonszám, az étlap, a weboldal-link, és hogy nyitottként jelenik-e meg.

Ez a szemüveg találta meg múltkor a legértékesebb dolgot. Menj és nézd meg élőben.`,
  },
  {
    key: 'jog',
    prompt: `${CONTEXT}

SZEMÜVEG: jogi és szabályozási megfelelés, magyar és uniós.

Nézd át, mi vonatkozik erre az oldalra, és teljesül-e:
- GDPR: tájékoztatás a gyűjtés pontján, jogalap, megőrzési idő, adatfeldolgozók, jogok.
  A megőrzés jelenleg "az utolsó levélváltástól 12 hónap", szezonalitással indokolva —
  ezt egy külső értékelő utólagos magyarázatnak nevezte. Neked kell eldöntened, kinek van igaza.
- ePrivacy: az oldal semmit nem tárol a böngészőben. Elég ez a banner elhagyásához?
- Ekertv. (2001. évi CVIII.) 4. §: impresszum kötelező elemei, tárhelyszolgáltatóval együtt.
- 1169/2011/EU + 19/2017 (V. 8.) FM rendelet: allergén-tájékoztatás. Az oldal jelenleg azt
  írja, kérdezd a szakácsokat. Elég ez, és mi a feltétele?
- Fogyasztóvédelem: kell-e bármi egy rendezvény-ajánlatkérő űrlaphoz, ahol pénz nem cserél gazdát?
- Változott-e bármi 2026 folyamán, ami érinti?

Jogszabályhelyre hivatkozz, ne általánosságra. Ha bizonytalan vagy, írd oda.`,
  },
  {
    key: 'szoveg',
    prompt: `${CONTEXT}

SZEMÜVEG: a magyar szöveg minősége és a kereskedelmi üzenet.

Olvasd végig a https://khrawpakthai.com oldalt, és nézd:
- Anyanyelvi magyarként hangzik-e minden mondat, vagy érződik rajta a fordítás?
  Csonka mondatok címként, kínos szóismétlés, magyartalan szerkezet?
- Az angol oldal (/en/) szövege természetes angol-e, vagy magyarból fordított?
- A hajtás fölött három másodperc alatt kiderül-e, mi ez a hely és miért érdemes bemenni?
- Van-e üres marketingfrázis, ami semmit nem mond?
- A fúzió-pozicionálás (thai + magyar egy asztalnál) segít vagy árt annak, aki
  "authentic thai budapest"-re keres? A Thai SELECT minősítés elég korán jön?

Konkrét mondatokat idézz, és írd oda a javasolt cserét.`,
  },
  {
    key: 'biztonsag',
    prompt: `${CONTEXT}

SZEMÜVEG: biztonsági felület — de reálisan.

Ennek az oldalnak nincs backendje, fiókja, fizetése, adatbázisa. Ne keress SQL injectiont.
A valódi felület ez:
- HTTP fejlécek élőben: CSP, HSTS, Referrer-Policy, Permissions-Policy, X-Content-Type-Options.
  Kérd le őket, és mondd meg, mi hiányzik vagy mi túl megengedő.
- DNS és e-mail: SPF, DKIM, DMARC, MX. (Tudjuk, hogy hiányosak — nézd meg az aktuális
  állapotot, és add meg a PONTOS rekordokat, amiket be kell írni.)
- Harmadik felek: Simple Analytics, Google Fonts (saját szerverről), a kattintásra
  betöltődő Google-térkép. Mennyi adat megy ki, és kinek?
- A Netlify Forms űrlap: honeypot van, CAPTCHA nincs. Reális-e a spam-kockázat?
- Van-e nyilvános információ a repóban, ami nem való oda?
- Tárhelyszintű kockázat: a Netlify beállításai, a domain, a DNS-szolgáltató.

Mérj, ne feltételezz. Add meg a lekérdezéseket, amiket futtattál.`,
  },
  {
    key: 'akadalymentesseg',
    prompt: `${CONTEXT}

SZEMÜVEG: akadálymentesség és használhatóság — azon túl, amit a gép már néz.

A renderelési teszt már ellenőrzi: dokumentumnyelv, alt/aria-label fordítottság,
billentyűzetes elérés a galériához, fókusz be- és visszatérése, vízszintes túlcsordulás.
NE ezeket ismételd.

Amit nézz helyette:
- WCAG 2.2 AA, amit gép nehezen mér: fókuszsorrend logikája, a linkszövegek önmagukban
  értelmesek-e, a címsorhierarchia (h1→h2→h3) törik-e valahol, a hibaüzenetek
  hozzárendelése az űrlapmezőkhöz, a "kihagyás a tartalomra" link megléte.
- Az űrlap: mi történik hibás kitöltéskor? Kap-e a felhasználó érthető visszajelzést?
- Képernyőolvasóval bejárva van-e olyan pont, ahol elveszik az ember?
- Mobilon a valódi használat: elérhető-e hüvelykujjal minden fontos gomb?
- Van-e olyan interakció, ami csak egérrel megy?

Az oldal élőben elérhető — nyisd meg, és próbáld ki, ne a forrásból következtess.`,
  },
]

// ---------------------------------------------------------------- futtatás
phase('Felderítés')
log(`Öt szemüveg indul párhuzamosan. Minden találatot cáfolni próbálunk, mielőtt eléd kerül.`)

const perLens = await pipeline(
  LENSES,

  // 1) felderítés
  (lens) =>
    agent(lens.prompt, {
      label: `keres:${lens.key}`,
      phase: 'Felderítés',
      schema: FINDINGS_SCHEMA,
    }),

  // 2) cáfolat — ugyanaz a szemüveg, de most az ügyész ellen dolgozunk
  (found, lens) => {
    if (!found || !found.findings || !found.findings.length) return { lens: lens.key, kept: [] }
    const list = found.findings
      .map((f, i) => `${i + 1}. ${f.title}\n   Bizonyíték: ${f.evidence}\n   Hatás: ${f.impact}\n   Bizonyosság: ${f.confidence}`)
      .join('\n\n')
    return agent(
      `${CONTEXT}

Az alábbi állításokat egy másik ügynök tette a Khraw Pak Thai weboldaláról.
A te dolgod NEM az, hogy egyetérts. A te dolgod, hogy MEGDÖNTSD őket.

Mindegyiknél nézd meg ténylegesen: igaz-e? Mérd le, kérdezd le, nézd meg élőben.
Gyakori hibák, amiket keresel:
- olyasmit állít hiányzónak, ami valójában ott van
- általános jó tanács, ami erre az oldalra nem érvényes
- valós probléma, de a hatását eltúlozza
- olyasmit javasol, amit a projekt szándékosan elutasított (l. fent)

Ha bizonytalan vagy, alapértelmezésben MEGDŐLT. Inkább dobjunk el egy igaz állítást,
mint hogy egy hamis elvigye a gazdi délutánját.

ÁLLÍTÁSOK:

${list}`,
      { label: `cáfol:${lens.key}`, phase: 'Cáfolat', schema: VERDICT_SCHEMA },
    ).then((v) => {
      const byTitle = {}
      ;(v && v.verdicts ? v.verdicts : []).forEach((x) => { byTitle[x.title] = x })
      const kept = found.findings
        .map((f) => {
          const verdict = byTitle[f.title]
          if (!verdict || verdict.refuted) return null
          return Object.assign({}, f, { severity: verdict.severity || 'közepes', why: verdict.reason })
        })
        .filter(Boolean)
      log(`${lens.key}: ${found.findings.length} állítás → ${kept.length} maradt talpon`)
      return { lens: lens.key, kept }
    })
  },
)

const survivors = perLens.filter(Boolean).flatMap((r) => (r.kept || []).map((f) => Object.assign({ lens: r.lens }, f)))

if (!survivors.length) {
  log('Egyetlen állítás sem élte túl a cáfolatot. Ez jó hír.')
  return { osszefoglalo: 'Nincs megerősített találat.', talalatok: [] }
}

phase('Összegzés')
const summary = await agent(
  `${CONTEXT}

Az alábbi találatok túlélték az adversarial ellenőrzést. Készíts belőlük egy rövid,
magyar nyelvű döntési listát az étterem tulajdonosának, aki nem fejlesztő.

Amit kérek:
1. Rangsorold ŐKET AZ ÜZLETI HATÁS szerint, ne technikai érdekesség szerint. Ami vendéget
   hoz vagy jogi kockázatot csökkent, az van elöl.
2. Mindegyiknél egy mondat: mi a baj, és mit kell tenni. Ne technikai szócséplés.
3. KÜLÖN JELÖLD, melyik találatból lehet AUTOMATIKUS TESZT a tests/render-check.py vagy
   a tests/audit.py fájlban — mert ami tesztté válik, azt soha többé nem kell újra keresni.
   Írd oda, pontosan mit ellenőrizne a teszt.
4. A végén egy mondat: mi az az EGY dolog, amit ma érdemes megcsinálni.

TALÁLATOK:

${survivors.map((f, i) => `${i + 1}. [${f.lens}] [${f.severity}] ${f.title}\n   Bizonyíték: ${f.evidence}\n   Miért áll: ${f.why}\n   Javítás: ${f.fix || '—'}`).join('\n\n')}`,
  { label: 'összegzés', phase: 'Összegzés' },
)

return { osszefoglalo: summary, talalatok: survivors, szemuvegek: perLens.length }
