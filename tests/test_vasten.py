"""Vastenperiode vervangt wekelijks wo/vr-vasten."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate import period_bounds_for_year  # noqa: E402
from load_entries import load_entries  # noqa: E402


def _by_id() -> dict[str, dict]:
    return {e["id"]: e for e in load_entries()}


def test_ontslapen_vasten_onderdrukt_wekelijks() -> None:
    e = _by_id()["ontslapen-vasten"]
    assert e["onderdrukt_wekelijks_vasten"] is True


def test_vrijdagvasten_blijft_wekelijks() -> None:
    e = _by_id()["vrijdag-vasten"]
    assert e.get("cyclus") == "wekelijks"
    assert e["onderdrukt_wekelijks_vasten"] is False


def test_ontslapen_periode_dekt_8_augustus() -> None:
    e = _by_id()["ontslapen-vasten"]
    bounds = period_bounds_for_year(e, 2026)
    assert bounds == (date(2026, 8, 1), date(2026, 8, 14))
    assert date(2026, 8, 8) >= bounds[0] and date(2026, 8, 8) <= bounds[1]
