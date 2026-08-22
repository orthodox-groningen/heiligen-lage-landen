---
title: Nieuwe en Oude kalender (technisch)
description: Offset, feestdatum versus burgerlijke vierdatum, ICS-oud
uitleg_stijl: nieuw-oud-technisch
build:
  list: never
  render: always
git_date: 2026-08-22
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

## Weergave op feest- en vastenpagina’s

Entry-pagina’s tonen **burgerlijke vierdata** (conventie B): de datum waarop
nieuwe-kalenderparochies vieren of vasten, en tussen haakjes die van
oude-kalenderparochies als die verschilt (`vierdatum_oud`, `van_oud` /
`tot_oud` in de Hugo-front matter; `oud_vierdatum_html` in `generate.py`).

Dat is **niet** de Juliaanse dagnaam van dezelfde burgerlijke dag. Pinksteren
2026 is 31 mei voor iedereen; er komt geen «18 mei» tussen haakjes.

- Vaste dag: feestdatum plus haakjes (`julian_feast_to_civil_date`).
- Paascyclus-dag of -periode (beide einden t.o.v. Pascha): één burgerlijke
  datum of van–tot, met bijschrift dat alle Orthodoxe parochies dezelfde
  burgerlijke dagen houden.
- Hybride periode (Apostelvasten) en weekdag-relatief: haakjes, omdat het
  einde of het anker een vaste feestdatum is.
- Popover `data-info-tip="vierdatum-oud"`; geen tweede Nieuw/Oud-knop op de
  entry-pagina.

## Offset

De offset Gregoriaans−Juliaans is jaarafhankelijk:

`⌊Y/100⌋ − ⌊Y/400⌋ − 2`

Dat is **13** tot en met 2099, **14** vanaf 2100. ICS-feeds «oud» gebruiken
dezelfde omrekening.

`datum.stijl` in YAML documenteert alleen hoe de beheerder de invoer
bedoelde (`gregoriaans` of `juliaans`). Het is geen schakelaar voor Nieuw/Oud
op de site. Zie [Feestdatum (technisch)]({{% ref "/uitleg/feestdatum-technisch" %}}).

## Agenda-feeds

Bij stijl `oud` vallen ICS-afspraken op de burgerlijke vierdatum. De
Juliaanse feestdatum staat in de beschrijving van de afspraak, niet in de
titel. Wekelijks vasten blijft op de burgerlijke weekdag. Zie
[Agenda (technisch)]({{% ref "/uitleg/agenda-technisch" %}}).
