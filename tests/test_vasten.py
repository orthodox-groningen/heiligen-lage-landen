"""Vastenregels: periode boven wekelijks; feestversoepeling; norm in YAML."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate import (  # noqa: E402
    CONTENT,
    _dump_hugo_markdown,
    period_bounds_for_year,
)
from load_entries import load_entries  # noqa: E402
from vasten import (  # noqa: E402
    NIVEAU_LABELS,
    entries_on_civil_date,
    indicatie_op_datum,
    load_vastenregels,
    mix_vastenniveau,
    render_vasten_clerus,
    render_vasten_technisch,
)


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


def test_yaml_niveaus_dekken_de_code() -> None:
    regels = load_vastenregels()
    ids = {n["id"] for n in regels["niveaus"]}
    assert ids == set(NIVEAU_LABELS)


def test_regels_voorbeelden_tegen_de_code() -> None:
    """Elk voorbeeld in data/regels/vasten.yaml moet matchen met mix_vastenniveau."""
    regels = load_vastenregels()
    catalogus = load_entries()
    for regel in regels["regels"]:
        rid = regel["id"]
        for i, v in enumerate(regel.get("voorbeelden") or []):
            expected = v.get("verwachte_niveau")
            if v.get("datum"):
                y, m, d = (int(x) for x in v["datum"].split("-"))
                day = date(y, m, d)
                ind = indicatie_op_datum(catalogus, day)
            else:
                ind = mix_vastenniveau(
                    list(v["entries"]),
                    int(v["weekday"]),
                    v.get("mmdd"),
                )
            got = None if ind is None else ind.niveau
            assert got == expected, (
                f"R-{rid} voorbeeld {i} ({v.get('datum') or 'synthetisch'}): "
                f"code={got!r} yaml={expected!r} — {v.get('toelichting') or ''}"
            )


def test_uitleg_vasten_is_gegenereerd_uit_yaml() -> None:
    regels = load_vastenregels()
    tech = regels["technisch"]
    clerus = _dump_hugo_markdown(
        {
            "title": regels["titel"],
            "description": regels["beschrijving"],
            "generator": "data/regels/vasten.yaml",
            "uitleg_stijl": "vasten",
        },
        render_vasten_clerus(regels),
    )
    technisch = _dump_hugo_markdown(
        {
            "title": tech["titel"],
            "description": tech["beschrijving"],
            "generator": "data/regels/vasten.yaml",
            "uitleg_stijl": "vasten-technisch",
            "build": {"list": "never", "render": "always"},
        },
        render_vasten_technisch(regels),
    )
    assert (CONTENT / "uitleg" / "vasten.md").read_text(encoding="utf-8") == clerus
    assert (
        CONTENT / "uitleg" / "vasten-technisch.md"
    ).read_text(encoding="utf-8") == technisch


def test_cleruspagina_heeft_geen_technische_sporen() -> None:
    body = render_vasten_clerus()
    assert "data/regels/vasten.yaml" not in body
    assert "scripts/vasten.py" not in body
    assert "calendar.js" not in body
    assert "R-periode-boven-wekelijks" not in body
    assert "→" not in body
    assert "wo/vr" not in body
    for regel in load_vastenregels()["regels"]:
        assert regel["titel"] in body


def test_technisch_noemt_elk_regel_id() -> None:
    body = render_vasten_technisch()
    assert "data/regels/vasten.yaml" in body
    for regel in load_vastenregels()["regels"]:
        assert f"R-{regel['id']}" in body


def test_vrijdag_in_grote_vasten_geen_wekelijks() -> None:
    day = date(2026, 3, 20)
    ids = {e["id"] for e in entries_on_civil_date(load_entries(), day)}
    assert "vrijdag-vasten" not in ids
    assert "grote-vasten" in ids
