"""Contracttests: docs/specs/lezingen.md voorbeelden ↔ scripts/lezingen.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from kalender import orthodox_pascha, mmdd_from_date  # noqa: E402
from lezingen import (  # noqa: E402
    SPEC_PATH,
    parse_spec_voorbeelden,
    resolve_lezingen,
    resultaat_matches_verwacht,
    spec_body_for_uitleg,
)


def test_spec_exists() -> None:
    assert SPEC_PATH.is_file()
    assert "R2" in SPEC_PATH.read_text(encoding="utf-8")


def test_parse_voorbeelden_nonempty() -> None:
    voorbeelden = parse_spec_voorbeelden()
    assert len(voorbeelden) >= 3
    statuses = {v["status"] for v in voorbeelden}
    assert "implemented" in statuses
    assert "pending" in statuses


def test_pascha_2025_mmdd_matches_computus() -> None:
    assert mmdd_from_date(orthodox_pascha(2025)) == "04-20"


@pytest.mark.parametrize(
    "voorbeeld",
    [v for v in parse_spec_voorbeelden() if v.get("status") == "implemented"],
    ids=lambda v: v["id"],
)
def test_implemented_voorbeelden(voorbeeld: dict) -> None:
    result = resolve_lezingen(
        int(voorbeeld["jaar"]),
        str(voorbeeld["mmdd"]),
        str(voorbeeld.get("stijl") or "nieuw"),
    )
    assert result.status == "gevonden", voorbeeld["id"]
    errors = resultaat_matches_verwacht(result, voorbeeld["verwacht"])
    assert not errors, f"{voorbeeld['id']}: " + "; ".join(errors)


def test_pending_voorbeelden_are_skipped_by_filter() -> None:
    pending = [v for v in parse_spec_voorbeelden() if v["status"] == "pending"]
    assert pending
    # Ze mogen nog "onbekend" zijn — geen harde assert op inhoud.


def test_weekreeks_fills_ordinary_weekday() -> None:
    r = resolve_lezingen(2025, "07-02", "nieuw")
    assert r.status == "gevonden"
    assert "R3" in r.regels
    assert r.apostel and r.evangelie


def test_lucaanse_sprong_switches_gospel() -> None:
    from lezingen import lucaanse_sprong_maandag

    assert lucaanse_sprong_maandag(2025).isoformat() == "2025-09-22"
    r = resolve_lezingen(2025, "09-22", "nieuw")
    assert r.status == "gevonden"
    assert "R3-lucaans" in r.regels
    assert r.evangelie and r.evangelie[0].ref.startswith("Luc.")


def test_spec_body_for_uitleg_strips_examples() -> None:
    body = spec_body_for_uitleg()
    assert "```lezingen-voorbeeld" not in body
    assert "### R2" in body or "## Regels" in body
