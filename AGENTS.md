# AGENTS.md — kalender

Orthodoxe heiligen- en feestkalender (statische Hugo-site) voor
[orthodox-ronl](https://github.com/orthodox-ronl).

Org-context: [bron/AGENTS.md](https://github.com/orthodox-ronl/bron/blob/main/AGENTS.md).
Terminologie: [bron/docs/specs/terminologie.md](https://github.com/orthodox-ronl/bron/blob/main/docs/specs/terminologie.md).

## Commando's

```cmd
cd /d C:\Git\orthodox-ronl\kalender
python -m pip install -r requirements.txt
python -m pytest -q
python scripts\validate.py
scripts\build.cmd
```

Preview lokaal: `scripts\serve.cmd`.

## Architectuur

- Brondata: `data/` (YAML)
- Validatie/generatie: `scripts/`
- Site: `site/` (Hugo)
- Uitleg: `site/content/uitleg/` (gebruikers) + `*-technisch.md` (niet in het overzicht)
- Beheerders: `site/content/beheer/`
- CI: `.github/workflows/pages.yml` (main → prod, andere branch → `/preview/`)
