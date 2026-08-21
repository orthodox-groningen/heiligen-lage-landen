---
title: "Ideeën"
description: "Toekomstige uitbreidingen; nog niet bouwen tot er een besluit is"
git_date: 2026-08-21
---

Eén verzamelplek voor ideeën en latere uitbreidingen. **Nog niet bouwen**
tot er een uitdrukkelijk besluit is. Geen YAML-velden of generatorwijziging
vanuit dit bestand alleen.

Dit is geen how-to en geen paginacontract. Contracten:
[Pagina-opbouw]({{% ref "/beheer/pagina-opbouw" %}}).

## Troparia en kondaken

Bij heiligen en feesten een hoofdstuk (of infobox-regel) met het
bijbehorende **troparion** en **kondakion**, met bron. Past bij zangers
en bij de rest van orthodox-ronl (zangstukken). Nog geen datamodel:
eerst één voorbeeldpagina uitschrijven (grootfeest of een kernheilige).

## Betekenis van feesten

Huidige feestpagina’s zijn kalenderfeit (wat/wanneer). Voor wie niet van
huis uit orthodox is, ontbreekt vaak: wat dit feest zegt over de weg naar
God.

Drie lagen, niet door elkaar:

1. **Gebeurtenis** — bestaande `verhaal` (kort, bron)
2. **Plaats in het jaar** — de kalender doet dit al
3. **Betekenis** — veld `betekenis` (1–3 alinea’s: geheim plus leiding
   van de Kerk; orthodox, weinig jargon; geen preek). Kerkvaders en
   dienstboek primair. Zelfde `bronlaag` als de rest van de pagina.

De twaalf grootfeesten **en Pascha** hebben nu `betekenis`. Voorfeest,
nafeest, synaxis, Heilige Week-dagen en Triodion-zondagen: nog niet;
die herhalen het grootfeest of vragen een eigen, latere ronde. Bronnen:
[`docs/onderzoek/feest-betekenis-bronnen.md`](https://github.com/orthodox-ronl/kalender/blob/main/docs/onderzoek/feest-betekenis-bronnen.md).

## Parochiepatronen

Patroon van een kerk is nu geen toelatingsgrond (zie
[uitleg heiligen]({{% ref "/uitleg/heiligen" %}}) en de C-lijst in
[docs/inventaris.md](https://github.com/orthodox-ronl/kalender/blob/main/docs/inventaris.md)).

Later denkbaar, **onderaan** de heiligen van een datum (na de
Lage-Landen-heiligen), duidelijk gemerkt, met link naar de parochiesite.
Pas als er een onderhouden lijst van parochiesites is. Geen vermenging
met `selectie: voldoet`.

**Volgende:** troparia/kondaken; daarna eventueel betekenis op Heilige
Week en andere kernfeesten.
