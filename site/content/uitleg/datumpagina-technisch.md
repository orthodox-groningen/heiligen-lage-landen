---
title: Datumpagina’s (technisch)
description: URL-parameters, entries.json en wat de dagweergave toont
uitleg_stijl: datumpagina-technisch
build:
  list: never
  render: always
git_date: 2026-08-16
---

Technische bijlage bij de [uitleg Datumpagina’s]({{% ref "/uitleg/datumpagina" %}}).

## Adres

`/datum/?jaar=2026&dag=08-15`

- `jaar` — burgerlijk jaar
- `dag` — MM-DD op de burgerlijke kalender (niet de Juliaanse dagnaam)

Ontbreken de parameters, dan vult `site/assets/js/calendar.js` «vandaag».
De layout is `site/layouts/_default/datum.html`; de body van
`site/content/datum/_index.md` blijft bij genereren staan (handmatig
beheerd).

## Brondata in de browser

De pagina leest `site/static/data/entries.json` (gegenereerd). Per entry
staan onder meer `soort`, `cyclus`, `feestdatum`, `occurrences` (paascyclus)
en `period_occurrences` (periodes). Wijzig die JSON **niet** met de hand;
`scripts/generate.py` schrijft hem opnieuw.

## Wat er op een dag komt

Op de burgerlijke datum van dat jaar:

1. Vaste feesten en heiligen waarvan de feestdatum (Nieuw) of de
   burgerlijke vierdatum (Oud) op die dag valt.
2. Paascyclus-dagen waarvan de berekende datum in dat jaar die dag is
   (onafhankelijk van Nieuw/Oud).
3. Vastenperiodes die die dag dekken, plus wekelijks vasten als er geen
   periode of vastenvrije week is.

Effectief vastenniveau: `scripts/vasten.py` / dezelfde mengregel in
`calendar.js`. Zie [Vasten (technisch)]({{% ref "/uitleg/vasten-technisch" %}}).

Het Meneon filtert op feestdatum zonder jaar; zie
[Meneon (technisch)]({{% ref "/uitleg/meneon-technisch" %}}).
