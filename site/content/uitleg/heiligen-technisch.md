---
title: Heiligen van de Lage Landen (technisch)
description: Selectievelden, curated-lat, id_aliassen; bron is YAML onder data/heiligen/
uitleg_stijl: heiligen-technisch
build:
  list: never
  render: always
git_date: 2026-08-17
---

Technische bijlage bij de [uitleg Heiligen]({{% ref "/uitleg/heiligen" %}}).

Normatief datamodel: [docs/datamodel.md](https://github.com/orthodox-groningen/heiligen-lage-landen/blob/main/docs/datamodel.md).
Schema: `schemas/entry.schema.json`. How-to:
[heiligen en feesten wijzigen]({{% ref "/beheer/how-to-heiligen-feesten" %}}).
Validatie: `python scripts/validate.py`.

Bron: `data/heiligen/<id>.yaml`. Gegenereerde markdown onder
`site/content/heiligen/` niet redigeren.

## Selectiecriteria (normatief)

Zie de gebruikerspagina voor de formulering in gewone taal. In YAML:

```yaml
selectie: voldoet   # voldoet | nader-onderzoek | kandidaat-schrappen
selectie_toelichting: "Kort waarom, voor beheerders."
```

- Ontbreekt `selectie` bij een heilige: behandel als `nader-onderzoek`
  (`scripts/load_entries.py`).
- `selectie` en `selectie_toelichting` horen **niet** op de publieke
  heiligenpagina. Overzicht voor beheerders: `/beheer/selectie/`
  (gegenereerd).
- `kandidaat-schrappen` verwijdert niets; dat is een markering tot een
  expliciet besluit.

Werklijst (scores, gaten, post-schisma):
[docs/inventaris.md](https://github.com/orthodox-groningen/heiligen-lage-landen/blob/main/docs/inventaris.md).
`selectie` staat per heilige in YAML; overzicht `/beheer/selectie/`.

## Betekenis voor de Lage Landen

```yaml
betekenis_lagenlanden: |
  Apart stuk: betekenis voor het christendom of de Orthodoxie
  in de Lage Landen.
```

Verplicht bij `status: curated` voor `soort: heilige`. Als het veld gezet
is, gelden dezelfde referentie-eisen als bij `verhaal` / `samenvatting`.
`generate.py` zet het onder het kopje **Betekenis voor de Lage Landen**
en in `entries.json` (veld `betekenis_lagenlanden`, alleen heiligen).

## Status curated (heiligen)

`validate.py` weigert `status: curated` bij een heilige tenzij:

1. `betekenis_lagenlanden` niet leeg is, en
2. minstens één referentie **niet** Wikipedia of heiligen.net is
   (`bron_id` `wiki-heiligen` / `hnet`, of url/label met `wikipedia.org` /
   `heiligen.net`; OrthodoxWiki telt wél als eigen bron).

Feesten en vasten: curated blijft nagekeken tekst met traceerbare bronnen.

## Eén persoon, één id

Canonieke weergavenamen: `data/namen.yaml` (`primair` + `alternatief`).
Na samenvoegen van dubbele bestanden:

```yaml
id: lebuinus
id_aliassen:
  - lubuinus
```

- `id_aliassen`: oude ids, patroon `[a-z0-9_-]+`, niet het eigen id, niet
  een nog levend entry-id, uniek over de catalogus. Wordt Hugo `aliases`.
- Zet de oude naam(en) ook in `namen.yaml` onder `alternatief`, anders
  vindt zoeken ze niet (Meneon en heiligenindex).

## Referenties

Zie [docs/datamodel.md](https://github.com/orthodox-groningen/heiligen-lage-landen/blob/main/docs/datamodel.md).
Wikipedia en heiligen.net mogen aanvullen.
