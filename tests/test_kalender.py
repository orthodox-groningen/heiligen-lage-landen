import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from kalender import normalize_dates


def test_julian_christmas_to_gregorian():
    d = normalize_dates("12-25", "juliaans")
    assert d["juliaans"] == "12-25"
    assert d["gregoriaans"] == "01-07"


def test_gregorian_default():
    d = normalize_dates("11-07")
    assert d["stijl"] == "gregoriaans"
    assert d["gregoriaans"] == "11-07"
    assert d["juliaans"] == "10-25"


def test_roundtrip_offset():
    d = normalize_dates("06-12", "gregoriaans")
    back = normalize_dates(d["juliaans"], "juliaans")
    assert back["gregoriaans"] == "06-12"
