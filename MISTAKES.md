# Hibanapló

Mi ment félre, mi volt a gyökérok, és mi akadályozza meg, hogy megismétlődjön.
**Legújabb felül.** Ha ugyanaz a minta többször előjön, egysoros szabállyá
desztilláljuk a `CLAUDE.md`-be — ez a napló őrzi meg, *miért* született a szabály.

Nem minden bosszúság kerül ide. Ide az kerül, ami **némán** romlott el, vagy
ami **másodszor** fordult elő.

---

## 2026-09-05 — A fülsor ARIA-szerepet hirdetett, amit egyikünk sem teljesített

**Mi történt.** Az étlap öt füle `role="tab"` attribútummal, a sor
`role="tablist"`-tel volt megjelölve. Ebből semmi nem valósult meg: nem volt
`aria-selected`, nem volt `aria-controls`, a panelekből hiányzott a
`role="tabpanel"`, és a nyílbillentyűk nem csináltak semmit. Egérrel tökéletesen
működött, ezért hónapokig nem tűnt fel.

**Gyökérok.** Az ARIA-szerep **ígéret**, nem díszítés. Aki `role="tab"`-ot ír,
azt vállalja, hogy a fül a WAI-ARIA tabs mintát követi. A képernyőolvasó ezt
felmondja a látogatónak („fül, 1 az 5-ből"), a látogató pedig a nyílbillentyűhöz
nyúl — és nem történik semmi. **Rosszabb, mint ha ott sem lenne a szerep**: egy
sima gombsor legalább azt mondja, amit tud.

Ugyanez a minta, mint a némán elnyelt adatvédelmi link: a forrás helyesnek
látszott, csak épp nem azt csinálta, amit állított magáról.

**Megelőzés.** Az `audit.py` mostantól minden `role="tab"`-nál megköveteli az
`aria-selected`-et és egy létező elemre mutató `aria-controls`-t, ellenőrzi, hogy
pontosan egy fül van kiválasztva, és hogy annyi `tabpanel` van, ahány fül. A
`render-check.py` a böngészőben megnyomja a nyílbillentyűt, és megnézi, hogy a
kijelölés meg a panel tényleg követi-e. Mind a négy ellenőrzés szándékos
regresszióval tesztelve.

**Ugyanebben a körben, ugyanezzel a tanulsággal.** A `CLAUDE.md` hetekig
„55 ellenőrzést" írt, miközben 60 futott — pedig a dokumentum-elcsúszást már
őrizte egy audit-ellenőrzés. Csak épp a **szabályfájlra nem terjedt ki**. A
kapun kívül hagyott dokumentum ugyanúgy elavul, mint a többi; most már ő is
belül van.

---

## 2026-08-31 — „Hand-coded" — másodszor csúszott vissza egy valótlan állítás

**Mi történt.** A showcase-dokumentumok hét helyen állították, hogy az oldal
„hand-coded" / „kézzel írt kód". Nem az: Claude Code-dal készült, emberi
irányítással. A tulajdonos ezt **már korábban is szóvá tette**, akkor kijavítottuk,
és azóta visszakúszott.

Ráadásul a dokumentumok **önmaguknak mondtak ellent**: a `PROJEKT-OSSZEFOGLALO.md`
záró bekezdése kimondja, hogy AI-asszisztenciával készült, a review-kérések pedig
két mondattal a „hand-written" után írják le, hogy „built by directing an AI coding
assistant".

**Gyökérok.** A javítás egyszeri szövegcsere volt, nem szabály. Egy állítás, amit
semmi nem ellenőriz, visszakerül, amikor a szöveget legközelebb átírják — különösen,
ha jól hangzik.

**Miért számít.** Ezek nem belső jegyzetek, hanem bemutatkozó anyagok. Egy valótlan
állítás bennük nem stílushiba, hanem hitelességi kockázat — és pont az ellenkezőjét
éri el annak, amit a projekt bizonyítani akar: hogy egy ember a megfelelő
AI-eszközökkel végponttól végpontig le tud szállítani egy valódi terméket.

**Megelőzés.** Audit-ellenőrzés, ami minden gyökérszintű `.md` fájlban bukik a
`hand-coded`, `hand-written HTML/CSS/JS` és `kézzel írt kód` mintákra, megnevezve a
fájlt és a talált szövegrészt. A legitim használatot (`srcset` kézzel írása, „ne
szerkeszd kézzel a generált oldalt", „kézzel átmásolt vélemény") nem érinti.
Szándékos regresszióval tesztelve.

---

## 2026-08-30 — Az ellenőrzések elvileg nem láthatták a hibákat

**Mi történt.** 2026-08-29-én hét hiba került elő egyszerre. Mind a hét az oldal
születése óta bent volt (`setLang`, `.hp`, `.mi-thumb`: 2026-08-06; a szűrő:
2026-08-24). Nem keletkeztek — csak addig senki nem nézett rájuk.

**Gyökérok.** 56 ellenőrzésből **nulla** nyitotta meg az oldalt; mind szövegként
olvasta a fájlokat. Mind a hét hiba olyan volt, ami csak a renderelt DOM-ban
látszik: a HTML forrás mindegyiknél helyes volt, a kimenet nem. Ezt nem
gondossággal lehet megoldani, mert szöveges ellenőrzés *elvileg* nem képes rá,
akárhány van belőle.

**Egy második ok.** Ugyanazt a fordítást két mechanizmus végezte — a generátor
build-időben, a `setLang()` futásidőben —, két külön hibakészlettel. A szűrő
kizárólag a futásidejű ág miatt létezett, és épp ő tette tönkre az adatvédelmi
linket.

**Megelőzés.**
- `tests/render-check.py`: 45 ellenőrzés igazi böngészőben, CI-ban minden push-ra.
  A tegnapi hétből hetet elkapott volna. Első futásán talált egy addig ismeretlen
  hibát is: 320 px-en a `white-space:nowrap` gombfelirat szétfeszítette az oldalt.
- A futásidejű nyelvváltó megszűnt: a gomb sima link `/en/`-re. Ezzel eltűnt
  `setLang`, a szűrő, a `data-hu` árnyékattribútumok és a `localStorage` —
  83 sor JS és egy egész hibacsalád.

**Amit ebből tanultunk.** Nem több szem kellett, hanem egy olyan ellenőrzés, ami
másképp néz. Három AI-értékelő vitatkozott a szűrőről; egyik sem vette észre,
hogy közben elront egy megfelelőségi linket. Egy böngésző, ami megnyitja az
oldalt, azonnal látta.

---

## 2026-08-29 — A `data-en` elnyeli az elem törzsét (3. előfordulás → szabály lett)

**Mi történt.** Ugyanaz a gyökérok három különböző álruhában, mind ugyanazon a napon:

1. Beágyazott azonos nevű elem esetén a generátor regexe a *legelső* záró tagnél
   fejezi be az elem törzsét, és lógó záró taget hagy a kimenetben.
   (`<div data-en="A">x <div>y</div></div>` → `<div>A</div></div>`)
2. Az `alt` és `aria-label` attribútum fordítatlanul maradt az angol oldalon —
   60 `alt`-ból 36, 8 `aria-label`-ből 7. A `data-en` az elem *szövegét* cseréli,
   az attribútumokat nem érinti. Egy vak, angolul beszélő látogatónak az egész
   képréteg magyarul szólt.
3. **A honeypot `<input>` mező eltűnt az angol oldalról.** A `data-en` a `<label>`
   teljes törzsét lecserélte, és elvitte a benne lévő mezőt is. Az angol űrlap
   spamvédelem nélkül ment ki — nem tudni, mióta.

**Gyökérok.** A `data-en` nem szöveget cserél, hanem **az elem teljes tartalmát**.
Minden, ami az elemben van — beágyazott elem, űrlapmező, kép —, elvész, hacsak a
fordítás vissza nem hozza. Ez a mechanizmus végig ugyanaz volt; csak háromféle
tünetet produkált, és a tünetekre külön-külön reagáltunk.

**Miért nem bukott ki hamarabb.** Az űrlap-ellenőrzés csak a magyar forrást nézte,
a generált angol oldalt nem. Az „angol oldal friss-e" ellenőrzés (`--check`) pedig
csak azt hasonlítja, hogy a commitolt fájl egyezik-e a generátor kimenetével —
ha a generátor rontja el, ez **bebetonozza** a hibát, nem elkapja.

**Megelőzés.** Négy ellenőrzés a `tests/audit.py`-ban, mindegyik szándékos
regresszióval tesztelve:
- nincs azonos nevű beágyazott elem `data-en`-en belül
- a `data-en` nem nyel el funkcionális elemet (`input`, `select`, `img`, …)
- minden magyar `alt`/`aria-label` mellett ott a `data-en-*` fordítás
- az angol űrlapon ugyanannyi mező van, mint a magyaron

Szabállyá desztillálva a `CLAUDE.md`-ben (4. pont).

---

## 2026-08-29 — A `sips` újratömörítés nagyobb fájlt csinált

**Mi történt.** Az étlap-bélyegképeket „optimalizáltam" `sips -s formatOptions 68`
paranccsal. 2948 KB → 2984 KB. Ugyanez `og-image.jpg`-vel (164→188 KB) és
`video-sk.jpg`-vel (76→132 KB).

**Gyökérok.** Egy már hatékonyan tömörített JPEG újrakódolása nem feltétlenül
kisebb — a `sips` nem őrzi meg az eredeti kvantálási táblát és kromasegmentálást.
A „minőség 68" nem abszolút méret-ígéret.

**Megelőzés.** Kép-optimalizálás után **mindig mérni**, és visszaállítani, ami
nagyobb lett. A valódi nyereség nem az újratömörítésből jött, hanem abból, hogy
a rossz *formátumot* (fotó PNG-ben) és a rossz *méretet* (720 px egy 62 px-es
helyre) javítottuk.

---

## 2026-08-29 — Elhittem egy értékelő állítását ellenőrzés nélkül

**Mi történt.** Egy külső értékelő azt írta, a magyar impresszumnak nem kell
tartalmaznia a tárhelyszolgáltatót. Kételkedtem benne, és **tévedtem** — az
Ekertv. 4. § h) 2014 óta kötelezővé teszi.

Fordítva is megtörtént: egy másik értékelő szerint „7 MB tönkreteszi az LCP-t",
és majdnem nekiálltam a rossz problémát javítani. Mérve a valódi kezdeti
képsúly 564 KB volt — a 62 képből 56 lazy.

**Gyökérok.** Külső értékelő állítása **adat, nem tény**. Mindkét irányban:
sem elfogadni, sem elutasítani nem szabad mérés vagy forrás nélkül.

**Megelőzés.** Minden ellenőrizhető állítás mérés vagy jogszabályi forrás ellen
fut, mielőtt kódot érintenék. A mai körben ez négy hamis állítást szűrt ki — és
közben, épp az ellenőrzés során bukott ki a két legsúlyosabb valódi hiba.
