"""Fase 1: navigatie, uitleg, bronlaag, issue-templates."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate import CONTENT  # noqa: E402

SITE = ROOT / "site"
SCHEMA = ROOT / "schemas" / "entry.schema.json"
ISSUES = ROOT / ".github" / "ISSUE_TEMPLATE"


def test_nav_heeft_heiligen_en_uitleg() -> None:
    html = (SITE / "layouts" / "_default" / "baseof.html").read_text(encoding="utf-8")
    assert 'href="{{ "heiligen/" | relURL }}">Heiligen</a>' in html
    assert ">Uitleg</a>" in html
    assert ">Help</a>" not in html


def test_homepage_verwijst_naar_uitleg_heiligen() -> None:
    text = (CONTENT / "_index.md").read_text(encoding="utf-8")
    assert "Wat er wel en niet in staat" in text
    assert "/uitleg/heiligen" in text


def test_footer_heeft_reactie() -> None:
    html = (SITE / "layouts" / "partials" / "footer.html").read_text(encoding="utf-8")
    assert "uitleg/reactie/" in html


def test_schema_bronlaag_geen_stub() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    enum = schema["properties"]["bronlaag"]["enum"]
    assert set(enum) == {"nagekeken", "encyclopedie"}
    assert "status" not in schema["properties"]


def test_lege_dag_linkt_naar_uitleg_heiligen() -> None:
    js = (SITE / "assets" / "js" / "calendar.js").read_text(encoding="utf-8")
    assert "Waarom niet iedere heilige hier staat" in js
    assert "today-geen-heilige" in js
    assert 'achtergrondLink(' in js
    assert '"heiligen"' in js


def test_issue_templates_bestaan() -> None:
    names = {p.name for p in ISSUES.glob("*.yml")}
    assert "config.yml" in names
    assert "heilige-voorstellen.yml" in names
    assert "correctie.yml" in names
    assert "vraag.yml" in names
    vraag = (ISSUES / "vraag.yml").read_text(encoding="utf-8")
    assert "Uw vraag of opmerking" in vraag


def test_reactie_pagina_wijst_naar_github() -> None:
    text = (CONTENT / "uitleg" / "reactie.md").read_text(encoding="utf-8")
    assert "issues/new/choose" in text
    assert "Heilige voorstellen" in text


def test_uitleg_heiligen_noemt_parochiepatronen() -> None:
    text = (CONTENT / "uitleg" / "heiligen.md").read_text(encoding="utf-8")
    hoofd = text.split("## Voor wie de site bijhoudt")[0]
    assert "Patroon van een parochie" in text
    assert "Nektarios" in text
    assert "bronlaag" not in hoofd
    assert "kaart" in hoofd
    assert "data/" not in hoofd
