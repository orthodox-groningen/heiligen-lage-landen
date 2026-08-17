"""Generatie van heiligenpagina’s, entries.json en beheer-selectie."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate import (  # noqa: E402
    CONTENT,
    _split_hugo_markdown,
    render_beheer_selectie,
    write_beheer_selectie,
    write_entries_json,
    write_entry_page,
)
from load_entries import load_entries  # noqa: E402


def _heilige(**overrides):
    entry = {
        "id": "voorbeeld",
        "soort": "heilige",
        "status": "stub",
        "cyclus": "jaar",
        "lagenlanden": True,
        "source_path": "data/heiligen/voorbeeld.yaml",
        "namen": {"primair": "Voorbeeld", "alternatief": ["Altnaam"]},
        "datum_norm": {
            "feestdatum": "11-07",
            "vorm": "dag",
            "stijl": "gregoriaans",
        },
        "titels": [],
        "referenties": [],
        "id_aliassen": [],
        "betekenis_lagenlanden": "",
        "selectie": "nader-onderzoek",
        "selectie_toelichting": "",
        "observances": ["heilige"],
        "onderdrukt_wekelijks_vasten": False,
    }
    entry.update(overrides)
    return entry


def test_entry_page_heeft_betekenis_en_aliases(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            betekenis_lagenlanden="Predikte onder de Friezen.",
            id_aliassen=["oud-id"],
            selectie="voldoet",
            selectie_toelichting="niet op de publieke pagina",
        )
    )
    text = (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    meta, body = _split_hugo_markdown(text)
    assert meta["aliases"] == ["/heiligen/oud-id/"]
    assert "selectie" not in meta
    assert "niet op de publieke pagina" not in body
    assert "## Betekenis voor de Lage Landen" in body
    assert "Predikte onder de Friezen." in body


def test_entries_json_heeft_betekenis_alleen_bij_heiligen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    static = tmp_path / "static" / "data"
    monkeypatch.setattr("generate.STATIC_DATA", static)
    heilige = _heilige(betekenis_lagenlanden="Voor de Lage Landen.")
    feest = {
        **_heilige(id="kerst", soort="feest"),
        "namen": {"primair": "Kerst", "alternatief": []},
        "source_path": "data/feesten/kerst.yaml",
        "observances": ["feest"],
        "betekenis_lagenlanden": "",
    }
    write_entries_json([heilige, feest])
    payload = json.loads((static / "entries.json").read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in payload}
    assert by_id["voorbeeld"]["betekenis_lagenlanden"] == "Voor de Lage Landen."
    assert "betekenis_lagenlanden" not in by_id["kerst"]
    assert "selectie" not in by_id["voorbeeld"]


def test_beheer_selectie_groepeert_en_toont_toelichting() -> None:
    body = render_beheer_selectie(
        [
            _heilige(
                id="willibrord",
                namen={"primair": "Willibrord", "alternatief": []},
                selectie="voldoet",
                source_path="data/heiligen/willibrord.yaml",
            ),
            _heilige(
                id="fridolin",
                namen={"primair": "Fridolin", "alternatief": []},
                selectie="kandidaat-schrappen",
                selectie_toelichting="Vooral Boven-Rijn.",
                source_path="data/heiligen/fridolin.yaml",
            ),
            _heilige(
                id="bavo",
                namen={"primair": "Bavo", "alternatief": []},
                source_path="data/heiligen/bavo.yaml",
            ),
        ]
    )
    assert "## Voldoet (1)" in body
    assert "[Willibrord](/heiligen/willibrord/)" in body
    assert "## Nader onderzoek (1)" in body
    assert "[Bavo](/heiligen/bavo/)" in body
    assert "## Kandidaat om te schrappen (1)" in body
    assert "Vooral Boven-Rijn." in body


def test_write_beheer_selectie_naar_beheer_map(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_beheer_selectie(load_entries())
    path = content / "beheer" / "selectie.md"
    meta, body = _split_hugo_markdown(path.read_text(encoding="utf-8"))
    assert meta["title"] == "Selectie heiligen"
    assert meta["generator"] == "scripts/generate.py"
    assert "Willibrord" in body
    assert "Nader onderzoek" in body


def test_heiligen_list_layout_zoekt_alternatieve_namen() -> None:
    layout = (ROOT / "site" / "layouts" / "heiligen" / "list.html").read_text(
        encoding="utf-8"
    )
    assert "heiligen-zoek" in layout
    assert "alternatief" in layout
    assert "entry-filter.js" in layout
    js = (ROOT / "site" / "assets" / "js" / "entry-filter.js").read_text(
        encoding="utf-8"
    )
    assert "data-zoek" in js
    assert "toLocaleLowerCase" in js
