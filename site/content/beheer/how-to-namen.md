---
title: "Weergavenamen wijzigen"
description: "Namen in data/namen.yaml; ids en bestandsnamen blijven stabiel"
weight: 30
git_date: 2026-08-16
---

De **getoonde naam** van een heilige, feest of vasten wijzigt u in
`data/namen.yaml`. Het **id** (bestandsnaam van de YAML) blijft gelijk.
Zoeken in het Meneon gebruikt ook de alternatieve namen.

How-to entries: [heilige of feest]({{% ref "/beheer/how-to-heiligen-feesten" %}}).

## Waar

Twee secties in hetzelfde bestand:

- `entries.<id>` — alles wat een eigen YAML-bestand heeft
- `labels.<id>` — termen zonder eigen entry (bijvoorbeeld een label dat
  alleen in de UI voorkomt)

```yaml
entries:
  aankondiging:
    primair: Aankondiging aan de Moeder Gods
    alternatief:
    - Aankondiging
    - Annunciatie
```

`primair` is verplicht. `alternatief` is een lijst; die namen zijn
zoekbaar, maar niet de titel van de pagina.

## Wat er gebeurt

`scripts/load_entries.py` past `namen.yaml` toe **over** `namen:` in het
entry-bestand. Staat een id in `namen.yaml`, dan wint die. Ontbreekt het
id daar én ontbreekt `namen.primair` in de YAML, dan faalt het laden.

Na wijzigen:

```text
python scripts/generate.py
```

Overal waar de naam staat (pagina, Meneon, kalender, ICS-titel) volgt de
nieuwe primaire naam. Oude ICS-abonnees zien de nieuwe titel na de
volgende publicatie.

## Wat u niet doet

- Het id / de bestandsnaam hernoemen «omdat de spelling anders moet» —
  dat verbreekt links en ICS-uids. Liever `primair` aanpassen en de oude
  spelling onder `alternatief` houden.
- Alleen `site/content/heiligen/<id>.md` aanpassen — die pagina wordt
  overschreven.
