"""Datahygiëne: merges en titels (stap 3)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from load_entries import load_entries  # noqa: E402
from validate import collect_content_errors  # noqa: E402

HEILIGEN = ROOT / "data" / "heiligen"


def test_dubbele_ids_zijn_samengevoegd() -> None:
    assert not (HEILIGEN / "lubuinus.yaml").exists()
    assert not (HEILIGEN / "alberik.yaml").exists()
    by_id = {e["id"]: e for e in load_entries() if e["soort"] == "heilige"}
    assert "lubuinus" not in by_id
    assert "alberik" not in by_id
    assert by_id["lebuinus"]["id_aliassen"] == ["lubuinus"]
    assert by_id["albericus-van-utrecht"]["id_aliassen"] == ["alberik"]
    alts_leb = by_id["lebuinus"]["namen"]["alternatief"]
    assert "Lubuinus" in alts_leb
    alts_alb = by_id["albericus-van-utrecht"]["namen"]["alternatief"]
    assert "Alberik" in alts_alb


def test_namen_staan_in_entry_niet_in_catalogusbestand() -> None:
    assert not (ROOT / "data" / "namen.yaml").exists()
    by_id = {e["id"]: e for e in load_entries()}
    assert "Lubuinus" in by_id["lebuinus"]["namen"]["alternatief"]
    assert "Alberik" in by_id["albericus-van-utrecht"]["namen"]["alternatief"]
    assert "Vleesvaarwel" in by_id["zondag-laatste-oordeel"]["namen"]["alternatief"]
    assert "Zuivelvaarwel" in by_id["vergevingszondag"]["namen"]["alternatief"]


def test_titels_zonder_engels_en_zonder_icoon_in_parochie() -> None:
    verboden = (
        "icoon in parochie",
        "virgin",
        "virgin martyr",
    )
    for path in HEILIGEN.glob("*.yaml"):
        text = path.read_text(encoding="utf-8").lower()
        for stuk in verboden:
            assert stuk not in text, f"{path.name}: {stuk!r}"
    temse = (HEILIGEN / "amalberga-van-temse.yaml").read_text(encoding="utf-8")
    assert "Monnik" not in temse
    assert "Maagd" in temse


def test_catalogus_valideert_na_hygiene() -> None:
    assert collect_content_errors(load_entries()) == []


def test_weekreeks_refs_zonder_bronnotities() -> None:
    import re

    import yaml

    raw = yaml.safe_load(
        (ROOT / "data" / "lezingen" / "weekreeks.yaml").read_text(encoding="utf-8")
    )
    dirty = []
    for row in raw["dagen"]:
        for key in ("apostel", "evangelie"):
            for item in row.get(key) or []:
                ref = str(item.get("ref") or "")
                if re.search(r"[А-Яа-яЁё/{}]", ref):
                    dirty.append(ref)
    assert dirty == []
