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
Evangelielezingen. Ze **vervangen** de doorlopende lezing tenzij de override
expliciet `modus: toevoegen` heeft (fase 3).

### R3 — Doorlopende weekreeks (nog niet geïmplementeerd)

Buiten feestoverrides: Apostel/Evangelie volgens de week na Pascha of na
Pinksteren en de weekdag (ma–zo), inclusief de Lucaanse sprong volgens Moskou.
→ Zie fase 2.

### R4 — Vasten / geen liturgie (documentair)

Op sommige vastendagen is er geen liturgie met Apostel/Evangelie van het type
“van de dag” (bijv. bepaalde weekdagen in de Grote Vasten: OT-lezingen op uren).
De engine markeert dat later expliciet; vooralsnog geen automatische uitspraak
buiten gedocumenteerde overrides.

### R5 — Rang en samenval (nog niet geïmplementeerd)

Bij samenval van heilige en rijádovoe of twee feesten volgt Moskou-rang
(groot feest > polyeleos > …). Bij twijfel: ROCOR-kalender raadplegen en de
uitkomst hier als voorbeeld vastleggen. → Fase 3.

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
| R2 | ja (`scripts/lezingen.py` + `data/lezingen/`) |
| R3 | pending |
| R4 | pending |
| R5 | pending |
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
id: weekdag-na-pinksteren-voorbeeld
status: pending
jaar: 2025
mmdd: "06-16"
stijl: nieuw
verwacht:
  apostel:
    - ref: "(rijádovoe — in te vullen)"
  evangelie:
    - ref: "(rijádovoe — in te vullen)"
  regels:
    - R3
notitie: "Fase 2: doorlopende weekreeks + Lucaanse sprong."
```

```lezingen-voorbeeld
id: samenval-schets
status: pending
jaar: 2025
mmdd: "08-15"
stijl: nieuw
verwacht:
  apostel:
    - ref: "(feest en/of dag — in te vullen)"
  evangelie:
    - ref: "(feest en/of dag — in te vullen)"
  regels:
    - R5
notitie: "Fase 3: Ontslapen vs. eventuele rijádovoe/samenval volgens Moskou."
```
