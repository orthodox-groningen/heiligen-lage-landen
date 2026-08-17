---
title: Toon van de week (technisch)
description: octoechos_toon in kalender.py; weergave in calendar.js
uitleg_stijl: toon-technisch
build:
  list: never
  render: always
git_date: 2026-08-17
---

Technische bijlage bij de [uitleg Toon van de week]({{% ref "/uitleg/toon" %}}).

## Formule

Wereldlijke datum `civil`. Orthodox Pascha van dat burgerlijk jaar; valt
`civil` vóór Pascha, dan Pascha van het vorige jaar. Thomaszondag is
Pascha plus zeven dagen.

- Pascha ≤ `civil` < Thomaszondag → toon **1** (Lichte Week)
- anders: `((civil − Thomaszondag).days // 7 % 8) + 1`

Bron: `scripts/kalender.py` (`octoechos_toon`). De titel op de datumpagina
spiegel dat in `site/assets/js/calendar.js` (`octoechosToon`). Nieuw/Oud
verschuift de toon niet: Pascha is dezelfde wereldlijke dag.

## Tests

`tests/test_octoechos.py`: Lichte Week en Thomaszondag 2026 = toon 1;
de week daarna = toon 2; na acht weken weer toon 1.
