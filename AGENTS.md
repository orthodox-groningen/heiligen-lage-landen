# AGENTS.md — heiligen-lage-landen

Orthodoxe heiligen- en feestkalender (statische Hugo-site) voor
[orthodox-groningen](https://github.com/orthodox-groningen).

Org-context: [bron/AGENTS.md](https://github.com/orthodox-groningen/bron/blob/main/AGENTS.md).
Terminologie: [bron/docs/specs/terminologie.md](https://github.com/orthodox-groningen/bron/blob/main/docs/specs/terminologie.md).

## Commando's

```cmd
cd /d C:\Git\orthodox-groningen\heiligen-lage-landen
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
- CI: `.github/workflows/pages.yml` (main → prod, andere branch → `/preview/`)
