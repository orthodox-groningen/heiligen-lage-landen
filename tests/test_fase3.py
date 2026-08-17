"""Fase 3: toon in de titel, lijsticonen, geen iconen in de jaarkalender-popover."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "site" / "assets" / "js" / "calendar.js"
HEILIGEN_LIST = ROOT / "site" / "layouts" / "heiligen" / "list.html"


def test_titel_toont_toon() -> None:
    js = JS.read_text(encoding="utf-8")
    assert "function octoechosToon" in js
    assert "(Toon ${p.toon})" in js
    assert 'achtergrondLink("toon"' in js


def test_lijsticonen_in_meneon_en_heiligenoverzicht() -> None:
    js = JS.read_text(encoding="utf-8")
    assert "class=\"list-icoon\"" in js or "class='list-icoon'" in js
    html = HEILIGEN_LIST.read_text(encoding="utf-8")
    assert "list-icoon" in html
    assert ".Params.icoon" in html


def test_jaarkalender_popover_zonder_iconen() -> None:
    js = JS.read_text(encoding="utf-8")
    start = js.index("function fillKalenderDagPopover")
    rest = js[start + 10 :]
    end = rest.index("\n  function ")
    body = rest[:end]
    assert "icoon" not in body
    assert "list-icoon" not in body


def test_bijbel_deeplink_in_calendar_js() -> None:
    js = JS.read_text(encoding="utf-8")
    assert "www.debijbel.nl/bijbel/" in js
    assert "class=\"bijbel-link\"" in js or "class='bijbel-link'" in js
    assert "bijbel-vertaling" in js
