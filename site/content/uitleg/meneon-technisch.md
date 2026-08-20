---
title: Meneon (technisch)
description: Vaste jaarcyclus in de UI; query dag; geen paascyclus
uitleg_stijl: meneon-technisch
build:
  list: never
  render: always
git_date: 2026-08-16
---

Technische bijlage bij de [uitleg Meneon]({{% ref "/uitleg/meneon" %}}).

## Adres

- `/meneon/` — bladeren (maand of alfabet) en zoeken
- `/meneon/?dag=08-15` — vaste cyclus van die feestdatum (MM-DD)

Alias: `/overzicht/` (front matter van `site/content/meneon/_index.md`).
Die `_index.md` is handmatig; `generate.py` overschrijft de body niet.

Layout: `site/layouts/_default/meneon.html`. Data:
`site/static/data/entries.json`.

## Filter

Het Meneon toont entries met een vaste plaats in het jaar:

- `cyclus: jaar` (heilige, feest, vaste vastenperiode)
- niet `cyclus: paascyclus`
- niet `cyclus: wekelijks`

Zoeken loopt over `namen.primair` en `namen.alternatief` uit het
entry-YAML.

In de Meneon-tabel toont `meneonTableHtml` een klein icoon als `entries.json`
`icoon` heeft. De jaarkalender-popover (`fillKalenderDagPopover`) toont
geen iconen.

## Gegenereerde entry-pagina’s

`scripts/generate.py` schrijft `site/content/heiligen/<id>.md`,
`site/content/feesten/<id>.md` en `site/content/vasten/<id>.md` opnieuw.
Onderaan een vaste dag staan links naar Meneon en datumpagina. Die
markdownbestanden zijn **geen** bron; bron is YAML onder `data/`.
