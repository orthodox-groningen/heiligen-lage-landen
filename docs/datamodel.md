# Datamodel

Elke entry is één YAML-bestand in `data/feesten/` of `data/heiligen/`.

## Datum en stijl

```yaml
datum:
  waarde: "08-15"          # MM-DD = feestdatum
  # stijl weglaten = gregoriaans (default) — alleen documentatie van de invoer
  stijl: juliaans          # of: gregoriaans
```

De **feestdatum** is de kalenderdag van het feest (bijv. Ontslapen = 15 augustus).
Die dagnaam is gelijk in de nieuwe (Gregoriaanse) en oude (Juliaanse) kalender.
`stijl` legt alleen vast hoe de beheerder de waarde bedoelde; er wordt géén
+13-dagenverschuiving op de feestdatum toegepast.

De offset van 13 dagen (tot 2100) wordt wél gebruikt om **vandaag** om te
rekenen: burgerlijk 15 augustus = Juliaans 2 augustus.

## Referenties

Verhaal of samenvatting mag alleen als er minstens één referentie is:

```yaml
referenties:
  - bron_id: hnet
    geraadpleegd: "2026-08-15"
  - label: "Eigen notitie"
    url: "https://…"
    geraadpleegd: "2026-08-15"
```

`bron_id` verwijst naar `data/bronnen/bronnen.yaml`.

## Status

- `stub` — basisgegevens, kort of geen verhaal
- `curated` — nagekeken tekst met traceerbare bronnen

## Iconen

Alleen publiceren met `icoon.rechten: ok` plus bron en licentie; bestand onder `site/static/`.
