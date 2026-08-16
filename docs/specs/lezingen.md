# Lezingen van de dag (Apostel en Evangelie)

Normatieve specificatie voor [heiligen-lage-landen](https://github.com/orthodox-groningen/heiligen-lage-landen).
Wijzigingen hier zijn bindend voor `scripts/lezingen.py` en worden gespiegeld naar
`/uitleg/lezingen/`. De machine-leesbare voorbeelden (onderaan dit bestand) sturen
pytest; die blokken staan niet op de publieke uitlegpagina.

## Traditiebeleid

1. **Primair:** praktijk van de Russische Orthodoxe Kerk (Moskou) —
   *Богослужебные указания* en de kerkkalender van het Издательство Московской
   Патриархии.
2. **Bij twijfel of lacune:** ROCOR (toetsen o.a. aan Holy Trinity Orthodox
   Calendar / Jordanville).
3. Geen Grieks/Antiocheens als default.

De site toont **verwijzingen** (boek + verzen; optioneel зачало-nummer), geen
volledige Bijbeltekst.

## Begrippen

- **Rijádovoe / doorlopende lezing:** Apostel en Evangelie van de weekreeks
  (na Pascha of na Pinksteren), niet van een heilige.
- **Feestlezing:** lezing die bij een feest of (hoog) heiligenfeest hoort.
- **Зачало:** liturgische perikoop-nummering in Apostel/Evangelie-boeken.
- **«От полу»:** begin midden in een genummerd зачало (zie Azbyka).

## Regels (fase 0+)

### R1 — Kalendercontext

Beweeglijke dagen (paascyclus) worden berekend t.o.v. **Orthodox Pascha**
(Alexandrijnse/Juliaanse computus → burgerlijke datum). Vaste feesten gebruiken
de **feestdatum** (MM-DD-dagnaam), consistent met de rest van deze site
(nieuw/oud); zie uitleg Nieuw/Oud.

### R2 — Bekende feestoverride

Als voor de dag een feestoverride bestaat in `data/lezingen/feest-overrides.yaml`
(match op paascyclus-offset of vaste MM-DD), dan gelden die Apostel- en
Evangelielezingen. Ze **vervangen** de doorlopende lezing tenzij R5 een andere
`modus` voorschrijft (`toevoegen` / `negeren`).

### R3 — Doorlopende weekreeks

Buiten feestoverrides: Apostel/Evangelie volgens de week na Pascha of na
Pinksteren en de weekdag (ma–zo), uit `data/lezingen/weekreeks.yaml`
(Messia/Brussel-tabellen; Moskou voor de Lucaanse sprong).

**Lucaanse sprong (Moskou):** vanaf de **maandag na de zondag na
Kruisverheffing** (14 sept.) volgt het Evangelie de Lucasse reeks vanaf
tabelweek 18; de Apostel blijft de doorlopende weektelling na Pinksteren.

**Отступка / преступка** (Azbyka, o.b.v. *Juliaanse* Pascha-datum):

| Juliaanse Pascha | Effect |
|------------------|--------|
| ≤ 30 maart | **отступка** — vóór de sprong blijven Matteüs-weken 1–17 (herhalen als de telling al ≥ 18 is); sprong naar Luc. 18 blijft |
| 31 maart – 6 april | normaal |
| ≥ 7 april | **преступка** — sprong naar Luc. 18 terwijl de Apostel-telling nog &lt; 17 kan zijn |

Tags in het resultaat: `R3-lucaans`, eventueel `R3-otstupka` / `R3-prestupka`.

### R4 — Vasten / geen liturgie

Op sommige vastendagen is er geen liturgie met Apostel/Evangelie van het type
“van de dag” (bijv. weekdagen in de Grote Vasten: OT-lezingen op uren). De
engine markeert dat als `status: geen_liturgie` wanneer de weekreeks dat
aangeeft.

### R5 — Rang en samenval

Bij samenval van feest/heilige en rijádovoe (of meerdere overrides) volgt
Moskou-rang. Configuratie: `data/lezingen/rang.yaml`.

| Rang | Standaard-modus |
|------|-----------------|
| `groot` | `vervangen` — alleen feestlezing |
| `vigil` / `polyeleos` / `doxologie` | `auto`: **zondag** → `toevoegen` (rijádovoe + feest); **weekdag** → `vervangen` |
| `zesstichiria` / `gewoon` | `negeren` — alleen rijádovoe |

Overrides mogen `rang` en/of expliciete `modus` zetten. Bij meerdere matches
wint de hoogste `prioriteit`. Wanneer een feest de rijádovoe **vervangt**
(andere perikopen), vermeldt het resultaat `R5` en optioneel het onderdrukte
`rijadovoe`-blok. Bij twijfel: ROCOR-kalender en voorbeeld hier vastleggen.

### R6 — Bronvermelding

Elke override en elk goedgekeurd voorbeeld noemt de geraadpleegde bron (URL of
drukwerk) en `geraadpleegd`-datum.

## Verantwoording / bronnen

| Bron | URL | Rol |
|------|-----|-----|
| MP-kalender | http://calendar.rop.ru | Officiële lezingen / BU |
| Патриархия — BU | https://patriarchia.ru/bu/tomorrow | Dagelijkse aanwijzingen |
| Azbyka — ukazatel’ | https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda | Index per periode |
| Azbyka — schema | https://azbyka.ru/shemy/tserkovnye_chtenyja.shtml | Jaarorde / Lucaanse sprong |
| Azbyka — зачало | https://azbyka.ru/zachala | Terminologie |
| Holy Trinity calendar | https://www.holytrinityorthodox.com/calendar/ | ROCOR-controle |
| Jordanville | https://jordanville.org/daily-orthodox-calendar/ | ROCOR-controle |

Drukwerk (jaarlijks): *Богослужебные указания* (Издательство Московской Патриархии).

## Implementatiestatus

| Regel | Status in code |
|-------|----------------|
| R1 | deels (kalenderhulp via `kalender.py`) |
| R2 | ja (feestoverrides + UI vandaag/datum) |
| R3 | ja (weekreeks + Lucaanse sprong; zie rooster) |
| R4 | deels (`geen_liturgie` via weekreeks) |
| R5 | ja (`rang.yaml` + modus vervangen/toevoegen/negeren) |
| R6 | documentair (data + voorbeelden) |

## Machine-leesbare voorbeelden

Pytest leest blokken ` ```lezingen-voorbeeld ` … ` ``` `.  
`status: implemented` moet slagen; `status: pending` wordt overgeslagen.

```lezingen-voorbeeld
id: pascha-2025
status: implemented
jaar: 2025
mmdd: "04-20"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Hand. 1:1-8"
  evangelie:
    - ref: "Joh. 1:1-17"
  regels:
    - R2
bron:
  label: "Azbyka — ukazatel’ (Pascha)"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: theofanie-nieuw
status: implemented
jaar: 2026
mmdd: "01-06"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Tit. 2:11-14; 3:4-7"
  evangelie:
    - ref: "Matt. 3:13-17"
  regels:
    - R2
    - R5
bron:
  label: "Azbyka / MP — Theofanie"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: palmzondag-2025
status: implemented
jaar: 2025
mmdd: "04-13"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Fil. 4:4-9"
  evangelie:
    - ref: "Joh. 12:1-18"
  regels:
    - R2
bron:
  label: "Azbyka — ukazatel’ (Palmzondag)"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: pinksteren-2025
status: implemented
jaar: 2025
mmdd: "06-08"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Hand. 2:1-11"
  evangelie:
    - ref: "Joh. 7:37-52; 8:12"
  regels:
    - R2
bron:
  label: "Azbyka — ukazatel’ (Pinksteren)"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: kerst-nieuw
status: implemented
jaar: 2026
mmdd: "12-25"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Gal. 4:4-7"
  evangelie:
    - ref: "Matt. 2:1-12"
  regels:
    - R2
    - R5
bron:
  label: "Azbyka — ukazatel’ (Kerst)"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: weekdag-na-pinksteren-voorbeeld
status: implemented
jaar: 2025
mmdd: "06-16"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Rom. 2:28-3:18"
  evangelie:
    - ref: "Matt. 6:31-34; 7:9-11"
  regels:
    - R3
bron:
  label: "Messia — ukazatel’ (2e week na Pinksteren, maandag)"
  url: "https://messia.ru/spravki/kalendar/lkcioprc.htm"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: ontslapen-vervangt-rijadovoe-2025
status: implemented
jaar: 2025
mmdd: "08-15"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Fil. 2:5-11"
  evangelie:
    - ref: "Luc. 10:38-42; 11:27-28"
  regels:
    - R2
    - R5
bron:
  label: "Azbyka — Ontslapen (groot feest vervangt vrijdag-rijádovoe)"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
notitie: "R5 vervangen: onderdrukte rijádovoe was 2 Kor. 1:12-20 / Matt. 22:23-33."
```

```lezingen-voorbeeld
id: elia-op-zondag-toevoegen-2025
status: implemented
jaar: 2025
mmdd: "07-20"
stijl: nieuw
verwacht:
  apostel:
    - ref: "Rom. 12:6-14"
    - ref: "Jak. 5:10-20"
  evangelie:
    - ref: "Matt. 9:1-8"
    - ref: "Luc. 4:22-30"
  regels:
    - R3
    - R2
    - R5
bron:
  label: "Menaion Elia + 6e zondag na Pinksteren (polyeleos auto/toevoegen)"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: aankondiging-op-pascha-1991-oud
status: implemented
jaar: 1991
mmdd: "03-25"
stijl: oud
verwacht:
  apostel:
    - ref: "Hand. 1:1-8"
    - ref: "Heb. 2:11-18"
  evangelie:
    - ref: "Joh. 1:1-17"
    - ref: "Luc. 1:24-38"
  regels:
    - R2
    - R5
bron:
  label: "Typikon — Kyriopascha 1991 (Juliaanse 25 maart = Pascha)"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: aankondiging-op-grote-zaterdag-2018-oud
status: implemented
jaar: 2018
mmdd: "03-25"
stijl: oud
verwacht:
  apostel:
    - ref: "Rom. 6:3-11"
    - ref: "Heb. 2:11-18"
  evangelie:
    - ref: "Matt. 28:1-20"
    - ref: "Luc. 1:24-38"
  regels:
    - R2
    - R5
bron:
  label: "Typikon — Aankondiging op grote zaterdag 2018"
  url: "https://azbyka.ru/days/p-ukazatel-evangelskih-i-apostolskih-chtenij-na-kazhdyj-den-goda"
  geraadpleegd: "2026-08-16"
```

```lezingen-voorbeeld
id: theofanie-otstupka-schets
status: pending
jaar: 2025
mmdd: "01-13"
stijl: nieuw
verwacht:
  apostel:
    - ref: "(Bogoyavlenskaya otstupka — in te vullen)"
  evangelie:
    - ref: "(idem)"
  regels:
    - R3
notitie: "Optioneel later: Theofanie-отступка in de winterreeks (aparte Azbyka-regel)."
```
