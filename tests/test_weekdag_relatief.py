"""Weekdag t.o.v. een vaste feestdatum (Kerst, Theofanie, Kruisverheffing)."""

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
    z7 = by_id["zondag-vaderen-zevende-concilie"]["datum_norm"]
    assert z7["vorm"] == "weekdag_relatief"
    assert z7["anker"] == "10-10"
    assert z7["richting"] == "na"


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


def test_kruisverheffing_zaterdag_zondag_2026() -> None:
    # 14 september 2026 is maandag.
    assert date(2026, 9, 14).isoweekday() == 1
    za_voor = weekday_relative_date(2026, "09-14", 6, 1, "voor", stijl="nieuw")
    zo_voor = weekday_relative_date(2026, "09-14", 7, 1, "voor", stijl="nieuw")
    za_na = weekday_relative_date(2026, "09-14", 6, 1, "na", stijl="nieuw")
    zo_na = weekday_relative_date(2026, "09-14", 7, 1, "na", stijl="nieuw")
    assert za_voor == date(2026, 9, 12)
    assert zo_voor == date(2026, 9, 13)
    assert za_na == date(2026, 9, 19)
    assert zo_na == date(2026, 9, 20)
    r = resolve_lezingen(2026, "09-12", "nieuw")
    assert r.override_id == "zaterdag-voor-kruisverheffing"
    assert [a.ref for a in r.apostel] == ["1 Kor. 2:6-9"]
    r = resolve_lezingen(2026, "09-13", "nieuw")
    assert r.override_id == "zondag-voor-kruisverheffing"
    assert [e.ref for e in r.evangelie] == ["Joh. 3:13-17"]
    r = resolve_lezingen(2026, "09-19", "nieuw")
    assert r.override_id == "zaterdag-na-kruisverheffing"
    r = resolve_lezingen(2026, "09-20", "nieuw")
    assert r.override_id == "zondag-na-kruisverheffing"
    assert [e.ref for e in r.evangelie] == ["Mark. 8:34-9:1"]


def test_kruisverheffing_op_zaterdag_of_zondag() -> None:
    # 14 sept. 2024 is zaterdag: «zaterdag vóór» is 7 sept., niet het feest.
    assert date(2024, 9, 14).isoweekday() == 6
    assert weekday_relative_date(
        2024, "09-14", 6, 1, "voor", stijl="nieuw"
    ) == date(2024, 9, 7)
    assert resolve_lezingen(2024, "09-14", "nieuw").override_id == "kruisverheffing"
    assert (
        resolve_lezingen(2024, "09-07", "nieuw").override_id
        == "zaterdag-voor-kruisverheffing"
    )
    # Zondag vóór valt op 8 sept. = Geboorte Moeder Gods; het grootfeest wint.
    assert date(2024, 9, 8).isoweekday() == 7
    assert (
        resolve_lezingen(2024, "09-08", "nieuw").override_id
        == "geboorte-moeder-gods"
    )
    # 14 sept. 2025 is zondag: «zondag ná» is 21 sept., niet het feest.
    assert date(2025, 9, 14).isoweekday() == 7
    assert weekday_relative_date(
        2025, "09-14", 7, 1, "na", stijl="nieuw"
    ) == date(2025, 9, 21)
    assert resolve_lezingen(2025, "09-14", "nieuw").override_id == "kruisverheffing"
    assert (
        resolve_lezingen(2025, "09-21", "nieuw").override_id
        == "zondag-na-kruisverheffing"
    )


def test_kruisverheffing_zaterdag_zondag_geen_feest_entries() -> None:
    by_id = {e["id"]: e for e in load_entries()}
    for eid in (
        "zaterdag-voor-kruisverheffing",
        "zondag-voor-kruisverheffing",
        "zaterdag-na-kruisverheffing",
        "zondag-na-kruisverheffing",
        "zaterdag-voor-theofanie",
        "zondag-voor-theofanie",
        "zaterdag-na-theofanie",
        "zaterdag-voor-kerst",
    ):
        assert eid not in by_id


def test_theofanie_zaterdag_zondag_2026() -> None:
    # 6 januari 2026 is dinsdag.
    assert date(2026, 1, 6).isoweekday() == 2
    assert weekday_relative_date(
        2026, "01-06", 6, 1, "voor", stijl="nieuw"
    ) == date(2026, 1, 3)
    assert weekday_relative_date(
        2026, "01-06", 7, 1, "voor", stijl="nieuw"
    ) == date(2026, 1, 4)
    assert weekday_relative_date(
        2026, "01-06", 6, 1, "na", stijl="nieuw"
    ) == date(2026, 1, 10)
    r = resolve_lezingen(2026, "01-03", "nieuw")
    assert r.override_id == "zaterdag-voor-theofanie"
    assert [a.ref for a in r.apostel] == ["1 Tim. 3:14-4:5"]
    assert [e.ref for e in r.evangelie] == ["Matt. 3:1-11"]
    r = resolve_lezingen(2026, "01-04", "nieuw")
    assert r.override_id == "zondag-voor-theofanie"
    r = resolve_lezingen(2026, "01-10", "nieuw")
    assert r.override_id == "zaterdag-na-theofanie"
    assert [e.ref for e in r.evangelie] == ["Matt. 4:1-11"]


def test_theofanie_samenval_grootfeest() -> None:
    # 6 jan. 2023 is vrijdag: zondag vóór = 1 jan. = Besnijdenis (wint van
    # zondag-na-kerst én zondag-voor-theofanie).
    assert date(2023, 1, 6).isoweekday() == 5
    assert weekday_relative_date(
        2023, "01-06", 7, 1, "voor", stijl="nieuw"
    ) == date(2023, 1, 1)
    assert resolve_lezingen(2023, "01-01", "nieuw").override_id == (
        "besnijdenis-des-heren"
    )
    # Zaterdag ná Theofanie = 7 jan. = synaxis Johannes.
    assert weekday_relative_date(
        2023, "01-06", 6, 1, "na", stijl="nieuw"
    ) == date(2023, 1, 7)
    assert (
        resolve_lezingen(2023, "01-07", "nieuw").override_id
        == "synaxis-johannes-doper"
    )
    # 6 jan. 2024 is zaterdag: het feest zelf, niet «zaterdag vóór».
    assert date(2024, 1, 6).isoweekday() == 6
    assert resolve_lezingen(2024, "01-06", "nieuw").override_id == "theofanie"
    assert weekday_relative_date(
        2024, "01-06", 6, 1, "voor", stijl="nieuw"
    ) == date(2023, 12, 30)
    assert (
        resolve_lezingen(2023, "12-30", "nieuw").override_id
        == "zaterdag-voor-theofanie"
    )


def test_zaterdag_voor_kerst_2026() -> None:
    assert date(2026, 12, 25).isoweekday() == 5
    assert weekday_relative_date(
        2026, "12-25", 6, 1, "voor", stijl="nieuw"
    ) == date(2026, 12, 19)
    r = resolve_lezingen(2026, "12-19", "nieuw")
    assert r.override_id == "zaterdag-voor-kerst"
    assert [a.ref for a in r.apostel] == ["Gal. 3:8-12"]
    assert [e.ref for e in r.evangelie] == ["Luc. 13:18-29"]


def test_begin_kerkelijk_jaar_2026() -> None:
    r = resolve_lezingen(2026, "09-01", "nieuw")
    assert r.override_id == "begin-kerkelijk-jaar"
    assert [a.ref for a in r.apostel] == ["1 Tim. 2:1-7"]
    assert [e.ref for e in r.evangelie] == ["Luc. 4:16-22"]


def test_zondag_vaderen_zevende_concilie() -> None:
    # 10 oktober 2026 is zaterdag → zondag ná = 11 oktober.
    assert date(2026, 10, 10).isoweekday() == 6
    assert weekday_relative_date(
        2026, "10-10", 7, 1, "na", stijl="nieuw"
    ) == date(2026, 10, 11)
    r = resolve_lezingen(2026, "10-11", "nieuw")
    assert r.override_id == "zondag-vaderen-zevende-concilie"
    assert [a.ref for a in r.apostel] == ["Tit. 3:8-15", "Heb. 13:7-16"]
    assert [e.ref for e in r.evangelie] == ["Joh. 17:1-13"]
    # Als 10 oktober zelf zondag is: strikt ná = 17 oktober.
    assert date(2021, 10, 10).isoweekday() == 7
    assert weekday_relative_date(
        2021, "10-10", 7, 1, "na", stijl="nieuw"
    ) == date(2021, 10, 17)
    assert (
        resolve_lezingen(2021, "10-17", "nieuw").override_id
        == "zondag-vaderen-zevende-concilie"
    )
