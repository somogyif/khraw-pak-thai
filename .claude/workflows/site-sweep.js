export const meta = {
  name: 'site-sweep',
  description: 'Öt szemüveg, vegyes modelleken, találatonként három cáfolóval',
  whenToUse: 'Negyedévente, étlapváltás vagy kampány előtt, vagy ha jogszabály mozdult. Nem hetente — a heti CI ingyen elvégzi, amit gép el tud végezni.',
  phases: [
    { title: 'Felderítés', detail: 'öt szemüveg, szemüvegenként más modellen' },
    { title: 'Cáfolat', detail: 'találatonként három nézőpont, a felderítőtől eltérő modelleken' },
    { title: 'Hiányellenőr', detail: 'mit hagyott ki mind az öt szemüveg?' },
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
- Az étterem a szomszédos Mirage Medic Hotel földszintjét bérli, de önálló, saját
  bejárattal. NEM a szálloda része, és a szállodát nem reklámozzuk.
- Statikus HTML/CSS/JS. Nincs backend, adatbázis, felhasználói fiók, fizetés, npm-függőség.
  Netlify tárhely, Netlify Forms (rendezvény-ajánlatkérő űrlap), Simple Analytics (süti nélkül).
- Kétnyelvű: a magyar a forrás, az angol oldal GENERÁLT (scripts/build-en.py).
  A nyelvváltó mindkét irányban sima link. Nincs futásidejű fordítás, nincs innerHTML.
- A böngészőben SEMMIT nem tárol: nulla süti, nulla localStorage. Nincs süti-banner.
- Az oldal Claude Code-dal készült, a tulajdonos irányításával. NEM "hand-coded".

AMI MÁR AUTOMATIKUSAN ELLENŐRZŐTT (ne ezekre pazarold az időt):
- 60 szöveges ellenőrzés (tests/audit.py) + 45 renderelési ellenőrzés igazi böngészőben
  (tests/render-check.py), minden push-ra, plusz hetente az ÉLES oldalon is.
  Ezek nézik: dokumentumnyelv, alt/aria-label fordítottság, adatvédelmi link megléte,
  űrlapmezők száma és honeypot, billentyűzetes elérés, fókuszkezelés, nulla süti,
  térkép csak kattintásra, vízszintes túlcsordulás 320/390/1280 px-en, konzolhibák,
  strukturált adatok érvényessége, titok-szivárgás, hreflang kölcsönösség,
  dokumentáció-elcsúszás, és hogy egyik dokumentum sem állítja, hogy kézzel írt kód.

AMIT MÁR ELDÖNTÖTTÜNK, ne hozd fel újra:
- Nincs vélemény-idézet az oldalon, csak az értékelés + link. Ok: a Maps-feltételek
  tiltják a tárolást, a fordítás pedig származékos mű (Szjt. 29. §).
- Nincs süti-banner, mert nincs mit engedélyezni.
- Nulla npm-függőség szándékos. Framework, CMS, build lépés javaslata nem hasznos.
- A magyar a forrásnyelv, az angol generált. Ez marad.
- A futásidejű nyelvváltás megszűnt. Nem hozzuk vissza.

ISMERT, NYITOTT TÉTELEK (ezeket ne "fedezd fel" újra, legfeljebb az állapotukat nézd meg):
- Az SPF a régi szolgáltatót engedélyezi (_spf.m1.websupport.sk), nincs DKIM, nincs DMARC.
- A Foodora-listázás él, CLOSED státusszal, régi címmel.
- A Google-profil a szálloda alatt jeleníti meg az éttermet.

SZABÁLY: minden állításodat mérd vagy forrással támaszd alá. Ha tippelsz, írd oda, hogy
tipp. Egy magabiztos téves állítás egy elveszett délutánt ér — a legutóbbi körben három
külső értékelő tíz valós mellett HAT téves állítást tett, és mindet le kellett mérni.
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
  required: ['refuted', 'reason'],
  properties: {
    refuted: { type: 'boolean', description: 'true = megdőlt, nem igazolható, vagy nem erre a projektre vonatkozik' },
    reason: { type: 'string', description: 'Mit ellenőriztél, és mire jutottál' },
    severity: { type: 'string', enum: ['magas', 'közepes', 'alacsony'] },
  },
}

// ---------------------------------------------------------------- öt szemüveg
// Szemüvegenként MÁS modell: így a vakfoltjaik nem esnek egybe. Ez a lényege
// a keresztellenőrzésnek — öt prompt egy modellen csak öt prompt.
const LENSES = [
  {
    key: 'listazasok', model: 'opus',
    prompt: `SZEMÜVEG: külső listázások és a valóság eltérése.

Keresd meg az étterem MINDEN nyilvános listázását, és nézd meg, egyezik-e a valósággal:
Google Maps, Wolt, Facebook, Instagram, TripAdvisor, Yelp, Foursquare, etterem.hu,
welovebudapest.com, funzine.hu, programturizmus, Thai nagykövetség / Thai Trade Center,
thaiselect.com, budapesti étteremlisták, aggregátor-oldalak, scrape-elt másolatok.

Mindegyiknél nézd: jó-e a cím (a 2026 februári költözés előtti régi cím a méreg),
a nyitvatartás, a telefonszám, az étlap, a weboldal-link, és hogy nyitottként jelenik-e meg.

Ez a szemüveg találta meg legutóbb a legértékesebb dolgot. Menj és nézd meg élőben.`,
  },
  {
    key: 'jog', model: 'opus',
    prompt: `SZEMÜVEG: jogi és szabályozási megfelelés, magyar és uniós.

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
    key: 'szoveg', model: 'fable',
    prompt: `SZEMÜVEG: a magyar szöveg minősége és a kereskedelmi üzenet.

Olvasd végig a https://khrawpakthai.com oldalt, és nézd:
- Anyanyelvi magyarként hangzik-e minden mondat, vagy érződik rajta a fordítás?
  Csonka mondatok címként, kínos szóismétlés, magyartalan szerkezet, ragozási hiba?
- Az angol oldal (/en/) szövege természetes angol-e, vagy magyarból fordított?
- A hajtás fölött három másodperc alatt kiderül-e, mi ez a hely és miért érdemes bemenni?
- Van-e üres marketingfrázis, ami semmit nem mond?
- A fúzió-pozicionálás (thai + magyar egy asztalnál) segít vagy árt annak, aki
  "authentic thai budapest"-re keres? A Thai SELECT minősítés elég korán jön?

A tulajdonos magyar anyanyelvű, és eddig többször javított ki minket rossz megfogalmazás
miatt. Konkrét mondatokat idézz szó szerint, és írd oda a javasolt cserét — ne
általánosságokat. Egy rossz javaslat rosszabb, mint a semmi.`,
  },
  {
    key: 'biztonsag', model: 'sonnet',
    prompt: `SZEMÜVEG: biztonsági felület — de reálisan.

Ennek az oldalnak nincs backendje, fiókja, fizetése, adatbázisa. Ne keress SQL injectiont.
A valódi felület ez:
- HTTP fejlécek élőben: CSP, HSTS, Referrer-Policy, Permissions-Policy, X-Content-Type-Options.
  Kérd le őket, és mondd meg, mi hiányzik vagy mi túl megengedő.
- DNS és e-mail: SPF, DKIM, DMARC, MX. (Tudjuk, hogy hiányosak — nézd meg az aktuális
  állapotot, és add meg a PONTOS rekordokat, amiket be kell írni.)
- Harmadik felek: Simple Analytics, a kattintásra betöltődő Google-térkép.
  Mennyi adat megy ki, és kinek?
- A Netlify Forms űrlap: honeypot van, CAPTCHA nincs. Reális-e a spam-kockázat?
- Van-e nyilvános információ a repóban, ami nem való oda?
- Tárhelyszintű kockázat: a Netlify beállításai, a domain, a DNS-szolgáltató.

Mérj, ne feltételezz. Add meg a lekérdezéseket, amiket futtattál.`,
  },
  {
    key: 'akadalymentesseg', model: 'opus',
    prompt: `SZEMÜVEG: akadálymentesség és használhatóság — azon túl, amit a gép már néz.

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

// Három cáfoló nézőpont. Nem három azonos szkeptikus: háromféle bukási mód.
const REFUTERS = [
  {
    key: 'tény',
    ask: `Igaz-e egyáltalán? Menj és MÉRD LE. Kérd le az oldalt, a fejlécet, a DNS-t,
nézd meg a forrást — amit csak lehet. A legutóbbi körben egy értékelő azt állította,
hogy hiányoznak a képméretek (mind a 62-n rajta voltak), és hogy az étlap csak kép
(61 ételnév és ár szerepel szövegként). Az ilyet kell kiszűrnöd.`,
  },
  {
    key: 'relevancia',
    ask: `Tegyük fel, hogy igaz. Vonatkozik-e EGYÁLTALÁN erre a projektre? Nézd meg a
fenti "AMIT MÁR ELDÖNTÖTTÜNK" és "AMI MÁR AUTOMATIKUSAN ELLENŐRZŐTT" listát. Sok
általános jó tanács egy statikus, backend nélküli étterem-oldalon egyszerűen nem
alkalmazható, vagy már meg van oldva. Ha ilyen, akkor MEGDŐLT.`,
  },
  {
    key: 'arányosság',
    ask: `Tegyük fel, hogy igaz és releváns. Arányos-e a leírt hatás a valósággal, és
megéri-e a javítás? A legutóbbi körben valaki azt állította, hogy "7 MB tönkreteszi az
LCP-t" — a valódi kezdeti képsúly 564 KB volt, mert a képek 90%-a lazy. Ha a hatás
eltúlzott, vagy a javítás többe kerül, mint amennyit ér, akkor MEGDŐLT.`,
  },
]

// A cáfoló soha ne ugyanazon a modellen fusson, mint a felderítő.
const OTHER_MODELS = { opus: ['sonnet', 'fable', 'sonnet'], sonnet: ['opus', 'fable', 'opus'], fable: ['opus', 'sonnet', 'opus'] }

const MAX_PER_LENS = 8   // ha egy szemüveg ennél többet hoz, a többit naplózzuk

// ---------------------------------------------------------------- futtatás
log('Öt szemüveg, öt különböző modellen. Minden találatot három nézőpont próbál megdönteni, mindegyik más modellen, mint a felderítő.')

const perLens = await pipeline(
  LENSES,

  // 1) felderítés — szemüvegenként más modell
  (lens) =>
    agent(`${CONTEXT}\n\n${lens.prompt}`, {
      label: `keres:${lens.key} (${lens.model})`,
      phase: 'Felderítés',
      model: lens.model,
      schema: FINDINGS_SCHEMA,
    }),

  // 2) cáfolat — találatonként három nézőpont, mind más modellen
  (found, lens) => {
    const all = (found && found.findings) || []
    if (!all.length) {
      log(`${lens.key}: nem talált semmit`)
      return { lens: lens.key, kept: [], raw: 0 }
    }
    const items = all.slice(0, MAX_PER_LENS)
    if (all.length > items.length) {
      log(`${lens.key}: ${all.length} találatból ${items.length} megy cáfolatra (felső korlát)`)
    }
    const models = OTHER_MODELS[lens.model]

    return parallel(
      items.map((f, i) => () =>
        parallel(
          REFUTERS.map((r, j) => () =>
            agent(
              `${CONTEXT}

Egy másik ügynök ezt állítja a Khraw Pak Thai weboldaláról. A te dolgod NEM az, hogy
egyetérts — hanem hogy MEGDÖNTSD, a saját nézőpontodból.

A NÉZŐPONTOD (${r.key}):
${r.ask}

Ha bizonytalan vagy, alapértelmezésben MEGDŐLT. Inkább dobjunk el egy igaz állítást,
mint hogy egy hamis elvigye a gazdi délutánját.

AZ ÁLLÍTÁS:
  Cím: ${f.title}
  Bizonyíték: ${f.evidence}
  Állított hatás: ${f.impact}
  Javasolt javítás: ${f.fix || '—'}
  A felderítő saját bizonyossága: ${f.confidence}`,
              {
                label: `cáfol:${lens.key}/${i + 1}/${r.key}`,
                phase: 'Cáfolat',
                model: models[j],
                effort: 'high',
                schema: VERDICT_SCHEMA,
              },
            ),
          ),
        ).then((votes) => {
          const valid = votes.filter(Boolean)
          const refuted = valid.filter((v) => v.refuted).length
          const survives = valid.length > 0 && refuted < 2   // többségi cáfolat öl
          const sev = (valid.find((v) => !v.refuted) || {}).severity || 'közepes'
          return survives
            ? Object.assign({}, f, {
                lens: lens.key,
                severity: sev,
                votes: `${valid.length - refuted}/${valid.length} tartotta`,
                why: valid.filter((v) => !v.refuted).map((v) => v.reason).join(' | '),
              })
            : null
        }),
      ),
    ).then((results) => {
      const kept = results.filter(Boolean)
      log(`${lens.key}: ${items.length} állítás → ${kept.length} élte túl a hármas cáfolatot`)
      return { lens: lens.key, kept, raw: all.length }
    })
  },
)

const survivors = perLens.filter(Boolean).flatMap((r) => r.kept || [])
const totalRaw = perLens.filter(Boolean).reduce((s, r) => s + (r.raw || 0), 0)
log(`Összesen ${totalRaw} nyers állítás, ebből ${survivors.length} élte túl.`)

// 3) hiányellenőr — mit hagyott ki mind az öt szemüveg?
phase('Hiányellenőr')
const gaps = await agent(
  `${CONTEXT}

Öt szemüveg vizsgálta ezt a projektet (külső listázások, jog, magyar szövegminőség,
biztonsági felület, akadálymentesség), és összesen ${totalRaw} állítást tettek.
Ami túlélte az adversarial cáfolatot:

${survivors.length ? survivors.map((f) => `- [${f.lens}] ${f.title}`).join('\n') : '(egyetlen állítás sem élte túl)'}

A te dolgod NEM újabb hibát keresni ugyanezekben a szemüvegekben. A te dolgod:
**mit hagyott ki mind az öt?** Milyen szempont, kockázat vagy lehetőség maradt
teljesen kívül a látókörükön?

Gondolj arra, ami se nem kód, se nem jog, se nem szöveg: üzletmenet-folytonosság
(mi történik, ha a tulajdonos elveszíti a domain- vagy Netlify-hozzáférést?),
szezonalitás, a versenytársak mozgása, mérés és visszacsatolás (honnan tudja
egyáltalán, hogy működik-e az oldal?), a tartalom elavulása (étlap, árak, ünnepi
nyitvatartás), vagy bármi más, amire nem gondoltunk.

Legfeljebb öt dolgot mondj, de azok legyenek valódiak és konkrétak.`,
  { label: 'hiányellenőr', phase: 'Hiányellenőr', model: 'opus', effort: 'high' },
)

// 4) összegzés
phase('Összegzés')
const summary = await agent(
  `${CONTEXT}

Az alábbi találatok túlélték a hármas adversarial ellenőrzést. Készíts belőlük egy
rövid, magyar nyelvű döntési listát az étterem tulajdonosának, aki nem fejlesztő.

Amit kérek:
1. Rangsorold őket AZ ÜZLETI HATÁS szerint, ne technikai érdekesség szerint. Ami
   vendéget hoz vagy jogi kockázatot csökkent, az van elöl.
2. Mindegyiknél egy mondat: mi a baj, és mit kell tenni. Ne technikai szócséplés.
3. KÜLÖN JELÖLD, melyik találatból lehet AUTOMATIKUS TESZT a tests/render-check.py
   vagy a tests/audit.py fájlban — mert ami tesztté válik, azt soha többé nem kell
   újra keresni. Írd oda, pontosan mit ellenőrizne a teszt.
4. A végén egy mondat: mi az az EGY dolog, amit ma érdemes megcsinálni.

Ha egy találat egybeesik a már ismert nyitott tételekkel (SPF/DKIM/DMARC, Foodora,
Google-profil), azt jelöld "már ismert"-ként, és ne ismételd a részleteket.

TÚLÉLŐ TALÁLATOK:

${survivors.length ? survivors.map((f, i) => `${i + 1}. [${f.lens}] [${f.severity}] [${f.votes}] ${f.title}\n   Bizonyíték: ${f.evidence}\n   Miért áll: ${f.why}\n   Javítás: ${f.fix || '—'}`).join('\n\n') : '(egyetlen állítás sem élte túl a cáfolatot)'}

AMIT A HIÁNYELLENŐR TALÁLT:

${gaps}`,
  { label: 'összegzés', phase: 'Összegzés', model: 'opus', effort: 'high' },
)

return {
  osszefoglalo: summary,
  hianyok: gaps,
  talalatok: survivors,
  statisztika: { nyers: totalRaw, tulelo: survivors.length, szemuvegek: LENSES.length },
}
