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

## Namen (één plek wijzigen)

Canonieke weergavenamen staan in **`data/namen.yaml`**:

- `entries.<id>.primair` / `alternatief` — wint bij laden over `namen:` in
  individuele YAML-bestanden
- `labels.<id>` — termen zonder eigen entry (bijv. Vleesvaarwel als label)

Ids (bestandsnamen) blijven stabiel; wijzig alleen de getoonde namen in
`namen.yaml`.

Eén persoon is één bestand. Andere spellingen en historische namen horen
in `alternatief` (via `namen.yaml`). Na een merge van twee ids blijft het
canonieke id de bestandsnaam; de oude id(s) komen in `id_aliassen` (voor
oude URL’s) én als naam in `alternatief` (zoeken en index).

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
van die dag; vrijdagvasten niet nog eens apart.

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
`config.yaml`, optioneel `parochies/<id>.yaml`, `meta.yaml`). Engine:
`scripts/lezingen.py`. Machine-leesbare voorbeelden in de spec sturen pytest.
Build schrijft `site/static/data/lezingen-dagen.json` (per stijl/jaar/mmdd, met
`daglabel` / `modus` / optioneel `rijadovoe`); UI op vandaag/`/datum/` en
overzichtspagina `/lezingenrooster/`.

## Observances (kleuren)

```yaml
observances: [feest, vasten]   # optioneel; default volgt soort
```

Het jaarrooster ondersteunt gecombineerde kleuren (feest+vasten, heilige+vasten).

## Heiligen: selectie en betekenis

Selectiecriteria (wie in de lijst hoort) staan op `/uitleg/heiligen/`;
veldsemantiek hier. How-to: `/beheer/how-to-heiligen-feesten/`.

```yaml
betekenis_lagenlanden: |
  Apart stuk: wat deze heilige voor het christendom of de Orthodoxie
  in de Lage Landen betekende.
selectie: voldoet            # of: nader-onderzoek | kandidaat-schrappen
selectie_toelichting: "…"    # optioneel; niet op de publieke pagina
id_aliassen: [lubuinus]      # oude ids na een merge
```

- **`betekenis_lagenlanden`** — verplicht bij `status: curated` voor
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

Werklijst (scores, gaten, post-schisma): [`docs/inventaris.md`](inventaris.md).

## Referenties

Verhaal, samenvatting of `betekenis_lagenlanden` mag alleen als er minstens
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

## Status

- `stub` — basisgegevens, kort of geen nagekeken betekenis-stuk
- `curated` — nagekeken tekst met traceerbare bronnen

Voor **heiligen** geldt `curated` alleen als:

1. `betekenis_lagenlanden` aanwezig en niet leeg is, en
2. er minstens één referentie is die **niet** alleen Wikipedia of
   heiligen.net is (die twee mogen aanvullen).

Feesten en vasten: `curated` blijft «nagekeken tekst met traceerbare
bronnen» (bestaande referentieverplichting bij verhaal/samenvatting).
