---
title: Agenda (technisch)
description: ICS-feeds, bestandsnamen en wat generate.py overschrijft
uitleg_stijl: agenda-technisch
build:
  list: never
  render: always
git_date: 2026-08-19
---

Technische bijlage bij de [uitleg Agenda]({{% ref "/uitleg/agenda" %}}).

How-to: [site bouwen en publiceren]({{% ref "/beheer/how-to-publiceren" %}}).

## Feeds

`scripts/ics.py` (aanroep vanuit `scripts/generate.py`) schrijft
`site/static/ics/<sleutel>-<stijl>.ics`. Die bestanden worden bij elke
generate **gewist en opnieuw gezet**. Niet met de hand redigeren.
Bestandsnamen blijven gelijk; de inhoud is **dag-centrisch** (één `VEVENT`
per burgerlijke dag).

| Sleutel            | Inhoud                      |
| ------------------ | --------------------------- |
| `alles`            | heiligen + feesten + vasten |
| `heiligen`         | alleen heiligen             |
| `feesten`          | vaste feesten + paascyclus  |
| `vasten`           | vastenperiodes + wekelijks  |
| `heiligen-feesten` | zonder vasten               |
| `heiligen-vasten`  | zonder feesten              |
| `feesten-vasten`   | zonder heiligen             |

`stijl` is `nieuw` of `oud`. De agendapagina bouwt **één** knop uit de
keuzes van de bezoeker (categorieën + stijl + downloaden/abonneren). Er is
geen lijst van alle feeds op de pagina. UI:
`site/layouts/_default/agenda.html` en `calendar.js`.

- **Abonneren:** de knop kopieert de HTTPS-URL van het gekozen `.ics`-bestand
  naar het klembord; Apple krijgt extra een `webcal:`-link. How-to’s op de
  pagina zeggen waar die URL geplakt wordt.
- **Downloaden:** dezelfde URL met `download`-attribuut.

`X-WR-CALNAME` is kort, bijvoorbeeld `Orthodox · Lage Landen (nieuw)`.
`UID` is `uuid5` van `{sleutel}:{stijl}:{datum}`. Wie al geabonneerd is,
ziet bij de volgende verversing nieuwe UIDs (oude per-entry-afspraken
verdwijnen uit het abonnement).

## Gedrag

Eén hele-dag-afspraak per burgerlijke dag die in de subset iets toont.
`SUMMARY` volgt `day_title` in `scripts/ics.py` (spiegel `icsDayTitle` in
`calendar.js`): dagtype-feest, anders `daglabel` uit `lezingen-dagen.json`
als feesten in de feed zitten, anders heiligen, anders alleen het
vastenlabel. Vastenlabels komen uit `mix_vastenniveau` in
`scripts/vasten.py`. `URL` wijst naar de datumpagina.

`DESCRIPTION` volgt de datumpagina-box zonder website-links in de regels:
vastenregel, overige dagtype-feesten (`Ook:`), Apostel/Evangelie als
verwijzingstekst, heiligen, laatste regel `Meer:` naar de datumpagina.
Geen wiki-tekst, geen vertaalkeuze, geen Bijbel-deeplinks in het event.

- **nieuw:** vaste feesten op de feestdatum (burgerlijk = dagnaam);
  paascyclus op de berekende Orthodoxe datum.
- **oud:** vaste feesten op Juliaanse feestdatum → burgerlijke vierdatum;
  paascyclus ongewijzigd; Juliaanse dagnaam in de `DESCRIPTION`, niet in
  de titel.
- Wekelijks vasten: burgerlijke weekdag, in beide stijlen. Onderdrukking
  in vastenperiodes en vastenvrije weken: zelfde regel als op de
  datumpagina.

`X-PUBLISHED-TTL:P1D`. `TRANSP:TRANSPARENT`. Geen `VALARM`.

Bereik: huidig jaar −2 … +25 (`ICS_YEAR_BACK` / `ICS_YEAR_FORWARD`).

`site/content/agenda/_index.md` is handmatig (body blijft staan).
