# Datamodel

Beheerders: wat u mag wijzigen, wat generate.py overschrijft, en how-to’s
staan op de site onder **Voor beheerders** (`site/content/beheer/`). Dit
bestand blijft de veldsemantiek van entries.

Elke entry is één YAML-bestand in `data/feesten/`, `data/heiligen/` of
`data/vasten/`.

## Datum en stijl (vaste jaarcyclus)

```yaml
datum:
  waarde: "08-15"          # MM-DD = feestdatum
  # stijl weglaten = gregoriaans (default) — alleen documentatie van de invoer
  stijl: juliaans          # of: gregoriaans
  # optioneel expliciet dubbel:
  # gregoriaans: "08-15"
  # juliaans: "08-15"
```

De **feestdatum** is de kalenderdag van het feest (bijv. Ontslapen = 15 augustus).
Die dagnaam is gelijk in de nieuwe (Gregoriaanse) en oude (Juliaanse) kalender.
`stijl` legt alleen vast hoe de beheerder de waarde bedoelde; er wordt géén
automatische +13 op de feestdatum zelf toegepast.

De offset Gregoriaans−Juliaans is **jaarafhankelijk** (13 tot 2099, 14 vanaf 2100:
`⌊Y/100⌋ − ⌊Y/400⌋ − 2`). Die offset zet vaste feesten op hun **wereldlijke
vierdatum** in de stand Oud (jaarkalender, home, datumpagina, ICS “oud”).
De paascyclus blijft in beide standen op de wereldlijke Orthodoxe Pascha-datum.

## Paascyclus

```yaml
cyclus: paascyclus
datum:
  stijl: gregoriaans       # default; berekende datums zijn wereldlijk
  paascyclus:
    anker: pascha
    offset_dagen: 0        # t.o.v. Orthodox Pascha (negatief = vóór)
```

Orthodox Pascha volgt de Alexandrijnse/Juliaanse computus (Meeus); alle Orthodoxe
kerken delen die datum. Generatie/ICS gebruiken het bereik **huidig jaar −2 … +25**.

## Namen

Canonieke weergavenamen staan **in het entry-YAML** als `namen.primair`
en optioneel `namen.alternatief`. Conventie:
`site/content/beheer/how-to-namen.md`.

Ids (bestandsnamen) blijven stabiel; wijzig de getoonde naam, niet het id.

Eén persoon is één bestand. Andere spellingen en historische namen horen
in `alternatief`. Na een merge van twee ids blijft het canonieke id de
bestandsnaam; de oude id(s) komen in `id_aliassen` (voor oude URL’s) én
als naam in `alternatief` (zoeken en index).

## Vasten

```yaml
soort: vasten
# Wekelijks (ISO-weekdag 1=ma … 7=zo):
cyclus: wekelijks
datum:
  weekdagen: [3]           # woensdag

# Vaste periode (MM-DD … MM-DD):
cyclus: jaar
datum:
  van: "08-01"
  tot: "08-14"

# Paascyclus-periode:
cyclus: paascyclus
datum:
  paascyclus:
    anker: pascha
    van_offset_dagen: -48
    tot_offset_dagen: -1
# of hybride: van_offset_dagen + datum.tot (MM-DD), bv. Apostelvasten
```

Pagina’s onder `/vasten/{id}/`; zichtbaar in meneon/agenda/kalender met
aan/uit-filters. ICS: `vasten-*.ics` en combinaties met heiligen/feesten.

Het **Meneon** (`/meneon/`, optioneel `?dag=MM-DD`) toont alleen de vaste
jaarcyclus. Een **datumpagina** (`/datum/?jaar=2026&dag=08-15`) toont wat er
op die dag in dat jaar valt, inclusief paascyclus en wekelijks vasten.

Optioneel op entries:

```yaml
vastenniveau: streng   # streng | wijn_olie | vis | lichter | vrij
onderdrukt_wekelijks_vasten: true   # wo/vr niet apart tonen (impliciet bij niveau: vrij)
```

**Voorrang (weergave, kalenderkleur, ICS):** wekelijks wo/vr-vasten is de
restcategorie. Het verdwijnt als die dag al in een **vastenperiode** valt
(Ontslapen, Geboorte, Apostolisch, Grote Vasten, Grote Week) of in een
vastenvrije periode (`vastenniveau: vrij`). Een named periode *is* het vasten
van die dag; vrijdagvasten niet nog eens apart. ICS zet dat als **één
dagregel** (titel met niveau), niet als losse woensdagvasten naast de periode.

Twee geneste periodes overlappen in de huidige data niet (Grote Vasten eindigt
vóór de Grote Week).

**Effectief niveau (home/datumpagina):** het getoonde niveau is één regel,
niet de som van overlappende vasten.

1. Basis = de dekkende periode. Zonder periode: wo/vr.
2. In een `streng`-periode (Grote Vasten, Ontslapen, Grote Week): weekdag
   `streng`; za/zo `wijn_olie`, **behalve** de Grote Week.
3. In Apostelen- en Geboortevasten (`lichter` als seizoen): ma/wo/vr `streng`,
   di/do `wijn_olie`, za/zo `vis`; 20–24 december geen vis.
4. Een feest met `vastenniveau` **versoepelt alleen**. In de Grote Week niet
   verder dan `wijn_olie`. Lazarus-zaterdag is kaviaar in het typikon; wij
   tonen `wijn_olie`.
5. Buiten een periode: een feest mét `observances: […, vasten]` **legt** het
   vasten op; anders versoepelt het alleen wo/vr of zet het uit (`vrij`).

Rang bij vergelijking: `streng` < `wijn_olie` ≈ `lichter` < `vis` < `vrij`.
**Normatief voor de dagregel:** `data/regels/vasten.yaml`. Cleruspagina:
`/uitleg/vasten/`; technische bijlage: `/uitleg/vasten-technisch/` (niet in het
uitleg-overzicht). How-to: `/beheer/how-to-vasten/`. Code: `scripts/vasten.py`
en `site/assets/js/calendar.js`.

## Lezingen (Apostel / Evangelie)

Normatieve regels: **`docs/specs/lezingen.md`** (traditie Moskou, ROCOR bij
twijfel). Clerus: `/uitleg/lezingen/`; technisch: `/uitleg/lezingen-technisch/`.

Data: `data/lezingen/` (`feest-overrides.yaml`, `weekreeks.yaml`, `rang.yaml`,
`config.yaml`, optioneel `parochies/<id>.yaml`, `meta.yaml`). Actieve
parochielijst in deze repo: `parochie: den-haag` (klooster Den Haag, niet
Groningen); niet stilzwijgend wijzigen. Engine:
`scripts/lezingen.py`. Machine-leesbare voorbeelden in de spec sturen pytest.
Build schrijft `site/static/data/lezingen-dagen.json` (per stijl/jaar/mmdd, met
`daglabel` / `modus` / optioneel `rijadovoe`); UI op vandaag/`/datum/` en
overzichtspagina `/lezingenrooster/`.

## Observances (kleuren)

```yaml
observances: [feest, vasten]   # optioneel; default volgt soort
```

Het jaarrooster ondersteunt gecombineerde kleuren (feest+vasten, heilige+vasten).

## Kalenderranden (voorfeest, nafeest, synaxis)

Rond de twaalf grote feesten staan gewone `soort: feest`-entries:

- **voorfeest** — één dag of `van`/`tot` (Kerst 20–24 dec., Theofanie 2–5 jan.)
- **nafeest** — periode tot en met de teruggave (apodosis)
- **synaxis** — dag na Kerst (Moeder Gods), na Theofanie (Johannes), na
  de Aankondiging (Gabriël)
- **Pokrov** (1 okt.) — groot Moeder-Godsfeest in de Moskou-traditie, niet
  één van de twaalf
- **teruggave** van Hemelvaart en Pinksteren (paascyclus); teruggave van
  Pascha bestond al

Palmzondag heeft geen nafeest (Grote Week). De Aankondiging heeft geen lang
nafeest, wel de synaxis van Gabriël. Het nafeest van de Ontmoeting toont de
volle jaarcyclus; in Boterweek of Grote Vasten bekort het typikon die periode.

## Weekdag t.o.v. een feestdatum

Geen derde cyclus (geen «kerstcyclus»). Wel dagen die aan een vaste
feestdatum hangen via de weekdag, met `cyclus: jaar`:

```yaml
datum:
  stijl: juliaans          # zelfde betekenis als bij Kerst: dagnaam
  weekdag_relatief:
    anker: "12-25"         # liturgische MM-DD
    weekdag: 7             # ISO: 1=ma … 7=zo
    welke: 1               # 1 = dichtstbijzijnde, 2 = de volgende
    richting: voor         # of: na
```

Strikt vóór/ná het anker: als 25 december zondag is, is «zondag vóór»
18 december, niet Kerst zelf. In de stand Oud is het anker de Juliaanse
feestdatum; de burgerlijke vierdatum schuift mee.

In deze kalender:

- `zondag-voorvaderen` — 2e zondag vóór Kerst
- `zondag-vaderen-voor-kerst` — zondag direct vóór Kerst
- `zondag-na-kerst` — zondag ná Kerst
- `zondag-na-theofanie` — zondag ná Theofanie

Die dagen staan **niet** in het Meneon (geen vaste MM-DD); wel op
jaarkalender, datumpagina en ICS. Functie: `weekday_relative_date` in
`scripts/kalender.py`.

## Heiligen: selectie en betekenis

Selectiecriteria (wie in de lijst hoort) staan op `/uitleg/heiligen/`;
veldsemantiek hier. How-to: `/beheer/how-to-heiligen-feesten/`.

```yaml
betekenis_lage_landen: |
  Apart stuk: wat deze heilige voor het christendom of de Orthodoxie
  in de Lage Landen betekende.
selectie: voldoet            # of: nader-onderzoek | kandidaat-schrappen
selectie_toelichting: "…"    # optioneel; niet op de publieke pagina
id_aliassen: [lubuinus]      # oude ids na een merge
```

- **`betekenis_lage_landen`** — verplicht bij `bronlaag: nagekeken` voor
  `soort: heilige`. Zelfde referentieverplichting als verhaal/samenvatting.
  Eigen kop op de heiligenpagina (**Betekenis voor de Lage Landen**); ook in
  `site/static/data/entries.json` (alleen bij heiligen).
- **`selectie`** — toetsing aan de criteria. Ontbreekt bij een heilige:
  behandel als `nader-onderzoek`. Waarden: `voldoet`, `nader-onderzoek`,
  `kandidaat-schrappen`. Verschijnt niet op de publieke heiligenpagina.
- **`id_aliassen`** — oude `[a-z0-9_-]+` ids; niet gelijk aan het eigen id
  en niet gelijk aan een ander levend entry-id. `generate.py` zet Hugo
  `aliases` (`/heiligen/<oud-id>/`).

Niemand wordt automatisch geschrapt. `kandidaat-schrappen` is een markering
voor een later, expliciet besluit.

Werklijst (beslissingen, geen catalogustelling): [`docs/inventaris.md`](inventaris.md).
`selectie` staat per heilige in YAML; gegenereerd overzicht `/beheer/selectie/`.
Later (niet gebouwd): [`docs/voorstellen.md`](voorstellen.md).

## Referenties

Verhaal, samenvatting of `betekenis_lage_landen` mag alleen als er minstens
één referentie is.
Elke referentie heeft `bron_id` en/of `label`, plus een **raadpleegbare locator**:

- `url` — bij voorkeur, of
- `isbn` (+ optioneel `pagina`), of
- `locator` — vrije tekst (archief, app, signatuur, …)

```yaml
referenties:
  - bron_id: oca-calendar
    url: "https://www.oca.org/saints/lives"
    geraadpleegd: "2026-08-16"
  - label: "Handboek X"
    isbn: "978-…"
    pagina: "120–124"
    geraadpleegd: "2026-08-16"
```

`bron_id` verwijst naar `data/bronnen/bronnen.yaml` (naam/metadata); de locator
hoort **ook** op de referentie zelf te staan.

## Bronlaag

- `encyclopedie` — tekst volgt open naslagwerken (Wikipedia, heiligen.net)
- `nagekeken` — nagekeken tekst met traceerbare bronnen (lexikon, vita, …)

Zelfde paginastructuur; `generate.py` zet een publieke bronzin.
Default als het veld ontbreekt: `encyclopedie`.

Voor **heiligen** geldt `nagekeken` alleen als:

1. `betekenis_lage_landen` aanwezig en niet leeg is, en
2. er minstens één referentie is die **niet** alleen Wikipedia of
   heiligen.net is (die twee mogen aanvullen).

Feesten en vasten: `nagekeken` blijft «nagekeken tekst met traceerbare
bronnen» (bestaande referentieverplichting bij verhaal/samenvatting).

Verouderd: `status: stub` / `status: curated`.

## Plaatsen

Register: [`data/plaatsen.yaml`](../data/plaatsen.yaml). Op een heilige:

```yaml
locaties:
  - utrecht              # plaats-id, geen vrije tekst
rustplaats:
  plaats: maastricht
  toelichting: "Sint-Servaasbasiliek"
```

`soort: plaats` krijgt een marker als minstens één heilige die id in
`locaties` heeft. `soort: streek` (Vlaanderen, Friesland) is vooral voor
zoeken; een marker alleen als een heilige die streek-id zelf in
`locaties` heeft. Op een heilige: liever concrete plaatsen; streek-ids
alleen als aanvulling of bij gebrek aan een betere plek. Optioneel
`streek:` op een plaats koppelt zoeken («Vlaanderen» vindt Drongen).
Geen relieken- of bedevaartenlijst.

## Icoon

```yaml
icoon:
  bestand: iconen/willibrord.jpg   # relatief t.o.v. site/static/
  rechten: ok                      # ok | onbekend | nee
  licentie: "Publiek domein"
  bron: "Wikimedia Commons — File:…"
```

`rechten: ok` is verplicht om te tonen. `bestand` is een lokaal pad, geen
`http(s)`-URL. `bron` en `licentie` zijn verplicht als `bestand` gezet is.
`generate.py` zet het pad plus bijschrift op de entry-pagina. Ontbreekt
een legaal bestand: veld weglaten.
