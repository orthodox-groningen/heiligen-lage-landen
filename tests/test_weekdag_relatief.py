"""Weekdag t.o.v. een vaste feestdatum (zondagen rond Kerst)."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from kalender import weekday_relative_date  # noqa: E402
from load_entries import load_entries  # noqa: E402
from lezingen import resolve_lezingen  # noqa: E402


def test_zondag_voor_kerst_2026_nieuw() -> None:
    # 25 december 2026 is vrijdag.
    assert date(2026, 12, 25).isoweekday() == 5
    vaderen = weekday_relative_date(
        2026, "12-25", 7, 1, "voor", stijl="nieuw"
    )
    voorvaderen = weekday_relative_date(
        2026, "12-25", 7, 2, "voor", stijl="nieuw"
    )
    na_kerst = weekday_relative_date(
        2026, "12-25", 7, 1, "na", stijl="nieuw"
    )
    assert vaderen == date(2026, 12, 20)
    assert voorvaderen == date(2026, 12, 13)
    assert na_kerst == date(2026, 12, 27)
    assert weekday_relative_date(
        2026, "01-06", 7, 1, "na", stijl="nieuw"
    ) == date(2026, 1, 11)


def test_zondag_voor_als_kerst_zelf_zondag_is() -> None:
    assert date(2022, 12, 25).isoweekday() == 7
    assert weekday_relative_date(
        2022, "12-25", 7, 1, "voor", stijl="nieuw"
    ) == date(2022, 12, 18)
    assert weekday_relative_date(
        2022, "12-25", 7, 2, "voor", stijl="nieuw"
    ) == date(2022, 12, 11)
    assert weekday_relative_date(
        2022, "12-25", 7, 1, "na", stijl="nieuw"
    ) == date(2023, 1, 1)


def test_entries_weekdag_relatief() -> None:
    by_id = {e["id"]: e for e in load_entries()}
    vv = by_id["zondag-voorvaderen"]["datum_norm"]
    assert vv["vorm"] == "weekdag_relatief"
    assert vv["anker"] == "12-25"
    assert vv["welke"] == 2
    assert vv["richting"] == "voor"
    vad = by_id["zondag-vaderen-voor-kerst"]["datum_norm"]
    assert vad["welke"] == 1
    assert by_id["zondag-na-theofanie"]["datum_norm"]["anker"] == "01-06"


def test_lezingen_zondagen_voor_kerst_2026() -> None:
    vad = resolve_lezingen(2026, "12-20", "nieuw")
    assert vad.override_id == "zondag-vaderen-voor-kerst"
    assert [a.ref for a in vad.apostel] == ["Heb. 11:9-10, 17-23, 32-40"]
    vv = resolve_lezingen(2026, "12-13", "nieuw")
    assert vv.override_id == "zondag-voorvaderen"
    assert [a.ref for a in vv.apostel] == ["Kol. 3:4-11"]
    na = resolve_lezingen(2026, "12-27", "nieuw")
    assert na.override_id == "zondag-na-kerst"
    theo = resolve_lezingen(2026, "01-11", "nieuw")
    assert theo.override_id == "zondag-na-theofanie"
    # 1 jan. 2023 is zondag ná Kerst 2022 én Besnijdenis; het grootfeest wint.
    jan1 = resolve_lezingen(2023, "01-01", "nieuw")
    assert jan1.override_id == "besnijdenis-des-heren"
