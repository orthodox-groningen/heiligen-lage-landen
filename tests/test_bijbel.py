"""Perikoop-verwijzing → OSIS-hoofdstuk voor debijbel.nl."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from bijbel import BOEK_OSIS, debijbel_url, osis_hoofdstuk  # noqa: E402


def test_bekende_verwijzingen() -> None:
    assert osis_hoofdstuk("Rom. 13:11-14:4") == "ROM.13"
    assert osis_hoofdstuk("Gal. 3:8-12") == "GAL.3"
    assert osis_hoofdstuk("1 Kor. 4:9-16") == "1CO.4"
    assert osis_hoofdstuk("1 Joh. 1:1-7") == "1JN.1"
    assert osis_hoofdstuk("Matt. 4:25; 5:1-13") == "MAT.4"
    assert osis_hoofdstuk("Joh. 1:1-17") == "JHN.1"


def test_meerdere_boeken_in_een_ref() -> None:
    from bijbel import ref_delen

    delen = ref_delen(
        "Matt. 26:2-20; Joh. 13:3-17; Matt. 26:21-39"
    )
    assert delen == ["Matt. 26:2-20", "Joh. 13:3-17", "Matt. 26:21-39"]
    assert ref_delen("Matt. 4:25; 5:1-13") == ["Matt. 4:25; 5:1-13"]


def test_onbekend_of_leeg() -> None:
    assert osis_hoofdstuk("") is None
    assert osis_hoofdstuk("Onbekend 1:1") is None


def test_debijbel_url_standaard_hsv() -> None:
    assert (
        debijbel_url("Luc. 9:57-62")
        == "https://www.debijbel.nl/bijbel/HSV/LUK.9"
    )
    assert (
        debijbel_url("Hand. 1:1-8", "BGT")
        == "https://www.debijbel.nl/bijbel/BGT/ACT.1"
    )


def _alle_refs(obj) -> list[str]:
    found: list[str] = []
    if isinstance(obj, dict):
        ref = obj.get("ref")
        if isinstance(ref, str) and ref.strip():
            found.append(ref.strip())
        for value in obj.values():
            found.extend(_alle_refs(value))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(_alle_refs(item))
    return found


def test_weekreeks_refs_krijgen_osis() -> None:
    missing: list[str] = []
    for name in ("weekreeks.yaml", "feest-overrides.yaml"):
        path = ROOT / "data" / "lezingen" / name
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for ref in _alle_refs(data):
            if osis_hoofdstuk(ref) is None:
                missing.append(f"{name}: {ref}")
    assert not missing, missing[:8]


def test_calendar_js_spiegel_boekcodes() -> None:
    js = (ROOT / "site" / "assets" / "js" / "calendar.js").read_text(
        encoding="utf-8"
    )
    for boek, osis in BOEK_OSIS.items():
        assert f'"{boek}": "{osis}"' in js, boek


def test_calendar_js_spiegel_vertalingen() -> None:
    from bijbel import STANDAARD_VERTALING, VERTALINGEN

    js = (ROOT / "site" / "assets" / "js" / "calendar.js").read_text(
        encoding="utf-8"
    )
    assert STANDAARD_VERTALING == "HSV"
    assert VERTALINGEN[0] == "HSV"
    for code in VERTALINGEN:
        assert f'"{code}"' in js, code
    assert 'return "HSV"' in js
    assert "NFB (Fries)" in js
    assert "UTT (Oekraïens)" in js
