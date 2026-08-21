# Bronnen voor `betekenis` van grootfeesten en Pascha

Onderzoeksnotitie bij het veld `betekenis` (twaalf grootfeesten en
Pascha). Geen canonieke spec, geen duplicaat van
[`bron/docs/specs/terminologie.md`](https://github.com/orthodox-ronl/bron/blob/main/docs/specs/terminologie.md).
Datamodel: [`docs/datamodel.md`](../datamodel.md).

**Datum:** 21 augustus 2026.

## Rangorde

1. Ontvangen kerkvader (feesthomilie of traktaat). Staat de vader in
   de dienst (Chrysostomos’ paaspreek), dan is dat tegelijk dienstboek.
2. Dienstboek (Triodion, Pentekostarion, Menaion, Euchologion, Oktoechos).
3. Oecumenische canon (o.a. Nicea I, 20; Trullo 90).
4. Typikon / jurisdictietabel voor de tafel, met economia.
5. Synodale catechese: OCA *The Orthodox Faith* (Hopko) — brug, niet de last.
6. Johannes van Shanghai of Sophrony van Essex alleen als **naspraak**
   van 1–3, uitgegeven tekst. Niet als enige bron. Hun band met de Lage
   Landen niet in `betekenis` uitspreken.
7. OrthodoxWiki: vingerwijzing.

`goedkeuring` blijft leeg tot een levende toets. `bronlaag: nagekeken`
is naspeurbaarheid, geen toets.

## Per feest

Locators staan in de YAML onder `referenties`. Hier de bedoelde last.

### Kerst (`kerst`)

- Primair: Athanasius, *De incarnatione*; Gregorius van Nazianze, *Oratie 38*.
- Leiding: paramonie / koninklijke uren (Hopko Church Year, Nativity).
- Naspraak: Johannes van Shanghai, kerstboodschap 1956 (West-Europese kudde).

### Theofanie (`theofanie`)

- Primair: Gregorius van Nazianze, *Oratie 39*.
- Leiding: grote waterwijding (hymnen via Hopko, Epiphany).
- Naspraak: Johannes van Shanghai, preek op Theofanie (ROCOR-synodesite; Bitola 1928 — niet een Haagse tekst).

### Kruisverheffing (`kruisverheffing`)

- Primair: Cyrillus van Jeruzalem, catechese 13.
- Leiding: feestdag én vasten (`vastenniveau: streng`).
- Naspraak: Johannes van Shanghai, *The Cross Preserves the Universe* (citeert het Oktoechos-exapostilarion).

### Pascha (`pascha`)

- Primair: Chrysostomos’ paaspreek in de nachtdienst; Gregorius van Nazianze, *Oratie 45*.
- Canon: Nicea I, 20 (staande bidden tot Pinksteren).
- Geen LL-heilige nodig.

### Pinksteren (`pinksteren`)

- Primair: Gregorius van Nazianze, *Oratie 41*; Basilius, *Over de Heilige Geest*.
- Canon: Nicea I, 20; knielgebeden van de vespers als liturgisch einde.
- Geen LL-heilige.

### Palmzondag (`palmzondag`)

- Primair: Chrysostomos, homilie 66 op Matteüs (intocht, veulen).
- Dienstboek via Hopko, Holy Week (metten Grote Maandag).
- Geen LL-heilige.

### Transfiguratie (`transfiguratie`)

- Primair: Chrysostomos, homilie 56 op Matteüs (Thabor).
- Leiding: vruchtenwijding (Hopko); vis in het Ontslapenvasten.
- Sophrony niet gebruikt: geen harde zin over dit feest als regel, alleen het licht in het algemeen.

### Ontslapen (`ontslapen-moeder-gods`)

- Primair: Johannes van Damascus, homilieën op het Ontslapen (Fordham Sourcebook).
- Leiding: Ontslapenvasten 1–14 augustus (OCA fasting outline).
- Johannes van Shanghai *Veneration of Mary* niet gebruikt: geen concrete naspraak van Damascus in deze ronde.

### Hemelvaart (`hemelvaart`)

- Primair: Chrysostomos, homilie 2 op Handelingen.
- Leiding: tien dagen wachten op de Geest (Hopko / Pentekostarion).

### Aankondiging (`aankondiging`)

- Primair: Proclus van Constantinopel, homilie 1 op de Theotokos (CPG 5800).
- Leiding: feestliturgie ook in de Vasten (`vastenniveau: vis`).

### Ontmoeting (`ontmoeting-in-de-tempel`)

- Primair: Cyrillus van Jeruzalem, catechese 12 (menswording; Simeon/wet).
- Kaarsenwijding niet als pan-Orthodoxe plicht.

### Geboorte van de Moeder Gods (`geboorte-moeder-gods`)

- Primair: Andreas van Kreta, homilieën in Cunningham, *Wider Than Heaven* (SVS, ISBN).

### Tempelgang (`tempelgang-moeder-gods`)

- Primair: Germanos van Constantinopel, eerste homilie op de tempelgang.

### Grote Week (vasten-entry `grote-week`)

Geen `betekenis` (generator toont dat veld alleen bij `soort: feest`).
`verhaal` volgt Chrysostomos’ paaspreek (tafel) en Hopko Holy Week
(mee naar Jeruzalem). Vasten is middel, geen telos.

## Bewust niet

- Paisios, Nektarios, Porfyrios als bron van feestdagleiding.
- «Heilige van de Lage Landen» in de betekenistekst.
- Troparion als pagina-onderdeel (zie `site/content/beheer/ideeen.md`).
