"""Inventaris (stap 4): elke heilige heeft een expliciete selectie."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from load_entries import load_entries  # noqa: E402

HEILIGEN = ROOT / "data" / "heiligen"

KANDIDAAT = {
    "adela-van-vlaanderen",
    "egbert-van-rathmelsigi",
    "fridolin",
    "walburga",
    "winnibald",
}
NADER = {
    "adelgonda",
    "agricolaus-van-maastricht",
    "aubertus-van-kamerijk",
    "folciunus",
    "medardus",
    "quirillus-van-tongern",
    "winnocus",
}


def test_elke_heilige_heeft_selectie_in_yaml() -> None:
    paths = sorted(HEILIGEN.glob("*.yaml"))
    assert len(paths) == 62
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "\nselectie: " in text, path.name


def test_selectie_groepen_kloppen() -> None:
    by_id = {e["id"]: e for e in load_entries() if e["soort"] == "heilige"}
    assert len(by_id) == 62
    kandidaat = {i for i, e in by_id.items() if e["selectie"] == "kandidaat-schrappen"}
    nader = {i for i, e in by_id.items() if e["selectie"] == "nader-onderzoek"}
    voldoet = {i for i, e in by_id.items() if e["selectie"] == "voldoet"}
    assert kandidaat == KANDIDAAT
    assert nader == NADER
    assert len(voldoet) == 50
    assert "willibrord" in voldoet
    assert by_id["willibrord"]["selectie_toelichting"]
    assert "Ierland" in by_id["egbert-van-rathmelsigi"]["selectie_toelichting"]
