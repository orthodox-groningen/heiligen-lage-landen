# Datamodel

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
`⌊Y/100⌋ − ⌊Y/400⌋ − 2`). Die offset wordt gebruikt om **vandaag** om te
rekenen, en voor **ICS-feeds “oud”** (vierdatum in westerse agenda’s).

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
# of hybride: van_offset_dagen + datum.tot (MM-DD), bv. Apostolisch vasten
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
vóór de Grote Week). Feestdagen die binnen een periode versoepelen (vis, olie)
zijn typikon en nog niet gemodelleerd.

## Observances (kleuren)

```yaml
observances: [feest, vasten]   # optioneel; default volgt soort
```

Het jaarrooster kleurt nu één dominante categorie. **TODO:** meerdere kleuren
tegelijk tonen wanneer een dag feest én vasten is (bijv. Onthoofding van Johannes).

## Referenties

Verhaal of samenvatting mag alleen als er minstens één referentie is.
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

- `stub` — basisgegevens, kort of geen verhaal
- `curated` — nagekeken tekst met traceerbare bronnen
