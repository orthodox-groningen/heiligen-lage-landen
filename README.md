# Heiligen van de Lage Landen

Statische site met orthodoxe **vaste feesten** (jaarcyclus) en **heiligen van de Lage Landen**.
MVP: nog géén paascyclus.

- Productie: https://orthodox-groningen.github.io/heiligen-lage-landen/
- Preview (niet-`main`): https://orthodox-groningen.github.io/heiligen-lage-landen/preview/

## Wat zit erin

| Onderdeel | Inhoud |
| --------- | ------ |
| Data      | YAML onder `data/` (feesten, heiligen, bronnen) |
| Build     | `scripts/validate.py`, `scripts/generate.py` → Hugo-content + ICS |
| Site      | Hugo in `site/` |
| Agenda    | ICS-feeds `/ics/*-{nieuw,oud}.ics` (oud = burgerlijk +13) |

Datums: default **Gregoriaans** invoer; optioneel `datum.stijl`. Feestdatum =
dagnaam (gelijk in nieuw/oud). Zie [docs/datamodel.md](docs/datamodel.md) en
de pagina **Uitleg** op de site.

## Lokaal bouwen

```cmd
cd /d C:\Git\orthodox-groningen\heiligen-lage-landen
python -m pip install -r requirements.txt
python scripts\validate.py
python scripts\generate.py --clean
python scripts\write_build_stamp.py
hugo --source site --destination generated\site --minify
hugo --source site --destination generated\site --minify --baseURL / --buildDrafts=false
```

Of met serve (na generate):

```cmd
cd /d C:\Git\orthodox-groningen\heiligen-lage-landen
scripts\serve.cmd
```

## GitHub Pages

Push naar `main` → productie. Push naar een andere branch → preview onder `/preview/`.
In repo-settings: **Pages → Deploy from a branch → `gh-pages` → `/`**.

## Licentie

Code/scripts: Apache 2.0. Inhoud (YAML/teksten): zie bronvermeldingen per entry; respecteer rechten van externe bronnen en iconen.
