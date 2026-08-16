---
title: "Vastenregels wijzigen"
description: "Periodes in data/vasten, mengregel in data/regels/vasten.yaml, code moet mee"
weight: 40
---

Er zijn **twee lagen**. Ze door elkaar halen is de meest voorkomende fout.

1. **Wat bestaat** — periodes en wekelijks vasten als entries:
   `data/vasten/*.yaml`, plus `vastenniveau` op feesten.
2. **Wat de kalender op een dag toont** — één effectief niveau, met
   voorrang en versoepeling: `data/regels/vasten.yaml`, uitgevoerd in
   `scripts/vasten.py` en `site/assets/js/calendar.js`.

De clerus leest [Uitleg: Vasten]({{% ref "/uitleg/vasten" %}}). De koppeling
naar ids en tests: [Vasten (technisch)]({{% ref "/uitleg/vasten-technisch" %}}).
Na een wijziging: [publiceren]({{% ref "/beheer/how-to-publiceren" %}}).

**Niet redigeren:** `site/content/uitleg/vasten.md`,
`site/content/uitleg/vasten-technisch.md`, en
`site/content/vasten/*.md`. Die drie komen uit generate.

## 1. Een periode of wekelijkse dag

Voorbeelden: `data/vasten/grote-vasten.yaml` (paascyclus-periode),
`data/vasten/ontslapen-vasten.yaml` (vaste MM-DD … MM-DD),
`data/vasten/woensdag-vasten.yaml` (`cyclus: wekelijks`).

Typische velden:

```yaml
soort: vasten
cyclus: jaar                 # of paascyclus, of wekelijks
vastenniveau: streng         # seizoensniveau van de periode
observances: [vasten]
datum:
  van: "08-01"
  tot: "08-14"
```

Wekelijks: `datum.weekdagen: [3]` (ISO: 1 = maandag … 7 = zondag).

`vastenniveau: vrij` (Lichte Week, week na Pinksteren, …) onderdrukt het
wekelijkse wo/vr-vasten op die dagen. Een named periode *is* het vasten
van de dag; vrijdagvasten wordt niet nog eens getoond.

Dit wijzigt **wanneer** iets loopt en welk seizoensniveau de periode heeft.
Het wijzigt niet de weekendversoepeling, het weekschema in het Apostelen-
en Geboortevasten, of «een feest versoepelt alleen». Dat is laag 2.

Ook namen van periodes: [namen.yaml]({{% ref "/beheer/how-to-namen" %}}).

## 2. De mengregel (wat er op de dag staat)

Bestand: `data/regels/vasten.yaml`.

- `inleiding`, `bronkeuze`, `niveaus`, `regels[].tekst` — tekst op de
  **cleruspagina**. Na `generate.py` is Uitleg → Vasten bijgewerkt.
- `regels[].id` — stabiel (`periode-boven-wekelijks`, …). Wordt `R-…` op
  de technische pagina.
- `regels[].voorbeelden` — burgerlijke `datum` + `verwachte_niveau`, of
  een synthetisch voorbeeld (`weekday`, `entries`, `mmdd`).
- `technisch.inleiding` — tekst van de technische bijlage.

**pytest** (`tests/test_vasten.py`) toetst elk voorbeeld tegen
`mix_vastenniveau` / `indicatie_op_datum`. Wijzigt u `verwachte_niveau`
omdat de clerus een andere uitkomst wil, dan moet de **code** dezelfde
uitkomst geven:

- `scripts/vasten.py` — serverkant, tests, generate
- `site/assets/js/calendar.js` — wat de bezoeker op Vandaag / datumpagina
  ziet

Die twee moeten hetzelfde doen. Alleen YAML aanpassen zonder code laat de
tests rood.

Synthetische voorbeelden (geen burgerlijke datum) zijn voor gevallen als
«Aankondiging in de Grote Week»: zeldzaam op de nieuwe kalender, wél
toetsbaar.

## 3. Een feest dat vasten versoepelt of oplegt

Op het feest zelf, niet in `vasten.yaml`:

```yaml
vastenniveau: vis
```

In een periode mag dat het getoonde niveau alleen **lichter** maken, nooit
strenger. Buiten een periode legt een feest met `observances` die `vasten`
bevatten het vasten op (Kruisverheffing: `streng`). Details en uitzonderingen
(Grote Week, Lazarus-zaterdag) staan in de clerustekst en in de code.

Nieuwe uitzondering: eerst met de clerus eens worden, dan een regel +
voorbeelden in `data/regels/vasten.yaml`, dan de code, dan generate.

## Controleren

1. Clerustekst en voorbeelden in `data/regels/vasten.yaml` (en zo nodig
   periode-YAML).
2. Code in `vasten.py` en `calendar.js` tot de voorbeelden kloppen.
3. `python -m pytest tests/test_vasten.py -q`
4. `python scripts/generate.py` — lees Uitleg → Vasten na; die pagina is
   nu de nieuwe clerustekst.
5. Steekproef op de datumpagina voor de voorbeelddata (jaar 2026 in de
   huidige voorbeelden).

«Wat nog niet in de kalender staat» op de cleruspagina is de lijst
`nog_niet` in dezelfde YAML: bewust geen regel tot er overleg is.
