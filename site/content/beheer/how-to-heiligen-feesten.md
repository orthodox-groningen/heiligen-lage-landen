---
title: "Heilige of feest toevoegen of wijzigen"
description: "YAML onder data/, namen.yaml, referenties; nooit de gegenereerde markdown"
weight: 20
git_date: 2026-08-17
---

Heiligen en feesten bestaan als **bron** in YAML. De pagina’s die u op de
site ziet, zijn een afdruk. Wijzig de YAML; laat `site/content/heiligen/`
en `site/content/feesten/` met rust.

Datamodel: [docs/datamodel.md](https://github.com/orthodox-groningen/heiligen-lage-landen/blob/main/docs/datamodel.md).
Schema: `schemas/entry.schema.json`. Publiceren:
[site bouwen]({{% ref "/beheer/how-to-publiceren" %}}).

## Nieuw id

1. Kies een id: alleen `a-z`, `0-9`, `_` en `-`, beginnend met een letter
   of cijfer. Voorbeeld: `willibrord`, `ontslapen-moeder-gods`.
2. Dat id is de **bestandsnaam** zonder `.yaml` en blijft stabiel. Wijzig
   later liever de getoonde naam dan het id.
3. Zet de canonieke naam in `data/namen.yaml` onder `entries.<id>` (primair,
   optioneel `alternatief`). Zie [namen wijzigen]({{% ref "/beheer/how-to-namen" %}}).

## Bestand

- Heilige: `data/heiligen/<id>.yaml` met `soort: heilige`
- Feest: `data/feesten/<id>.yaml` met `soort: feest`

Minimaal: `id`, `soort`, `datum`. Voor een verhaal, samenvatting of
`betekenis_lagenlanden` is minstens één **referentie** verplicht, met een
locator: `url`, of `isbn`, of `locator`.

### Vaste dag

```yaml
id: willibrord
soort: heilige
status: stub             # curated: zie onder
cyclus: jaar
lagenlanden: true
datum:
  waarde: "11-07"
  stijl: gregoriaans     # documentatie van de invoer; default gregoriaans
```

`stijl` schakelt de site niet tussen Nieuw en Oud. Zie
[Feestdatum (technisch)]({{% ref "/uitleg/feestdatum-technisch" %}}).

### Paascyclus

```yaml
cyclus: paascyclus
datum:
  paascyclus:
    anker: pascha
    offset_dagen: 0      # 0 = Pascha; negatief = dagen vóór
```

Periodes (vasten of een week) gebruiken `van_offset_dagen` /
`tot_offset_dagen`, of hybride `van_offset_dagen` plus `datum.tot` (MM-DD),
zoals het Apostelvasten.

## Namen in het entry-bestand

U *mag* `namen.primair` in de YAML zetten. Bij laden **wint**
`data/namen.yaml`. Zet nieuwe namen dus daar, anders lijkt de YAML-naam te
werken tot iemand `namen.yaml` aanvult.

## Vasten op een feest

Optioneel:

```yaml
vastenniveau: vis        # streng | wijn_olie | vis | lichter | vrij
observances: [feest, vasten]
```

`vastenniveau` op een feest **versoepelt** in een periode, of legt vasten
op buiten een periode als `observances` vasten bevat (Kruisverheffing,
Onthoofding). De mengregel zelf wijzigt u niet hier. Zie
[vastenregels]({{% ref "/beheer/how-to-vasten" %}}).

## Referenties

```yaml
referenties:
  - bron_id: oca-calendar
    url: "https://www.oca.org/saints/lives"
    geraadpleegd: "2026-08-16"
  - label: "Handboek X"
    isbn: "978-…"
    pagina: "120–124"
    geraadpleegd: "2026-08-16"
```

`bron_id` wijst naar `data/bronnen/bronnen.yaml`. De locator hoort **ook**
op de referentie in de entry, niet alleen in de catalogus.

## Heiligen: selectie, betekenis, status

Criteria in gewone taal: [Heiligen van de Lage Landen]({{% ref "/uitleg/heiligen" %}}).
Velden: [technisch]({{% ref "/uitleg/heiligen-technisch" %}}) en
[docs/datamodel.md](https://github.com/orthodox-groningen/heiligen-lage-landen/blob/main/docs/datamodel.md).

```yaml
betekenis_lagenlanden: |
  Wat deze heilige voor het christendom of de Orthodoxie
  in de Lage Landen betekende.
selectie: voldoet          # of nader-onderzoek | kandidaat-schrappen
selectie_toelichting: "…"  # optioneel; niet op de publieke pagina
```

- Ontbreekt `selectie`: behandel als `nader-onderzoek`. Zet het veld als u
  een heilige toetst. `kandidaat-schrappen` verwijdert niets.
- Scores en gatenlijst: [docs/inventaris.md](https://github.com/orthodox-groningen/heiligen-lage-landen/blob/main/docs/inventaris.md).
  Overzicht: [Selectie heiligen]({{% ref "/beheer/selectie" %}}). Nieuwe
  heiligen (Servatius, Otger, Johannes van Shanghai, Sophrony van Essex,
  …) in stap 5 volgens die lijst.
- `betekenis_lagenlanden` is een **apart** stuk, niet hetzelfde als
  `verhaal` of `samenvatting`.

`status: stub` — basisgegevens, kort of geen nagekeken betekenis-stuk.
`status: curated` bij een **heilige** alleen als:

1. `betekenis_lagenlanden` niet leeg is, en
2. minstens één referentie niet Wikipedia of heiligen.net is
   (die twee mogen aanvullen; OrthodoxWiki telt wél).

Feesten: `curated` blijft nagekeken tekst met traceerbare bronnen.

`validate.py` weigert een heilige die `curated` is zonder die lat.

## Dubbele ids samenvoegen

Eén persoon = één bestand. Houd het canonieke id (bestandsnaam). Zet oude
ids in `id_aliassen` en de oude namen in `data/namen.yaml` onder
`alternatief`:

```yaml
id: lebuinus
id_aliassen:
  - lubuinus
```

`id_aliassen` mag het eigen id niet herhalen en geen id dat nog als
apart YAML-bestand bestaat. Verwijder het oude bestand in dezelfde
wijziging. `generate.py` zet oude ids om in Hugo-aliases en schrijft
`betekenis_lagenlanden` onder **Betekenis voor de Lage Landen**. Selectie
staat op [Selectie heiligen]({{% ref "/beheer/selectie" %}}), niet op de
publieke pagina.

## Controleren

```text
python scripts/validate.py
python scripts/generate.py
python -m pytest -q
```

Daarna de entry op de site: Meneon (vaste dag), datumpagina (dit jaar),
eventueel ICS. Klopt de naam niet, dan eerst `namen.yaml`.
