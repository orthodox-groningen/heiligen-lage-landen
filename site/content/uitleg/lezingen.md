---
title: Lezingen van de dag
description: 'Apostel en Evangelie: regels Moskou (ROCOR bij twijfel), met verantwoording'
---

Deze pagina is de **publieke spiegel** van de normatieve specificatie
`docs/specs/lezingen.md`. Wijzig die specificatie (regels + voorbeelden);
daarna moet `scripts/lezingen.py` meekomen — pytest bewaakt dat.

---

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
| R2 | ja (feestoverrides + `lezingen-dagen.json` + UI vandaag/datum) |
| R3 | pending |
| R4 | pending |
| R5 | pending |
| R6 | documentair (data + voorbeelden) |
