---
title: Nieuwe en Oude kalender (technisch)
description: Offset, feestdatum versus burgerlijke vierdatum, ICS-oud
uitleg_stijl: nieuw-oud-technisch
build:
  list: never
  render: always
git_date: 2026-08-16
---

Technische bijlage bij de [uitleg Nieuwe en Oude kalender]({{% ref "/uitleg/nieuw-oud" %}}).
De gebruikerspagina beschrijft de keuze in gewone taal. Hier staat hoe de
site die keuze doorrekent.

Stap-voor-stap voor wie data wijzigt: [Voor beheerders]({{% ref "/beheer" %}}).

## Feestdatum versus burgerlijke vierdatum

De **feestdatum** is de dagnaam in het kerkelijk jaar (Kerst = 25 december).
Die dagnaam is in nieuw en oud gelijk; er wordt **geen** automatische
verschuiving op de feestdatum zelf toegepast.

De knop **Oud** zet vaste feesten op hun **burgerlijke vierdatum**: de
Juliaanse feestdatum omgerekend naar de Gregoriaanse kalender van dat jaar.
Pascha en de paascyclus blijven op de berekende Orthodoxe (burgerlijke)
datum.

Code: `scripts/kalender.py` (`julian_feast_to_civil_date`,
`gregorian_to_julian_calendar`) en, gespiegeld in de browser,
`site/assets/js/calendar.js`.

## Offset

De offset Gregoriaans−Juliaans is jaarafhankelijk:

`⌊Y/100⌋ − ⌊Y/400⌋ − 2`

Dat is **13** tot en met 2099, **14** vanaf 2100. ICS-feeds «oud» gebruiken
dezelfde omrekening.

`datum.stijl` in YAML documenteert alleen hoe de beheerder de invoer
bedoelde (`gregoriaans` of `juliaans`). Het is geen schakelaar voor Nieuw/Oud
op de site. Zie [Feestdatum (technisch)]({{% ref "/uitleg/feestdatum-technisch" %}}).

## Agenda-feeds

Bij stijl `oud` vallen ICS-afspraken op de burgerlijke vierdatum. In de titel
staat de Juliaanse feestdatum tussen haakjes. Wekelijks vasten blijft op de
burgerlijke weekdag. Zie [Agenda (technisch)]({{% ref "/uitleg/agenda-technisch" %}}).
