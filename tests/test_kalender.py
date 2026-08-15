import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from kalender import (
    civil_to_julian_mmdd,
    julian_to_civil_mmdd,
    normalize_dates,
)


def test_feestdatum_same_in_both_styles():
    """Ontslapen is 15 augustus in beide kalenders — geen +13 op de feestdatum."""
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
