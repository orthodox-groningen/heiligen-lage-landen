---
title: Vasten
description: Welk vastenniveau de kalender op een dag toont, en waarom
generator: data/regels/vasten.yaml
---

De [datumpagina]({{% ref "/uitleg/datumpagina" %}}) en *Vandaag* tonen **één**
vastenregel per dag (niet twee vasten tegelijk). Deze pagina is de
**normatieve uitleg** van die regel: wat Moskou (en bij twijfel ROCOR) voorschrijft,
hoe wij dat tot vijf niveaus vereenvoudigen, en welke voorbeelden de tests
afdwingen.

Wijzigingen horen in `data/regels/vasten.yaml`. Daarna `python3 scripts/generate.py`
(deze pagina wordt opnieuw gegenereerd) en de code in `scripts/vasten.py` plus
`site/assets/js/calendar.js`. Een commit waarin de uitleg iets anders belooft
dan de kalender, laat de tests zakken.

Dit is een hulpmiddel voor overleg met de clerus, geen biechtregel. Economia
en persoonlijke zegen gaan altijd vóór een website.

## Bronkeuze

We volgen in eerste instantie   het **Slavische typikon** zoals de
**Russisch-Orthodoxe Kerk (Moskou)** het publiceert: Typikon hoofdstuk 32–33
(en h. 49 voor Lazarus-zaterdag), het *Православный церковный календарь* van
de Uitgeverij van het Moskouse Patriarchaat
([calendar.rop.ru](http://calendar.rop.ru)), en de gangbare dagkalender
[days.pravoslavie.ru](https://days.pravoslavie.ru/).

Bij twijfel of een lacune in die publieke kalenders kijken we naar **ROCOR**,
die hetzelfde Sabbas-typikon hanteert (o.a. de Engelse weergave van h. 33 bij
Fr. Seraphim Rose / orthodoxinfo, en de OCA-samenvatting die uit dezelfde
Slavische traditie komt).

De parochie viert vaste feesten op de **feestdatum** (nieuw of oud via de
knop); de *regels* hier gaan over liturgische dagen (Aankondiging, Grote Week,
…), niet over of 25 maart burgerlijk of Juliaans is.

## Niveaus op deze site

| Id | Weergave | Betekenis |
|---|---|---|
| `streng` | streng | Geen vlees, zuivel, vis, wijn of olie. Droog eten en gekookt zonder olie slaan we tot dit ene niveau samen. |
| `wijn_olie` | wijn en olie | Wijn en plantaardige olie toegestaan; geen vis. Lazarus-kaviaar valt hieronder (we hebben geen apart niveau «kaviaar»). |
| `vis` | vis | Vis, wijn en olie toegestaan; geen vlees of zuivel. |
| `lichter` | lichter | Alleen als seizoenslabel (Boterweek: geen vlees, wel zuivel). Voor Apostelen- en Geboortevasten rekenen we het weekschema van typikon h. 33 om naar streng / wijn_olie / vis per weekdag. |
| `vrij` | vastenvrij | Geen vasten (lichte weken, Kerst, Theofanie). |

## Regels die de kalender volgt

Elke regel heeft een stabiel id (`R-…`). Wijzig je de verwachting in `data/regels/vasten.yaml`, dan falen de tests tot `scripts/vasten.py` en `site/assets/js/calendar.js` meegaan.

### R-periode-boven-wekelijks — Een vastenperiode vervangt woensdag- en vrijdagvasten

Wekelijks wo/vr is de restcategorie. Valt de dag in een vastenperiode of
een vastenvrije periode, dan is *die* periode het vasten van de dag;
woensdag- of vrijdagvasten wordt niet apart getoond (kalender, datumpagina, ICS).

Voorbeelden (burgerlijke datum, nieuwe kalender):

| Datum | Verwacht | Toelichting |
|---|---|---|
| 2026-03-20 | `streng` | Vrijdag in de Grote Vasten; geen aparte Vrijdagvasten. |
| 2026-08-07 | `streng` | Vrijdag in het Ontslapen-vasten. |

### R-streng-weekend-olie — Zaterdag en zondag in een strenge periode — wijn en olie

In de Grote Vasten en het Ontslapen-vasten is de weekdag streng; zaterdag
en zondag wijn en olie (geen vis), **behalve** in de Grote Week.

Voorbeelden (burgerlijke datum, nieuwe kalender):

| Datum | Verwacht | Toelichting |
|---|---|---|
| 2026-03-21 | `wijn_olie` | Zaterdag in de Grote Vasten. |
| 2026-04-11 | `streng` | Grote Zaterdag — geen weekendversoepeling. |
| 2026-04-10 | `streng` | Grote Vrijdag. |

### R-lichter-weekschema — Apostelen- en Geboortevasten — weekschema van typikon h. 33

In een vastenperiode met seizoenslabel `lichter` (Apostolisch vasten,
Geboortevasten): maandag/woensdag/vrijdag **streng**; dinsdag/donderdag
**wijn en olie**; zaterdag/zondag **vis**. (Boterweek is geen
vastenperiode van dit type: die blijft `lichter` op elke dag.)

Voorbeelden (burgerlijke datum, nieuwe kalender):

| Datum | Verwacht | Toelichting |
|---|---|---|
| 2026-11-20 | `streng` | Vrijdag in het Geboortevasten. |
| 2026-11-17 | `wijn_olie` | Dinsdag in het Geboortevasten. |
| 2026-02-20 | `lichter` | Vrijdag in de Boterweek (zuivel, geen vlees). |

### R-geboortevasten-20-24 — Geboortevasten 20–24 december — geen vis

Van 20 tot en met 24 december (feestdatum) geen vis, ook niet op
zaterdag of zondag (typikon h. 33). Wij capen dan op wijn en olie.

Voorbeelden (burgerlijke datum, nieuwe kalender):

| Datum | Verwacht | Toelichting |
|---|---|---|
| 2026-12-20 | `wijn_olie` | Zondag 20 december, nog Geboortevasten, geen vis. |

### R-feest-versoepelt — Een feest versoepelt een periode, het maakt hem niet strenger

Heeft een feestdag `vastenniveau`, dan geldt het soepelste van periode-dag
en feest. Voorbeelden uit het typikon: vis op Aankondiging (tot Palmzondag),
Palmzondag, Transfiguratie, Tempelgang; vis op wo/vr voor Geboorte van de
Moeder Gods, Petrus en Paulus, Geboorte van Johannes.

Voorbeelden (burgerlijke datum, nieuwe kalender):

| Datum | Verwacht | Toelichting |
|---|---|---|
| 2026-03-25 | `vis` | Aankondiging op woensdag in de Grote Vasten. |
| 2026-08-06 | `vis` | Transfiguratie in het Ontslapen-vasten. |
| 2026-11-21 | `vis` | Tempelgang (zaterdag in het Geboortevasten; vis al via het weekschema). |
| 2026-04-05 | `vis` | Palmzondag (tussen Grote Vasten en Grote Week). |

### R-lazarus-geen-vis — Lazarus-zaterdag — kaviaar, geen vis

Typikon h. 49: op Lazarus-zaterdag gekookt met olie, wijn, en kaviaar
als die er is; **geen vis**. Vis is voor Palmzondag. Wij hebben geen
niveau «kaviaar» en tonen daarom **wijn en olie** (zelfde als andere
zaterdagen in de Grote Vasten).

Voorbeelden (burgerlijke datum, nieuwe kalender):

| Datum | Verwacht | Toelichting |
|---|---|---|
| 2026-04-04 | `wijn_olie` | Lazarus-zaterdag 2026. |

### R-grote-week-cap — In de Grote Week geen vis, ook niet op de Aankondiging

Valt de Aankondiging in de Grote Week, dan vis → hoogstens wijn en olie
(typikon h. 33: tot Grote Donderdag olie en wijn; Grote Vrijdag alleen
wijn). Op deze site capen we de hele Grote Week op `wijn_olie` als een
feest verder zou gaan. (Op de nieuwe kalender valt 25 maart zelden in de
Grote Week; op de oude kalender kan het wel, zoals in 2026.)

Voorbeelden (burgerlijke datum, nieuwe kalender):

| Datum | Verwacht | Toelichting |
|---|---|---|

### R-vastenfeest-buiten-periode — Sommige feesten zijn zelf een vastendag

Buiten een periode: een feest mét `observances` die `vasten` bevatten,
**legt** het niveau op (Kruisverheffing, Onthoofding van Johannes: streng,
ook op zaterdag/zondag). Een feest zonder die observantie versoepelt
alleen wo/vr (vis) of zet wo/vr uit (`vrij` op Kerst en Theofanie).

Voorbeelden (burgerlijke datum, nieuwe kalender):

| Datum | Verwacht | Toelichting |
|---|---|---|
| 2026-09-14 | `streng` | Kruisverheffing op maandag. |
| 2026-08-29 | `streng` | Onthoofding van Johannes op zaterdag. |
| 2026-12-25 | `vrij` | Kerst op vrijdag — geen Vrijdagvasten. |
| 2026-09-08 | — | Geboorte van de Moeder Gods op dinsdag — geen vasten om te versoepelen. |

### R-vastenvrije-weken — Vastenvrije weken

Lichte Week, week van de Tollenaar en de Farizeeër, week na Pinksteren:
`vrij`, en wo/vr geldt niet.

Voorbeelden (burgerlijke datum, nieuwe kalender):

| Datum | Verwacht | Toelichting |
|---|---|---|
| 2026-04-13 | `vrij` | Maandag van de Lichte Week. |

## Bewuste vereenvoudigingen

- Droog eten (xerophagy) en gekookt zonder olie vallen beide onder `streng`. We tellen geen aantal maaltijden per dag.
- Kaviaar op Lazarus-zaterdag heeft geen eigen niveau; we tonen wijn en olie.
- Wijn-alleen op Grote Vrijdag (als de Aankondiging daarop valt) wordt niet van wijn-én-olie onderscheiden.
- Schelpdieren (geen ruggengraat) worden niet apart gemodelleerd; wie ze eet op een strenge dag volgt lokale zegen, niet deze site.

## Nog niet in de code

Dit zijn typikon-punten voor overleg. Zet er een regel + voorbeeld van in `regels.yaml` als de clerus ze wil; dan moet de code volgen.

- Olie/wijn op middelfeesten in de Grote Vasten (veertig martelaren van Sebaste, Voorfeest van de Aankondiging, …) — heiligen hebben nog geen `vastenniveau`.
- Vis op een heilige met doxologie of wakker in Apostelen-/Geboortevasten (typikon h. 33, rang van de dienst).
- Grote Donderdag: typikon staat wijn en olie toe; wij laten de Grote Week streng (behalve een eventuele Aankondiging-cap).
- Vooravond van Theofanie (5/6 januari) als aparte strenge dag.
- Tempelpatroon: vis of olie op de parochiële kermisdag.

## Referenties

- [Typikon, hoofdstuk 33 (Azbuka.ru)](https://www.azbyka.ru/otechnik/Pravoslavnoe_Bogosluzhenie/tipikon/33) *(typikon)* — O разрешении всего лета — Aankondiging tot Palmzondag vis; in de Grote Week olie/wijn; Apostelen- en Geboortevasten weekschema; Ontslapen-vasten vis alleen op Transfiguratie; Kruisverheffing en Onthoofding zonder vis.
- [Typikon h. 49, Lazarus-zaterdag (citaat via SPŽ)](https://spzh.eu/ru/socseti/79300-lazareva-subbota-pogovorim-ob-ikre-i-ne-tolyko) *(typikon)* — «Аще же и икру имамы…» — kaviaar, olie en wijn; geen vis.
- [Azbuka very — Пост по Типикону](https://azbyka.ru/post-po-tipikonu) *(moskou)* — Hedendaagse Russische uitleg van hetzelfde typikon.
- [Uitgeverij Moskous Patriarchaat — kerkelijk kalender](http://calendar.rop.ru) *(moskou)* — Officiële dagkalender; trapeza-notities per dag.
- [Календарь постов и трапез 2026 (Izd. MP, aankondiging)](http://www.rop.ru/novosti/article_post/otkryta-dlya-svobodnogo-skachivaniya-publikaciya-obschedostupnoy-versii-kalendarya-postov-i-trapez-na-2026-god) *(moskou)*
- [Pravoslavie.ru — Церковный календарь 2026](https://days.pravoslavie.ru/docs/2026_1.html) *(moskou)* — Sretenski-klooster (Moskou); veelgebruikte publieke kalender.
- [OCA — Fasting and Fast-Free Seasons](https://www.oca.org/liturgics/outlines/fasting-fast-free-seasons-of-the-church) *(slavisch)* — Engelse samenvatting van typikon h. 32–33 plus Triodion (Ware); zelfde Slavische lijn als Moskou/ROCOR.
- [The Rule of Fasting (Fr. Seraphim Rose / orthodoxinfo)](http://orthodoxinfo.com/praxis/father-seraphim-rose-fasting-rules.aspx) *(rocor)* — ROCOR-weergave van typikon h. 33, inclusief 20–24 december zonder vis.
- [OrthodoxWiki — Fasting](https://orthodoxwiki.org/Fasting) *(toelichting)*
- [OrthodoxWiki — Great Lent](https://orthodoxwiki.org/Great_Lent) *(toelichting)*
