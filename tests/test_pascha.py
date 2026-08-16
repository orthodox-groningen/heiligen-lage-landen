"""Tests voor offset 13/14 en Orthodox Pascha."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from kalender import (  # noqa: E402
    julian_calendar_to_gregorian,
    julian_gregorian_offset_days,
    julian_to_civil_mmdd,
    mmdd_from_date,
    orthodox_pascha,
    orthodox_pascha_julian,
)


KNOWN_GREGORIAN = {
    2019: "04-28",
    2020: "04-19",
    2021: "05-02",
    2022: "04-24",
    2023: "04-16",
    2024: "05-05",
    2025: "04-20",
    2026: "04-12",
}


def test_offset_before_and_after_2100():
    assert julian_gregorian_offset_days(2099) == 13
    assert julian_gregorian_offset_days(2100) == 14
    assert julian_gregorian_offset_days(2001) == 13


def test_known_orthodox_pascha_dates():
    for year, expect in KNOWN_GREGORIAN.items():
        assert mmdd_from_date(orthodox_pascha(year)) == expect


def test_pascha_1995_through_2022_table():
    """Controletabel 1995–2022 (Meeus/Alexandrijns → Gregoriaans)."""
    table = {y: mmdd_from_date(orthodox_pascha(y)) for y in range(1995, 2023)}
    assert table[1995] == "04-23"
    assert table[2001] == "04-15"
    assert table[2010] == "04-04"
    assert table[2014] == "04-20"
    assert table[2017] == "04-16"
    assert table[2019] == "04-28"
    assert table[2020] == "04-19"
    assert table[2021] == "05-02"
    assert table[2022] == "04-24"
    assert len(table) == 28


def test_julian_component_converts_to_same_gregorian():
    for year in (1995, 2010, 2024, 2099, 2100, 2101):
        j_m, j_d = orthodox_pascha_julian(year)
        assert julian_calendar_to_gregorian(year, j_m, j_d) == orthodox_pascha(year)


def test_civil_aug_roundtrip_unchanged():
    assert julian_to_civil_mmdd("08-02") == "08-15"


def test_pascha_not_shifted_by_julian_offset():
    """Pascha 2026 is 12 april wereldlijk; +13 zou 25 april zijn."""
    assert orthodox_pascha(2026) == date(2026, 4, 12)
