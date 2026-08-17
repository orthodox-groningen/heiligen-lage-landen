"""Kerninhoud (stap 5): nieuwe heiligen en curated-lat."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from load_entries import load_entries  # noqa: E402
from validate import referentie_is_aanvullend  # noqa: E402

NIEUW = {
    "servatius",
    "otger",
    "odulphus",
    "begga",
    "monulphus",
    "gondulphus",
    "rumold",
    "johannes-van-shanghai",
    "sophrony-van-essex",
}

CURATED_KERN = NIEUW | {
    "willibrord",
    "bonifatius",
    "lambertus",
    "lebuinus",
    "adelbert",
    "gertrudis",
    "dymphna",
}


def test_nieuwe_heiligen_bestaan_met_betekenis() -> None:
    by_id = {e["id"]: e for e in load_entries() if e["soort"] == "heilige"}
    for sid in NIEUW:
        entry = by_id[sid]
        assert entry["selectie"] == "voldoet"
        assert (entry.get("betekenis_lage_landen") or "").strip()
        assert entry["referenties"]


def test_curated_kern_heeft_niet_alleen_wikipedia() -> None:
    by_id = {e["id"]: e for e in load_entries() if e["soort"] == "heilige"}
    for sid in CURATED_KERN:
        entry = by_id[sid]
        assert entry["status"] == "curated", sid
        assert (entry.get("betekenis_lage_landen") or "").strip(), sid
        assert any(not referentie_is_aanvullend(r) for r in entry["referenties"]), sid
