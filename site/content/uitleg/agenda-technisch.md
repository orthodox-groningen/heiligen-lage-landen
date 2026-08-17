---
title: Agenda (technisch)
description: ICS-feeds, bestandsnamen en wat generate.py overschrijft
uitleg_stijl: agenda-technisch
build:
  list: never
  render: always
git_date: 2026-08-16
---

Technische bijlage bij de [uitleg Agenda]({{% ref "/uitleg/agenda" %}}).

How-to: [site bouwen en publiceren]({{% ref "/beheer/how-to-publiceren" %}}).

## Feeds

`scripts/generate.py` schrijft `site/static/ics/<sleutel>-<stijl>.ics`.
Die bestanden worden bij elke generate **gewist en opnieuw gezet**. Niet
met de hand redigeren.

| Sleutel | Inhoud |
| --- | --- |
| `alles` | heiligen + feesten + vasten |
| `heiligen` | alleen heiligen |
| `feesten` | vaste feesten + paascyclus |
| `vasten` | vastenperiodes + wekelijks |
| `heiligen-feesten` | zonder vasten |
| `heiligen-vasten` | zonder feesten |
| `feesten-vasten` | zonder heiligen |

`stijl` is `nieuw` of `oud`. De agendapagina bouwt **één** knop uit de
keuzes van de bezoeker (categorieën + stijl + downloaden/abonneren). Er is
geen lijst van alle feeds op de pagina. UI:
`site/layouts/_default/agenda.html` en `calendar.js`.

- **Abonneren:** de knop kopieert de HTTPS-URL van het gekozen `.ics`-bestand
  naar het klembord; how-to’s op de pagina zeggen waar die URL geplakt wordt.
- **Downloaden:** dezelfde URL met `download`-attribuut.

## Gedrag

- **nieuw:** vaste feesten op de feestdatum (burgerlijk = dagnaam);
  paascyclus op de berekende Orthodoxe datum.
- **oud:** vaste feesten op Juliaanse feestdatum → burgerlijke vierdatum;
  paascyclus ongewijzigd; titel bevat de Juliaanse dagnaam.
- Wekelijks vasten: burgerlijke weekdag, in beide stijlen. Onderdrukking
  in vastenperiodes en vastenvrije weken: zelfde regel als op de
  datumpagina (`context_entries` in `build_ics`).

Bereik: huidig jaar −2 … +25 (`ICS_YEAR_BACK` / `ICS_YEAR_FORWARD`).

`site/content/agenda/_index.md` is handmatig (body blijft staan).
