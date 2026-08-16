import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from kalender import (
    civil_to_julian_mmdd,
    julian_feast_to_civil_date,
    julian_to_civil_mmdd,
    normalize_dates,
)


def test_feestdatum_same_in_both_styles():
    d = normalize_dates("08-15", "juliaans")
    assert d["feestdatum"] == "08-15"
    assert d["stijl"] == "juliaans"


def test_gregorian_default_feestdatum():
    d = normalize_dates("11-07")
    assert d["stijl"] == "gregoriaans"
    assert d["feestdatum"] == "11-07"


def test_today_conversion_aug15_civil_is_aug2_julian():
    assert civil_to_julian_mmdd("08-15") == "08-02"
    assert julian_to_civil_mmdd("08-02") == "08-15"


def test_transfiguratie_oud_ics_civil_date():
    """6 augustus Juliaans → 19 augustus burgerlijk in westerse agenda."""
    assert julian_to_civil_mmdd("08-06") == "08-19"


def test_besnijdenis_oud_civil_is_14_january():
    """1 januari Juliaans → 14 januari wereldlijk (offset 13, niet 13 januari)."""
    assert julian_feast_to_civil_date(2026, "01-01") == date(2026, 1, 14)


def test_kerst_oud_civil_crosses_year():
    assert julian_feast_to_civil_date(2026, "12-25") == date(2027, 1, 7)
    assert julian_feast_to_civil_date(2025, "12-25") == date(2026, 1, 7)
