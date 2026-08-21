---
title: "Startpagina (Vandaag)"
description: "Contract: identiteit van de site plus de dagkaart van vandaag"
git_date: 2026-08-21
---

**Contract, geen echte inhoud.** Voor wie: bezoeker. Canonieke URL: `/`.
Bron: handmatig `site/content/_index.md` (URL `/`) plus dezelfde
JS-dagkaart als de datumpagina.

De startpagina *is* de datumpagina van de huidige burgerlijke dag. Alle
slots van [Datumpagina]({{% ref "/beheer/pagina-opbouw/datumpagina" %}})
gelden hier ook. Extra, alleen hier:

## Sitenaam (kop)

**Wel:** de sitenaam als link naar vandaag; info-tip (popover) over wat
de site is. Terugkerende gebruikers gaan voor: geen identiteitszin op
de startpagina zelf. Wie voor het eerst komt en nieuwsgierig is, komt
de popover tegen.

**Niet:** een tweede navigatie; interne padnamen (`data/`, YAML).

## Identiteitszin (body van `_index.md`)

**Gesloten.** De zin in HTML-commentaar blijft commentaar (niet
zichtbaar). Identiteit hoort bij de sitenaam-popover, niet in de body.

## Dagkaart

Zie [Datumpagina]({{% ref "/beheer/pagina-opbouw/datumpagina" %}})
(titelrij, vasten, Nieuw/Oud, dagtype, lezingen, heiligen).
