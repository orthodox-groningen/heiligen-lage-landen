# Inventaris heiligen van de Lage Landen

Stap 4 van het verbeterplan. Scores staan in `data/heiligen/*.yaml`
(`selectie`, `selectie_toelichting`). Overzicht: `/beheer/selectie/`
(gegenereerd). Niemand van de huidige lijst is verwijderd;
`kandidaat-schrappen` is alleen een markering.

Criteria (normatief voor gebruikers):
[Heiligen van de Lage Landen](../site/content/uitleg/heiligen.md).
Velden: [docs/datamodel.md](datamodel.md).

Post-schisma-onderzoek (17 augustus 2026):
[eerste ronde](onderzoek/post-schisma-orthodoxe-heiligen-lage-landen.md),
[aanvulling Russische/ROCOR/parochielijsten](onderzoek/post-schisma-aanvulling-2026-08-17.md).

## Afbakening bij het scoren

- **Voldoet:** vóór het schisma in **huidig Nederland, België of Luxemburg**
  geweest én daar iets gedaan (prediking, stichting, martelaarschap, bestuur
  van kerk of klooster). Niet alleen doorreis.
- **Nader onderzoek:** werk vooral in historische Nederlanden die nu in
  Frankrijk liggen; of de persoon is te legendarisch om de toets hard te
  maken; of de band met de Lage Landen is vooral later bisdom/cultus.
- **Kandidaat-schrappen:** niet in de Lage Landen geweest; werk elders
  (Boven-Rijn, Heidenheim); of na het schisma westers, zonder orthodoxe
  bijdrage aan NL/BE.

Post-schisma: alleen Orthodox vereerd **én** bijgedragen aan de Orthodoxie
in NL/BE. Een kerk of parochie die naar iemand is genoemd, of een
Nederlandse dienst/vertaling, is daarvoor niet genoeg.

## Besluiten voor stap 5

Nieuwe YAML volgt in stap 5, in deze volgorde.

### Post-schisma — toevoegen

| Id | Naam | Grond |
| --- | --- | --- |
| `johannes-van-shanghai` | Johannes Maximovitsj van Shanghai | Categorie A: institutionele ontwikkeling van de Orthodoxie in Nederland |
| `sophrony-van-essex` | Sophrony (Sacharov) van Essex | Categorie B: liturgie in Gent (14 september 1980); geestelijke raad aan de stichteres van Asten |

Feestdag, `betekenis_lagenlanden` en `status: curated` in stap 5. Voor
Johannes de keten 1952 (bezoek) / 1954 (opname in zijn bisdom, wijding
van Jakob Akkersdijk, klooster Johannes de Doper in Den Haag) meenemen;
het bisdom van 1965 later toetsen aan synodale stukken. Pervijze
(1976, vanuit Den Haag) is bron voor Nederlandstalige liturgie, geen
aparte heilige.

### Post-schisma — niet invoeren

Alleen lokale cultus of patroonschap (C), of invloed uitsluitend via een
andere heilige (D).

| Heilige | Onderzoek | Waarom niet |
| --- | --- | --- |
| Silouan de Athoniet | D/C | Geen persoonlijke relatie met NL/BE; invloed via Sophrony |
| Tichon van Moskou | C | Parochie Nijmegen (2005); ROCOR-stichting is te indirect |
| Sergius van Radonezj | C | Parochie Amsterdam/Haarlem (2022); patroon, geen eigen bijdrage |
| Serafim van Sarov | C | Parochie Namen; kerk Luik (met Alexander Nevski) |
| Porfyrios van Kavsokalivia | C | Parochie Tilburg; geen eigen historische bijdrage |
| Nektarios van Egina | C | Patroon van Eindhoven; geen eigen historische bijdrage |
| Paisios de Athoniet | C | Parochie Lasne; geen eigen historische bijdrage |
| Alexander Nevski | C | Patroon van Rotterdam (en Luik); geen eigen historische bijdrage |
| Dorothea van Kashin | C | Kapel bij Asten; lokale verering |
| Maria van Egypte | C | ROCOR-parochie Aalsmeer |
| Johannes de Doper | C | Patroon van het Haagse missieklooster; universeel, pre-schisma |
| Johannes Chrysostomos | C | Parochie Maastricht (met Servatius); universeel, pre-schisma |
| Nicolaas van Myra | C | Klooster Hemelum e.a.; universeel, pre-schisma |

Pre-schisma patroonheiligen van huidige parochies (Maximos de Belijder,
Theofano, Antonius en Theodosius van Kiev, Nicolaas, Johannes de Doper,
Chrysostomos) horen niet automatisch in de catalogus: alleen
patroonschap volstaat niet. Servatius is geen patroon-alleen: hij
werkte in Maastricht/Tongeren en blijft op de toevoeglijst hieronder.

### Pre-schisma — toevoegen

Alle zeven voldoen aan «in de Lage Landen geweest en daar iets gedaan».

| Id | Naam | Toets |
| --- | --- | --- |
| `servatius` | Servatius van Maastricht / Tongeren | Apostel van de Maasstreek; eerste bisschop van Tongeren |
| `otger` | Otger | Metgezel van Wiro en Plechelm; stichting Odiliënberg |
| `odulphus` | Odulphus | Kanunnik van Utrecht; missie in Friesland (Stavoren) |
| `begga` | Begga | Dochter van Iduberga; stichting Andenne |
| `monulphus` | Monulphus | Bisschop van Maastricht (samen met Gondulphus) |
| `gondulphus` | Gondulphus | Bisschop van Maastricht |
| `rumold` | Rumold van Mechelen | Martelaar / Mechelen |

Niet uitputtend. Andere namen alleen na bron, niet ad hoc. In stap 5 eerst
Servatius, Otger (completteert Wiro/Plechelm) en Odulphus, daarna de rest
van deze zeven, daarna Johannes en Sophrony, daarna de bestaande kernset.

## Huidige catalogus (62)

Scores 17 augustus 2026. Toelichting per id staat in de YAML.

### Voldoet (50)

`acharius-van-doornik`, `adelbert`, `adelgondis-van-drongen`,
`albericus-van-utrecht`, `alena-van-dilbeek`, `alubertus-van-utrecht`,
`amalberga-van-susteren`, `amalberga-van-temse`, `amandus-van-maastricht`,
`ansfried-van-utrecht`, `bavo`, `bernulphus`, `bonifatius`, `cunera`,
`domitianus`, `dymphna`, `eligius`, `engelmund`, `ermelindis`, `floribert`,
`foillan`, `frederich`, `gertrudis`, `gommar`, `gregorius-van-utrecht`,
`gudula-van-brussel`, `hubertus-van-maastricht`, `hunger-van-utrecht`,
`iduberga`, `jeroen-van-noordwijk`, `lambertus`, `lebuinus`, `ludger`,
`marcellinus-van-utrecht`, `oda-van-amay`, `oda-van-de-peel`, `odrada`,
`plechelm-von-odilienberg`, `radboud`, `remaclus`, `swidbert`,
`theodaard-van-maastricht`, `trudo`, `ultan`, `walfridus-bedum`,
`werenfrid`, `willibrord`, `wiro`, `woutruide`, `wulfram`.

### Nader onderzoek (7)

| Id | Toelichting |
| --- | --- |
| `adelgonda` | Maubeuge; historisch Henegouwen, nu Frankrijk |
| `agricolaus-van-maastricht` | Vroege/legendarische bisschop van Maastricht |
| `aubertus-van-kamerijk` | Kamerijk nu in Frankrijk; bisdom reikte tot Henegouwen |
| `folciunus` | Folquinus van Terwaan; bisdom nu in Frankrijk |
| `medardus` | Noyon (Picardië); band vooral via later bisdom of cultus |
| `quirillus-van-tongern` | Vroege bisschop van Tongeren; of hij historisch is, is onzeker |
| `winnocus` | Wormhout; historisch Vlaanderen, nu Frankrijk |

### Kandidaat-schrappen (5)

Niet verwijderen tot een uitdrukkelijk besluit.

| Id | Toelichting |
| --- | --- |
| `adela-van-vlaanderen` | Gestorven 1079; westerse cultus na het schisma |
| `egbert-van-rathmelsigi` | Ierland; zelf niet in de Lage Landen |
| `fridolin` | Boven-Rijn (Säckingen) |
| `walburga` | Abdis van Heidenheim |
| `winnibald` | Heidenheim / Engeland |
