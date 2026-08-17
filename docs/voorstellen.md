# Voorstellen (nog niet bouwen)

Korte vastlegging bij het vervolgplan. Geen YAML-velden tot er een
uitdrukkelijk besluit is om te implementeren.

## Betekenis van feesten

Huidige feestpagina’s zijn kalenderfeit (wat/wanneer). Voor wie niet van
huis uit orthodox is, ontbreekt vaak: wat dit feest zegt over de weg naar
God.

Drie lagen, niet door elkaar:

1. **Gebeurtenis** — bestaande `verhaal` (kort, bron)
2. **Plaats in het jaar** — de kalender doet dit al
3. **Betekenis** — nieuw veld `betekenis` (1–3 alinea’s; orthodox, weinig
   jargon; geen preek). Zelfde `bronlaag` als de rest van de pagina.

Eerst alleen de twaalf grootfeesten; één voorbeeld uitschrijven (Theofanie
of Transfiguratie) voordat de rest volgt.

## Parochiepatronen (categorie D / C)

Patroon van een kerk is nu geen toelatingsgrond (zie
[uitleg heiligen](../site/content/uitleg/heiligen.md) en de C-lijst in
[inventaris.md](inventaris.md)).

Later denkbaar, **onderaan** de heiligen van een datum (na de
Lage-Landen-heiligen):

```yaml
categorie: parochiepatroon
parochies:
  - naam: "…"
    plaats: eindhoven
    url: "https://…"
```

Pas als er een onderhouden lijst van parochiesites is. Geen vermenging
met `selectie: voldoet`.
