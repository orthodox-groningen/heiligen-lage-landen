# Datamodel

Elke entry is één YAML-bestand in `data/feesten/` of `data/heiligen/`.

## Datum en stijl

```yaml
datum:
  waarde: "12-06"          # MM-DD
  # stijl weglaten = gregoriaans (default)
  stijl: gregoriaans       # of: juliaans
```

De build normaliseert altijd naar beide stijlen (offset 13 dagen tot 2100).

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
