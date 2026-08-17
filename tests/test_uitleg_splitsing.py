"""Gebruikersuitleg versus technische bijlage; beheerdershome."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate import ACHTERGROND_TOPICS, CONTENT, _split_hugo_markdown  # noqa: E402

UITLEG = CONTENT / "uitleg"
BEHEER = CONTENT / "beheer"

# Onderwerpen met een handmatige gebruikerspagina + technische bijlage.
# Vasten is gegenereerd; de splitsing daarvan staat in tests/test_vasten.py.
HANDMATIGE_ONDERWERPEN = (
    "nieuw-oud",
    "feestdatum",
    "datumpagina",
    "meneon",
    "heiligen",
    "kleuren",
    "agenda",
    "toon",
)

TECHNISCHE_SPOREN = (
    "data/",
    "scripts/",
    ".yaml",
    ".py",
    "calendar.js",
    "?jaar=",
    "?dag=",
    "MM-DD",
    "+13",
    "wo/vr",
    "→",
)

HOW_TOS = (
    "how-to-publiceren",
    "how-to-heiligen-feesten",
    "how-to-namen",
    "how-to-vasten",
    "how-to-lezingen",
)


def _meta_body(path: Path) -> tuple[dict, str]:
    return _split_hugo_markdown(path.read_text(encoding="utf-8"))


def test_elk_handmatig_onderwerp_heeft_technische_bijlage() -> None:
    for topic in HANDMATIGE_ONDERWERPEN:
        user = UITLEG / f"{topic}.md"
        tech = UITLEG / f"{topic}-technisch.md"
        assert user.is_file(), user
        assert tech.is_file(), tech
        umeta, ubody = _meta_body(user)
        tmeta, tbody = _meta_body(tech)
        assert umeta.get("build", {}).get("list") != "never"
        assert tmeta.get("build", {}).get("list") == "never"
        assert tmeta.get("build", {}).get("render") == "always"
        assert tmeta.get("uitleg_stijl") == f"{topic}-technisch"
        assert f"/uitleg/{topic}-technisch" in ubody
        assert f"/uitleg/{topic}" in tbody


def test_gebruikerspaginas_zonder_technische_sporen() -> None:
    for topic in HANDMATIGE_ONDERWERPEN:
        _meta, body = _meta_body(UITLEG / f"{topic}.md")
        hoofd, voet = body, ""
        if "## Voor wie de site bijhoudt" in body:
            hoofd, voet = body.split("## Voor wie de site bijhoudt", 1)
        for spoor in TECHNISCHE_SPOREN:
            assert spoor not in hoofd, f"{topic}: {spoor!r} in gebruikersdeel"
        assert "technische pagina" in voet


def test_technische_bijlagen_niet_in_uitleg_overzicht_front_matter() -> None:
    for path in UITLEG.glob("*-technisch.md"):
        meta, _body = _meta_body(path)
        assert meta.get("build", {}).get("list") == "never", path.name


def test_beheer_home_onderscheidt_aanraken_en_overschrijven() -> None:
    meta, body = _meta_body(BEHEER / "_index.md")
    assert meta["title"] == "Voor beheerders"
    assert "data/heiligen/" in body
    assert "data/regels/vasten.yaml" in body
    assert "site/content/heiligen/*.md" in body
    assert "site/content/uitleg/vasten.md" in body
    assert "entries.json" in body
    assert "plaatsen.yaml" in body
    assert "plaatsen.json" in body
    assert "beheer-tabel-aanraken" in body
    assert "beheer-tabel-afblijven" in body
    for slug in HOW_TOS:
        assert f"/beheer/{slug}" in body
    assert "/beheer/selectie" in body
    assert "site/content/beheer/selectie.md" in body


def test_how_tos_bestaan() -> None:
    for slug in HOW_TOS:
        path = BEHEER / f"{slug}.md"
        assert path.is_file(), path
        meta, body = _meta_body(path)
        assert isinstance(meta.get("title"), str) and meta["title"].strip()
        assert "python scripts/" in body or "generate.py" in body or "data/" in body


def test_how_to_lezingen_zonder_hugo_ref_naar_ontbrekende_paginas() -> None:
    text = (BEHEER / "how-to-lezingen.md").read_text(encoding="utf-8")
    assert 'ref "/uitleg/lezingen' not in text
    assert "data/lezingen/" in text
    assert "parochies/" in text


def test_uitleg_index_wijst_naar_beheer() -> None:
    _meta, body = _meta_body(UITLEG / "_index.md")
    assert "/beheer" in body
    assert "geen" in body.lower()
    assert "Lage Landen" in body
    assert "typikon" in body.lower()


def test_uitleg_overzicht_groepeert_onderwerpen() -> None:
    layout = (ROOT / "site" / "layouts" / "uitleg" / "list.html").read_text(
        encoding="utf-8"
    )
    assert "Op één dag" in layout
    assert "Heiligen van hier" in layout
    assert "Kalender gebruiken" in layout
    assert "Reageren" in layout
    for slug in (
        "datumpagina",
        "toon",
        "lezingen",
        "vasten",
        "heiligen",
        "nieuw-oud",
        "feestdatum",
        "meneon",
        "kleuren",
        "agenda",
        "reactie",
    ):
        assert f'"{slug}"' in layout


def test_sitenaam_popover_wijst_naar_uitleg() -> None:
    js = (ROOT / "site" / "assets" / "js" / "calendar.js").read_text(
        encoding="utf-8"
    )
    assert 'kind === "site"' in js
    assert "Nederlandersmet" not in js
    assert "Lage Landen" in js
    assert 'assetUrl("uitleg/")' in js


def test_achtergrond_topics_hebben_geen_technische_ids() -> None:
    ids = {t["id"] for t in ACHTERGROND_TOPICS}
    assert "vasten-technisch" not in ids
    for topic in HANDMATIGE_ONDERWERPEN:
        assert topic in ids
        assert f"{topic}-technisch" not in ids


def test_agenda_pagina_heeft_geen_lijst_vaste_feeds() -> None:
    layout = (ROOT / "site" / "layouts" / "_default" / "agenda.html").read_text(
        encoding="utf-8"
    )
    js = (ROOT / "site" / "assets" / "js" / "calendar.js").read_text(encoding="utf-8")
    assert "ics-all-links" not in layout
    assert "Alle vaste feeds" not in layout
    assert 'name="ics-modus"' in layout
    assert "Kopieer de agenda-link" in layout
    assert "Download de kalender" in layout
    assert "ics-all-links" not in js
    assert "heiligen-feesten-nieuw" not in js
