"""Vastenperiode vervangt wekelijks wo/vr-vasten; feesten kunnen versoepelen."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate import period_bounds_for_year  # noqa: E402
from kalender import mmdd_from_date, pascha_offset_date  # noqa: E402
from load_entries import load_entries  # noqa: E402
from vasten import mix_vastenniveau  # noqa: E402


def _by_id() -> dict[str, dict]:
    return {e["id"]: e for e in load_entries()}


def _day_entries(day: date) -> list[dict]:
    """Entries die op deze burgerlijke dag vallen (wekelijks al onderdrukt)."""
    entries = load_entries()
    mmdd = mmdd_from_date(day)
    matched: list[dict] = []
    suppressed = False
    for e in entries:
        dn = e["datum_norm"]
        vorm = dn.get("vorm") or "dag"
        if vorm == "weekdagen":
            continue
        bounds = period_bounds_for_year(e, day.year)
        hit = False
        if bounds:
            start, end = bounds
            if start <= end:
                hit = start <= day <= end
            else:
                hit = day >= start or day <= end
        elif e.get("cyclus") == "paascyclus" and vorm == "dag":
            hit = pascha_offset_date(day.year, dn["paascyclus_offset"]) == day
        elif dn.get("feestdatum") == mmdd:
            hit = True
        if not hit:
            continue
        matched.append(e)
        if e.get("onderdrukt_wekelijks_vasten") or (
            e["soort"] == "vasten" and vorm != "weekdagen"
        ):
            suppressed = True
    if not suppressed:
        for e in entries:
            dn = e["datum_norm"]
            if dn.get("vorm") == "weekdagen" and day.isoweekday() in dn["weekdagen"]:
                matched.append(e)
    return matched


def _indicatie(day: date):
    return mix_vastenniveau(_day_entries(day), day.isoweekday())


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


def test_aankondiging_in_grote_vasten_is_vis() -> None:
    """25 maart 2026 = woensdag in de Grote Vasten → vis."""
    day = date(2026, 3, 25)
    assert day.isoweekday() == 3
    ind = _indicatie(day)
    assert ind is not None
    assert ind.niveau == "vis"
    assert ind.periode_id == "grote-vasten"
    assert ind.versoepeld_door_id == "aankondiging"
    assert "versoepeld (Aankondiging" in ind.tekst


def test_vrijdag_in_grote_vasten_blijft_streng() -> None:
    day = date(2026, 3, 20)
    assert day.isoweekday() == 5
    ind = _indicatie(day)
    assert ind is not None
    assert ind.niveau == "streng"
    assert ind.periode_id == "grote-vasten"
    assert ind.versoepeld_door_id is None
    assert "vrijdag-vasten" not in {e["id"] for e in _day_entries(day)}


def test_zaterdag_in_grote_vasten_wijn_olie() -> None:
    day = date(2026, 3, 21)
    assert day.isoweekday() == 6
    ind = _indicatie(day)
    assert ind is not None
    assert ind.niveau == "wijn_olie"
    assert ind.weekend is True
    assert "(zaterdag)" in ind.tekst


def test_lazarus_zaterdag_is_vis() -> None:
    """4 april 2026 = Lazarus-zaterdag, nog in de Grote Vasten."""
    day = date(2026, 4, 4)
    ind = _indicatie(day)
    assert ind is not None
    assert ind.niveau == "vis"
    assert ind.versoepeld_door_id == "lazarus-zaterdag"


def test_palmzondag_is_vis() -> None:
    """Palmzondag valt tussen Grote Vasten en Grote Week."""
    day = date(2026, 4, 5)
    ids = {e["id"] for e in _day_entries(day)}
    assert "palmzondag" in ids
    assert "grote-vasten" not in ids
    assert "grote-week" not in ids
    ind = _indicatie(day)
    assert ind is not None
    assert ind.niveau == "vis"
    assert "Palmzondag" in ind.tekst


def test_grote_vrijdag_blijft_streng() -> None:
    day = date(2026, 4, 10)
    ind = _indicatie(day)
    assert ind is not None
    assert ind.niveau == "streng"
    assert ind.periode_id == "grote-week"
    assert ind.weekend is False


def test_grote_zaterdag_geen_weekendversoepeling() -> None:
    day = date(2026, 4, 11)
    assert day.isoweekday() == 6
    ind = _indicatie(day)
    assert ind is not None
    assert ind.niveau == "streng"
    assert ind.periode_id == "grote-week"


def test_aankondiging_in_grote_week_cap_wijn_olie() -> None:
    """Feest-vis in de Grote Week gaat niet verder dan wijn/olie."""
    ind = mix_vastenniveau(
        [
            {
                "id": "grote-week",
                "soort": "vasten",
                "vorm": "periode",
                "vastenniveau": "streng",
                "naam": "Grote Week",
            },
            {
                "id": "aankondiging",
                "soort": "feest",
                "vorm": "dag",
                "vastenniveau": "vis",
                "naam": "Aankondiging aan de Moeder Gods",
                "observances": ["feest"],
            },
        ],
        weekday=2,
    )
    assert ind is not None
    assert ind.niveau == "wijn_olie"
    assert ind.versoepeld_door_id == "aankondiging"


def test_transfiguratie_in_ontslapen_vasten_is_vis() -> None:
    day = date(2026, 8, 6)
    ind = _indicatie(day)
    assert ind is not None
    assert ind.niveau == "vis"
    assert ind.periode_id == "ontslapen-vasten"
    assert ind.versoepeld_door_id == "transfiguratie"


def test_vrijdag_ontslapen_vasten_streng_geen_wekelijks() -> None:
    day = date(2026, 8, 7)
    assert day.isoweekday() == 5
    ids = {e["id"] for e in _day_entries(day)}
    assert "vrijdag-vasten" not in ids
    ind = _indicatie(day)
    assert ind is not None
    assert ind.niveau == "streng"


def test_tempelgang_in_geboortevasten_is_vis() -> None:
    day = date(2026, 11, 21)
    ind = _indicatie(day)
    assert ind is not None
    assert ind.niveau == "vis"
    assert ind.periode_id == "geboorte-vasten"
    assert ind.versoepeld_door_id == "tempelgang-moeder-gods"


def test_kruisverheffing_is_streng_ook_buiten_periode() -> None:
    day = date(2026, 9, 14)
    assert day.isoweekday() == 1
    ind = _indicatie(day)
    assert ind is not None
    assert ind.niveau == "streng"
    assert "Kruisverheffing" in ind.tekst


def test_onthoofding_zaterdag_blijft_streng() -> None:
    day = date(2026, 8, 29)
    assert day.isoweekday() == 6
    ind = _indicatie(day)
    assert ind is not None
    assert ind.niveau == "streng"


def test_kerst_op_vrijdag_is_vastenvrij() -> None:
    day = date(2026, 12, 25)
    assert day.isoweekday() == 5
    ids = {e["id"] for e in _day_entries(day)}
    assert "vrijdag-vasten" not in ids
    ind = _indicatie(day)
    assert ind is not None
    assert ind.niveau == "vrij"
    assert "Vastenvrij" in ind.tekst


def test_geboorte_moeder_gods_versoepelt_alleen_wo_vr() -> None:
    """Dinsdag 8 september 2026: geen vasten; woensdag wel vis."""
    dinsdag = date(2026, 9, 8)
    assert dinsdag.isoweekday() == 2
    assert _indicatie(dinsdag) is None

    woensdag = mix_vastenniveau(
        [
            {
                "id": "woensdag-vasten",
                "soort": "vasten",
                "vorm": "weekdagen",
                "vastenniveau": "wijn_olie",
                "naam": "Woensdagvasten",
            },
            {
                "id": "geboorte-moeder-gods",
                "soort": "feest",
                "vorm": "dag",
                "vastenniveau": "vis",
                "naam": "Geboorte van de Moeder Gods",
                "observances": ["feest"],
            },
        ],
        weekday=3,
    )
    assert woensdag is not None
    assert woensdag.niveau == "vis"
    assert woensdag.versoepeld_door_id == "geboorte-moeder-gods"


def test_lichte_week_is_vastenvrij() -> None:
    day = date(2026, 4, 13)
    ind = _indicatie(day)
    assert ind is not None
    assert ind.niveau == "vrij"
    ids = {e["id"] for e in _day_entries(day)}
    assert "woensdag-vasten" not in ids
    assert "vrijdag-vasten" not in ids
