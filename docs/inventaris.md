# Inventaris heiligen van de Lage Landen

Werklijst voor stap 4 van het verbeterplan. Geen YAML schrijven tot deze
lijst is nagekeken. `selectie` in de catalogus blijft tot die review
`nader-onderzoek` (default).

Criteria (normatief voor gebruikers):
[Heiligen van de Lage Landen](../site/content/uitleg/heiligen.md).
Velden: [docs/datamodel.md](datamodel.md).

Post-schisma-onderzoek (17 augustus 2026):
[docs/onderzoek/post-schisma-orthodoxe-heiligen-lage-landen.md](onderzoek/post-schisma-orthodoxe-heiligen-lage-landen.md).

## Review

- [ ] Voorgestelde scores van de huidige 62 heiligen akkoord of aangepast
- [ ] Pre-schisma-gaten: wie in stap 5, wie later
- [ ] Post-schisma: Johannes en Sophrony in stap 5; C-heiligen blijven buiten
      de catalogus tenzij later een ander besluit volgt
- [ ] Daarna: `selectie` / `selectie_toelichting` in YAML zetten
      (`/beheer/selectie/`)

Niemand van de huidige lijst wordt verwijderd. `kandidaat-schrappen` is
alleen een markering.

## Besluiten (17 augustus 2026)

| Id (voorstel) | Naam | Actie | Grond |
| --- | --- | --- | --- |
| `johannes-van-shanghai` | Johannes Maximovitsj van Shanghai | **toevoegen** in stap 5 | Categorie A: institutionele ontwikkeling van de Orthodoxie in Nederland |
| `sophrony-van-essex` | Sophrony (Sacharov) van Essex | **toevoegen** in stap 5 | Categorie B: liturgie in Gent (14 september 1980); geestelijke raad aan de stichteres van Asten |

Voorgestelde ids volgen `[a-z0-9_-]+`. Feestdag, `betekenis_lagenlanden` en
`status: curated` horen in stap 5, met referenties die niet alleen Wikipedia
of heiligen.net zijn. De claim over het Nederlandse bisdom (1965) later
toetsen aan synodale stukken; tot die tijd mag de tekst `stub` blijven als
de betekenis-bronnen kerkelijke websites zijn.

## Niet automatisch invoeren

Alleen lokale cultus of patroonschap (categorie C), of invloed uitsluitend
via een andere heilige (D), voldoet niet aan «heeft bijgedragen aan de
Orthodoxie in NL/BE».

| Heilige | Onderzoek | Waarom niet automatisch |
| --- | --- | --- |
| Silouan de Athoniet | D/C | Geen persoonlijke relatie met NL/BE; invloed via Sophrony en Essex; parochie/cultus is patroonschap |
| Porfyrios van Kavsokalivia | C | Parochie Tilburg (vanaf 2014); geen eigen historische bijdrage |
| Nektarios van Egina | C | Patroon van Eindhoven (1988); geen eigen historische bijdrage |
| Paisios de Athoniet | C | Parochie Lasne; geen eigen historische bijdrage |
| Alexander Nevski | C | Patroon van Rotterdam; geen eigen historische bijdrage |
| Dorothea van Kashin | C | Kapel bij Asten; lokale verering |

Pre-schisma patroonheiligen van huidige parochies (Maximos de Belijder,
Theofano, Antonius en Theodosius van Kiev) horen niet in deze
post-schisma-lijst. Of zij als Lage-Landen-heiligen in de catalogus
thuis horen, is een aparte vraag (alleen patroonschap volstaat niet).

## Pre-schisma: ontbreekt, wel toetsen

Startpunt. Alleen opnemen als de heilige in de Lage Landen is geweest **en**
daar iets heeft gedaan (niet alleen doorreis).

| Voorstel-id | Naam | Toets |
| --- | --- | --- |
| `servatius` | Servatius van Maastricht / Tongeren | Duidelijke kandidaat (apostel van de Maasstreek) |
| `otger` | Otger | Metgezel van Wiro en Plechelm (Odiliënberg) |
| `odulphus` | Odulphus | Friesland / Stavoren / Utrecht |
| `begga` | Begga | Dochter van Iduberga; Andenne |
| `monulphus` | Monulphus | Bisschop van Maastricht (samen met Gondulphus) |
| `gondulphus` | Gondulphus | Bisschop van Maastricht |
| `rumold` | Rumold van Mechelen | Martelaar / Mechelen |

Niet uitputtend. Andere namen alleen na bron, niet ad hoc.

## Huidige catalogus (62) — voorgestelde score

Kolom **voorstel** is nog niet in YAML gezet.

### Voldoet (voorstel)

In de Lage Landen geweest en daar iets gedaan (prediking, stichting,
martelaarschap, bestuur van kerk of klooster).

| Id | Toelichting |
| --- | --- |
| `acharius-van-doornik` | Bisschop van Doornik |
| `adelbert` | Egmond; metgezel van Willibrord |
| `adelgondis-van-drongen` | Drongen |
| `albericus-van-utrecht` | Bisschop van Utrecht |
| `alena-van-dilbeek` | Martelares Dilbeek |
| `alubertus-van-utrecht` | Wijbisschop Utrecht |
| `amalberga-van-susteren` | Abdis Susteren |
| `amalberga-van-temse` | Temse |
| `amandus-van-maastricht` | Maastricht / Elno |
| `ansfried-van-utrecht` | Bisschop van Utrecht |
| `aubertus-van-kamerijk` | Bisschop van Kamerijk |
| `bavo` | Gent |
| `bernulphus` | Bisschop van Utrecht; sterfjaar 1054 (vóór/op de schisma-grens, westers episcopaat in de Lage Landen) |
| `bonifatius` | Martelaarschap Dokkum; missie in Frisia |
| `cunera` | Rhenen |
| `domitianus` | Bisschop van Maastricht |
| `dymphna` | Geel |
| `eligius` | Bisdom Noyon-Doornik; prediking in Vlaanderen |
| `engelmund` | Velsen / Holland |
| `ermelindis` | Brabant (Meldert) |
| `floribert` | Bisschop van Luik |
| `foillan` | Fosses |
| `frederich` | Bisschop van Utrecht |
| `gertrudis` | Abdis van Nijvel |
| `gommar` | Lier |
| `gregorius-van-utrecht` | Utrecht; leerling van Bonifatius |
| `gudula-van-brussel` | Brussel |
| `hubertus-van-maastricht` | Maastricht / Luik |
| `hunger-van-utrecht` | Bisschop van Utrecht |
| `iduberga` | Nijvel |
| `jeroen-van-noordwijk` | Noordwijk |
| `lambertus` | Bisschop van Maastricht |
| `lebuinus` | Deventer (id_aliassen: `lubuinus`) |
| `ludger` | Geboren bij Utrecht; missie in Frisia |
| `marcellinus-van-utrecht` | Utrecht |
| `oda-van-amay` | Amay |
| `oda-van-de-peel` | Peel |
| `odrada` | Balen |
| `plechelm-von-odilienberg` | Odiliënberg / Nederrijn |
| `radboud` | Bisschop van Utrecht |
| `remaclus` | Maastricht / Stavelot |
| `swidbert` | Missie met Willibrord in Frisia; later Kaiserswerth |
| `theodaard-van-maastricht` | Maastricht |
| `trudo` | Sint-Truiden |
| `ultan` | Fosses (met Foillan) |
| `walfridus-bedum` | Bedum |
| `werenfrid` | Westervoort / Friesland |
| `willibrord` | Apostel van de Friezen |
| `wiro` | Limburg / Odiliënberg |
| `woutruide` | Bergen (Waudru) |
| `wulfram` | Missie onder de Friezen |

### Nader onderzoek (voorstel)

| Id | Toelichting |
| --- | --- |
| `adelgonda` | Maubeuge (nu Frankrijk); historisch Henegouwen |
| `agricolaus-van-maastricht` | Vroege/legendarische bisschop; historicity |
| `egbert-van-rathmelsigi` | Rath Melsigi (Ierland); zond missionarissen naar Frisia, zelf mogelijk nooit in de Lage Landen |
| `folciunus` | Tervas / Terwaan (nu Frankrijk) |
| `medardus` | Bisschop van Noyon; band met de Lage Landen vooral via later bisdom/cultus |
| `quirillus-van-tongern` | Vroege/legendarische bisschop van Tongeren |
| `winnocus` | Wormhout / Frans-Vlaanderen |

### Kandidaat-schrappen (voorstel)

Niet verwijderen. Markering tot een uitdrukkelijk besluit.

| Id | Toelichting |
| --- | --- |
| `adela-van-vlaanderen` | Gestorven 1079; westerse cultus na het schisma, geen orthodoxe bijdrage aan NL/BE |
| `fridolin` | Titel: verlichter van de Boven-Rijn (Säckingen); geen aantoonbaar werk in de Lage Landen |
| `walburga` | Abdis van Heidenheim; cultus elders is geen «daar iets gedaan» |
| `winnibald` | Heidenheim / Engeland; geen aantoonbaar werk in de Lage Landen |

## Stap 5 (nog niet doen)

Na review, in deze volgorde:

1. Ontbrekenden die duidelijk voldoen (in ieder geval Servatius).
2. `johannes-van-shanghai` en `sophrony-van-essex`.
3. Kernset bestaande heiligen: betekenis, verhaal, referenties, `curated`
   waar de lat gehaald wordt.

C-heiligen uit het post-schisma-onderzoek niet in deze ronde.