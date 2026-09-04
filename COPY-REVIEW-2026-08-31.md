# Magyar szövegminőségi kör — 2026-08-31

Mondatonkénti átolvasás mindkét oldalon. Ami **egyértelműen hibás**, azt javítottam;
ami **döntést igényel**, az alább vár rád.

---

## Javítva

| Volt | Lett | Miért |
|---|---|---|
| „Néhány perc séta az Andrássy út, a Városliget és a Széchenyi fürdő." | „Néhány perc **sétára van** az Andrássy út…" | **Nyelvtani hiba.** Alanyesetű felsorolás állítmány nélkül — a mondat így befejezetlen. |
| Fejléc: „Kilátás a Hősök térre" · törzs: „**Közvetlen kilátással a Hősök terére** – pár lépésre…" | törzs: „Pár lépésre az Andrássy úttól…" | A fejléc és a törzs első fele ugyanazt mondta kétszer. |
| „Premium tea" | „**Prémium** tea" | Máshol az oldalon „Prémium Angus marhahús". Az angol oldalon marad „Premium tea", ott helyes. |
| „**Ebből** született meg a mi thai–magyar fúziós konyhánk." | „**Így** született meg…" | Természetesebb kötés. |
| „tartsd nálunk, a Hősök terénél, thai–magyar fúziós **konyhánkkal**." | „tartsd nálunk, a Hősök terénél — thai–magyar fúziós **konyhával**." | A lelógó eszközhatározó nem kapcsolódott rendesen az igéhez. |

---

## Döntést igényel — nem nyúltam hozzá

### 1. A szomszédos szállodát háromszor nevezzük meg a saját oldalunkon

Ezt tartom a kör legfontosabb találatának, mert **közvetlenül összefügg** azzal, amit
Grok talált: a Google-listázás a Mirage Medic Hotel alatt jeleníti meg az éttermet, és
ez neked kifejezetten nem tetszik.

Csakhogy mi magunk mondjuk ezt a Google-nak — **köztük strukturált adatban is**:

1. **JSON-LD FAQ-válasz** (ezt a Google gépileg olvassa):
   > „…Budapest 1068 – a Mirage Medic Hotel épületében."
2. **A látható GYIK-válasz**, ugyanez a mondat
3. **A kapcsolat szekció**: „Egy 19. századi, kupolás villában… – a Mirage Medic Hotel
   épületében."

**A kompromisszum valós.** A szálloda neve segít odatalálni annak, aki az épületet
keresi. Viszont amíg a saját strukturált adatunk azt állítja, hogy a szálloda
épületében vagyunk, nehéz a Google-tól elvárni, hogy leválasszon róla.

**Javaslatom:** a JSON-LD-ből mindenképp kerüljön ki (az megy a keresőnek), a látható
szövegben pedig épületleírás helyettesítse a márkanevet — például *„egy 19. századi,
kupolás villa földszintjén, saját bejárattal"*. Ez odatalálni is segít, de nem köti
össze a két üzletet.

Egy szavadba kerül, és megcsinálom.

### 2. Három ételnél nem növekvő az ár

A fejléc szerint a sorrend **zöldség / csirke / sertés / marha / garnéla**, és
tizenhárom tételnél ez növekvő is. Háromnál viszont nem:

```
Panang curry   4 950 / 5 380 / 5 550 / 6 230 / 6 030     ← marha > garnéla
Pad Thai       4 950 / 5 380 / 5 550 / 6 230 / 6 030     ← marha > garnéla
Pad See Ew     4 950 / 5 380 / 5 550 / 6 230 / 6 030     ← marha > garnéla
```

Egy negyediknél a kettő azonos: **Pad Med Mamuang 6 230 / 6 230**.

Ez vagy **elgépelés az étlap átvitelekor**, vagy tényleg így van árazva. Nem tudom
eldönteni — az étteremnek kell megmondania. Ha a marha valóban drágább, akkor rendben
van, csak az oszlopsorrend nem „olcsóból drágába" megy ezeknél.

### 3. „Vadpörkölt · + sztrapacska: 990 Ft · 5 990"

Így három adat áll egymás mellett, és nem egyértelmű, mit jelent: a vadpörkölt 5 990,
és a sztrapacska 990-ért kérhető mellé? Vagy 5 990-ben már benne van? Egy vendégnek ezt
egy pillanat alatt értenie kellene.

### 4. „73 Google-vélemény" — beégetett szám

Két helyen szerepel, és **elavul**. Egy külső ellenőrzés már ~76-ot látott. Vagy
frissíteni kell rendszeresen, vagy át kell fogalmazni úgy, hogy ne legyen benne pontos
szám („több mint 70 vélemény alapján").

---

## Amit végigolvastam, és jónak találtam

A **Thai SELECT szakasz** a legerősebb szöveg az oldalon:

> „A minősítést azért hozták létre, mert külföldön sok étterem hívja magát »thainak«
> anélkül, hogy valódi thai ételt főzne. Nálunk tehát nem mi állítjuk, hogy autentikusak
> vagyunk – a thai kormány igazolja."

Ez pontosan az, amit egy jó márkaszöveg csinál: nem állít, hanem bizonyít.

A **történet szakasz** is működik — a „Új otthonunkban láttuk, hogy vendégeink egy része
a megszokott, hazai ízeket is keresi" mondat őszintén magyarázza el a fúziót, ahelyett
hogy koncepciónak adná el.

A **hero** felvezetése („a felfedezők és a biztosra menők egyaránt jól laknak") pontosan
azt a kettősséget fogja meg, ami a hely üzleti előnye.

Az **étlap-leírások** végig konkrétak, nincs bennük üres jelző. Nem találtam egyetlen
olyan mondatot sem, ami fordításízű lenne — ez az oldal magyarul íródott, és látszik.
