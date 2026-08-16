"""Genereer Hugo-content, entries.json en ICS-feeds."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from load_entries import load_entries  # noqa: E402
from vasten import (  # noqa: E402
    load_vastenregels,
    render_vasten_clerus,
    render_vasten_technisch,
)
from kalender import (  # noqa: E402
    format_mmdd,
    gregorian_to_julian_calendar,
    julian_feast_to_civil_date,
    mmdd_from_date,
    parse_mmdd,
    pascha_offset_date,
)

SITE = ROOT / "site"
CONTENT = SITE / "content"
STATIC_DATA = SITE / "static" / "data"
STATIC_ICS = SITE / "static" / "ics"

# Live site / ICS: huidig jaar −2 … +25.
ICS_YEAR_BACK = 2
ICS_YEAR_FORWARD = 25

MONTH_NAMES_NL = [
    "",
    "januari",
    "februari",
    "maart",
    "april",
    "mei",
    "juni",
    "juli",
    "augustus",
    "september",
    "oktober",
    "november",
    "december",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genereer site-content en ICS.")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Wis gegenereerde dag-/entry-mappen vóór genereren.",
    )
    return parser.parse_args()


def mmdd_label(mmdd: str) -> str:
    month, day = (int(x) for x in mmdd.split("-"))
    return f"{day} {MONTH_NAMES_NL[month]}"


def occurrence_years(today: date | None = None) -> range:
    today = today or date.today()
    return range(today.year - ICS_YEAR_BACK, today.year + ICS_YEAR_FORWARD + 1)


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


SOORT_DIR = {
    "feest": "feesten",
    "heilige": "heiligen",
    "vasten": "vasten",
}


def entry_permalink(entry: dict[str, Any]) -> str:
    kind = SOORT_DIR[entry["soort"]]
    return f"/{kind}/{entry['id']}/"


def mmdd_in_inclusive_range(mmdd: str, van: str, tot: str) -> bool:
    """True als mmdd in [van, tot] ligt; ondersteunt jaarovergang (van > tot)."""
    if van <= tot:
        return van <= mmdd <= tot
    return mmdd >= van or mmdd <= tot


def iter_civil_days(start: date, end: date):
    """Inclusieve reeks kalenderdagen."""
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def render_refs_md(refs: list[dict[str, Any]]) -> str:
    if not refs:
        return "_Nog geen referenties._\n"
    lines = []
    for ref in refs:
        label = ref.get("label") or "Bron"
        url = ref.get("url")
        geraadpleegd = ref.get("geraadpleegd")
        opmerking = ref.get("opmerking")
        if url:
            line = f"- [{label}]({url})"
        elif ref.get("isbn"):
            pagina = ref.get("pagina")
            line = f"- {label} — ISBN {ref['isbn']}"
            if pagina:
                line += f", p. {pagina}"
        elif ref.get("locator"):
            line = f"- {label} — {ref['locator']}"
        else:
            line = f"- {label}"
        extras = []
        if geraadpleegd:
            extras.append(f"geraadpleegd {geraadpleegd}")
        if opmerking:
            extras.append(opmerking)
        if extras:
            line += f" — {'; '.join(extras)}"
        lines.append(line)
    return "\n".join(lines) + "\n"


def period_bounds_for_year(
    entry: dict[str, Any], year: int
) -> tuple[date, date] | None:
    """Start/eind (inclusief) van een periode in een burgerlijk jaar."""
    dn = entry["datum_norm"]
    vorm = dn.get("vorm") or "dag"
    if vorm == "periode" and dn.get("van") and dn.get("tot"):
        vm, vd = parse_mmdd(dn["van"])
        tm, td = parse_mmdd(dn["tot"])
        return date(year, vm, vd), date(year, tm, td)
    if entry.get("cyclus") == "paascyclus" and vorm == "periode":
        start = pascha_offset_date(year, dn["van_offset_dagen"])
        end = pascha_offset_date(year, dn["tot_offset_dagen"])
        if start > end:
            return None
        return start, end
    if entry.get("cyclus") == "paascyclus" and vorm == "periode_hybride":
        start = pascha_offset_date(year, dn["van_offset_dagen"])
        tm, td = parse_mmdd(dn["tot_mmdd"])
        end = date(year, tm, td)
        if start > end:
            return None
        return start, end
    return None


def write_entry_page(entry: dict[str, Any]) -> None:
    kind = SOORT_DIR[entry["soort"]]
    title = entry["namen"]["primair"]
    dn = entry["datum_norm"]
    feestdatum = dn.get("feestdatum")
    vorm = dn.get("vorm") or "dag"
    fm = [
        "---",
        f"title: {yaml_quote(title)}",
        f"slug: {entry['id']}",
        f"type: {entry['soort']}",
        f"soort: {entry['soort']}",
        f"entry_id: {entry['id']}",
        f"cyclus: {entry.get('cyclus') or 'jaar'}",
        f"status: {entry.get('status', 'stub')}",
        f"lagenlanden: {'true' if entry.get('lagenlanden') else 'false'}",
        f"source_path: {yaml_quote(entry['source_path'])}",
    ]
    if feestdatum and vorm == "dag":
        fm.append(f"feestdatum: {feestdatum}")
    if dn.get("van") and dn.get("tot"):
        fm.append(f"van: {dn['van']}")
        fm.append(f"tot: {dn['tot']}")
    if dn.get("weekdagen"):
        fm.append("weekdagen:")
        for d in dn["weekdagen"]:
            fm.append(f"  - {d}")
    if entry.get("cyclus") == "paascyclus":
        if dn.get("paascyclus_offset") is not None and vorm == "dag":
            fm.append(f"paascyclus_offset: {dn['paascyclus_offset']}")
        if dn.get("van_offset_dagen") is not None:
            fm.append(f"van_offset_dagen: {dn['van_offset_dagen']}")
        if dn.get("tot_offset_dagen") is not None:
            fm.append(f"tot_offset_dagen: {dn['tot_offset_dagen']}")
        if dn.get("tot_mmdd"):
            fm.append(f"tot: {dn['tot_mmdd']}")
    if entry.get("titels"):
        fm.append("titels:")
        for t in entry["titels"]:
            fm.append(f"  - {yaml_quote(t)}")
    alts = (entry.get("namen") or {}).get("alternatief") or []
    if alts:
        fm.append("alternatief:")
        for a in alts:
            fm.append(f"  - {yaml_quote(a)}")
    icoon = entry.get("icoon") or {}
    if icoon.get("bestand") and icoon.get("rechten") == "ok":
        fm.append(f"icoon: {yaml_quote('/' + icoon['bestand'].lstrip('/'))}")
    fm.append("---")

    body: list[str] = []
    if entry.get("titels"):
        body.append("*" + " · ".join(entry["titels"]) + "*")
        body.append("")

    weeknamen = {
        1: "maandag",
        2: "dinsdag",
        3: "woensdag",
        4: "donderdag",
        5: "vrijdag",
        6: "zaterdag",
        7: "zondag",
    }
    if vorm == "weekdagen":
        namen = ", ".join(weeknamen[d] for d in dn["weekdagen"])
        body.append(f"**Wekelijks:** elke {namen}.")
        body.append("")
    elif entry.get("cyclus") == "paascyclus" and vorm in {"periode", "periode_hybride"}:
        van_o = dn["van_offset_dagen"]
        body.append(
            f"**Paascyclus-periode:** vanaf {van_o:+d} dagen t.o.v. Orthodox Pascha"
        )
        if vorm == "periode":
            body.append(f" tot en met {dn['tot_offset_dagen']:+d} dagen.")
        else:
            body.append(
                f" tot en met {mmdd_label(dn['tot_mmdd'])} (vaste einddatum)."
            )
        body.append("")
        body.append("**Komende jaren (wereldlijk / Gregoriaans):**")
        body.append("")
        for y in occurrence_years():
            start = pascha_offset_date(y, van_o)
            if vorm == "periode":
                end = pascha_offset_date(y, dn["tot_offset_dagen"])
            else:
                tm, td = parse_mmdd(dn["tot_mmdd"])
                end = date(y, tm, td)
            if start > end:
                body.append(f"- {y}: _geen dagen_ (begin na einddatum)")
            else:
                body.append(
                    f"- {y}: {mmdd_label(mmdd_from_date(start))} – "
                    f"{mmdd_label(mmdd_from_date(end))}"
                )
        body.append("")
    elif entry.get("cyclus") == "paascyclus":
        offset = dn["paascyclus_offset"]
        sign = "+" if offset >= 0 else ""
        body.append(
            f"**Paascyclus:** {sign}{offset} dagen t.o.v. Orthodox Pascha "
            "(zelfde wereldlijke datum voor alle Orthodoxe kerken)."
        )
        body.append("")
        body.append("**Komende jaren (wereldlijk / Gregoriaans):**")
        body.append("")
        for y in occurrence_years():
            d = pascha_offset_date(y, offset)
            jy, jm, jd = gregorian_to_julian_calendar(d)
            body.append(
                f"- {y}: {mmdd_label(mmdd_from_date(d))} "
                f"(Juliaans {jd} {MONTH_NAMES_NL[jm]})"
            )
        body.append("")
    elif vorm == "periode" and dn.get("van") and dn.get("tot"):
        body.append(
            f"**Periode:** {mmdd_label(dn['van'])} – {mmdd_label(dn['tot'])} "
            "(zelfde dagnamen in nieuwe én oude kalender)."
        )
        body.append("")
    else:
        assert feestdatum
        body.append(
            f"**Feestdag:** {mmdd_label(feestdatum)} "
            f"(zelfde datum in de nieuwe/Gregoriaanse én de oude/Juliaanse kalender)"
        )
        if dn.get("gregoriaans") or dn.get("juliaans"):
            parts = []
            if dn.get("gregoriaans"):
                parts.append(f"Gregoriaans {mmdd_label(dn['gregoriaans'])}")
            if dn.get("juliaans"):
                parts.append(f"Juliaans {mmdd_label(dn['juliaans'])}")
            body.append("")
            body.append("**Expliciete notatie:** " + "; ".join(parts))
        body.append("")
    if entry.get("vastenniveau"):
        niveau_labels = {
            "streng": "streng",
            "wijn_olie": "wijn en olie",
            "vis": "vis toegestaan (typikon)",
            "lichter": "lichter",
            "vrij": "vastenvrij",
        }
        body.append(
            f"**Vastenniveau (indicatief):** "
            f"{niveau_labels.get(entry['vastenniveau'], entry['vastenniveau'])}."
        )
        body.append("")
    if entry.get("onderdrukt_wekelijks_vasten"):
        body.append(
            "**Wekelijks vasten:** woensdag- en vrijdagvasten gelden niet in deze periode."
        )
        body.append("")
    if entry.get("locaties"):
        body.append("**Plaatsen:** " + "; ".join(entry["locaties"]))
        body.append("")
    if entry.get("periode"):
        body.append(f"**Periode:** {entry['periode']}")
        body.append("")
    if entry.get("samenvatting"):
        body.append(entry["samenvatting"].strip())
        body.append("")
    if entry.get("verhaal"):
        body.append("## Verhaal")
        body.append("")
        body.append(entry["verhaal"].strip())
        body.append("")
    elif entry.get("status") == "stub":
        body.append(
            "> Deze pagina is nog een stub: alleen basisgegevens. "
            "Een onderbouwd verhaal volgt."
        )
        body.append("")
    body.append("## Referenties")
    body.append("")
    body.append(render_refs_md(entry.get("referenties") or []))
    body.append("")
    if feestdatum and vorm == "dag":
        body.append(
            f"[Meneon: {mmdd_label(feestdatum)}](/meneon/?dag={feestdatum}) · "
            f"[Deze dag dit jaar](/datum/?dag={feestdatum})"
        )
        body.append("")
    write_text(CONTENT / kind / f"{entry['id']}.md", "\n".join(fm + ["", *body]))


def write_generated_indexes() -> None:
    """Sectie-indexes die bij --clean opnieuw worden aangemaakt."""
    write_text(
        CONTENT / "heiligen" / "_index.md",
        """---
title: "Heiligen"
---

Overzicht van heiligen van de Lage Landen in deze kalender.
""",
    )
    write_text(
        CONTENT / "feesten" / "_index.md",
        """---
title: "Vaste feesten"
---

Grote vaste feesten van de jaarcyclus en de paascyclus.
""",
    )
    write_text(
        CONTENT / "vasten" / "_index.md",
        """---
title: "Vasten"
---

Vastenperiodes en wekelijkse vastendagen.
""",
    )


def _split_hugo_markdown(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n") and text != "---":
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        raise ValueError("front matter zonder afsluitende ---")
    fm_raw = text[4:end]
    body = text[end + 4 :]
    if body.startswith("\n"):
        body = body[1:]
    meta = yaml.safe_load(fm_raw) or {}
    if not isinstance(meta, dict):
        raise ValueError("front matter moet een mapping zijn")
    return meta, body


def _dump_hugo_markdown(meta: dict[str, Any], body: str) -> str:
    # Stabiele, leesbare YAML (title eerst, dan layout, dan rest).
    ordered: dict[str, Any] = {}
    if "title" in meta:
        ordered["title"] = meta["title"]
    if "layout" in meta:
        ordered["layout"] = meta["layout"]
    for key, value in meta.items():
        if key in ordered:
            continue
        ordered[key] = value
    dumped = yaml.safe_dump(
        ordered,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).strip()
    body = body if body.endswith("\n") or body == "" else body + "\n"
    body = body.lstrip("\n")
    return f"---\n{dumped}\n---\n\n{body}"


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def ensure_hand_owned_indexes() -> None:
    """Handmatige sectiepagina's: bestaan, niet-lege title, juiste layout.

    Overschrijft geen body en raakt andere front matter niet aan, behalve
    het corrigeren van `layout` als die ontbreekt of afwijkt.
    """
    specs = [
        {
            "path": CONTENT / "_index.md",
            "title": "Heiligen van de Lage Landen",
            "layout": None,
        },
        {
            "path": CONTENT / "kalender" / "_index.md",
            "title": "Jaarkalender",
            "layout": "kalender",
        },
        {
            "path": CONTENT / "meneon" / "_index.md",
            "title": "Meneon",
            "layout": "meneon",
        },
        {
            "path": CONTENT / "datum" / "_index.md",
            "title": "Datum",
            "layout": "datum",
        },
        {
            "path": CONTENT / "agenda" / "_index.md",
            "title": "Agenda (ICS)",
            "layout": "agenda",
        },
        {
            "path": CONTENT / "uitleg" / "_index.md",
            "title": "Uitleg",
            "layout": None,
        },
        {
            "path": CONTENT / "beheer" / "_index.md",
            "title": "Voor beheerders",
            "layout": None,
        },
    ]

    for spec in specs:
        path: Path = spec["path"]
        default_title: str = spec["title"]
        expected_layout = spec["layout"]
        if not path.exists():
            meta: dict[str, Any] = {"title": default_title}
            if expected_layout:
                meta["layout"] = expected_layout
            write_text(path, _dump_hugo_markdown(meta, ""))
            print(f"Aangemaakt: {_rel(path)}")
            continue
        try:
            meta, body = _split_hugo_markdown(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise SystemExit(f"{_rel(path)}: {exc}") from exc
        title = meta.get("title")
        if not isinstance(title, str) or not title.strip():
            raise SystemExit(
                f"{_rel(path)}: front matter 'title' ontbreekt of is leeg"
            )
        changed = False
        if expected_layout is not None and meta.get("layout") != expected_layout:
            meta["layout"] = expected_layout
            changed = True
        if expected_layout is None and meta.get("layout") == "uitleg":
            # Legacy: oude monolithische uitleg-layout verwijderen.
            del meta["layout"]
            changed = True
        if changed:
            write_text(path, _dump_hugo_markdown(meta, body))
            print(f"Front matter bijgewerkt: {_rel(path)}")


# Onderwerpen onder site/content/uitleg/<id>.md — handmatig, stabiele ids.
ACHTERGROND_TOPICS: list[dict[str, str]] = [
    {
        "id": "nieuw-oud",
        "title": "Nieuwe en Oude kalender",
        "description": "Welke kalender uw parochie volgt, en wat de knop Nieuw/Oud doet",
    },
    {
        "id": "feestdatum",
        "title": "Feestdatum",
        "description": "De naam van een feestdag in het kerkelijk jaar, in nieuw en oud dezelfde",
    },
    {
        "id": "datumpagina",
        "title": "Datumpagina’s",
        "description": "Wat er op één burgerlijke dag in een bepaald jaar valt",
    },
    {
        "id": "meneon",
        "title": "Meneon",
        "description": "De vaste jaarcyclus: wat er altijd op een kalenderdag hoort",
    },
    {
        "id": "kleuren",
        "title": "Kleuren in de jaarkalender",
        "description": "Wat de kleuren op de jaarkalender betekenen",
    },
    {
        "id": "vasten",
        "title": "Vasten",
        "description": "Waar onze vastenregels vandaan komen, en wat de kalender toont",
    },
    {
        "id": "agenda",
        "title": "Agenda",
        "description": "Heiligen, feesten en vasten in Google Calendar, Apple Agenda of Outlook",
    },
]


def ensure_achtergrond_topics() -> None:
    """Zorg dat bekende uitleg-onderwerpen bestaan met niet-lege title.

    Body en overige front matter blijven onaangeroerd. Ontbrekende bestanden
    krijgen een korte stub.
    """
    uitleg_dir = CONTENT / "uitleg"
    uitleg_dir.mkdir(parents=True, exist_ok=True)
    for topic in ACHTERGROND_TOPICS:
        path = uitleg_dir / f"{topic['id']}.md"
        if not path.exists():
            meta = {
                "title": topic["title"],
                "description": topic["description"],
            }
            body = (
                f"_{topic['description']}_\n\n"
                "(Tekst nog toe te voegen.)\n"
            )
            write_text(path, _dump_hugo_markdown(meta, body))
            print(f"Aangemaakt: {_rel(path)}")
            continue
        try:
            meta, _body = _split_hugo_markdown(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise SystemExit(f"{_rel(path)}: {exc}") from exc
        title = meta.get("title")
        if not isinstance(title, str) or not title.strip():
            raise SystemExit(
                f"{_rel(path)}: front matter 'title' ontbreekt of is leeg"
            )


def write_vasten_uitleg() -> None:
    """Genereer clerus- en technische vastenpagina uit data/regels/vasten.yaml."""
    regels = load_vastenregels()
    write_text(
        CONTENT / "uitleg" / "vasten.md",
        _dump_hugo_markdown(
            {
                "title": regels["titel"],
                "description": regels["beschrijving"],
                "generator": "data/regels/vasten.yaml",
                "uitleg_stijl": "vasten",
            },
            render_vasten_clerus(regels),
        ),
    )
    tech = regels.get("technisch") or {}
    write_text(
        CONTENT / "uitleg" / "vasten-technisch.md",
        _dump_hugo_markdown(
            {
                "title": tech.get("titel") or "Vasten (technisch)",
                "description": tech.get("beschrijving") or "",
                "generator": "data/regels/vasten.yaml",
                "uitleg_stijl": "vasten-technisch",
                "build": {"list": "never", "render": "always"},
            },
            render_vasten_technisch(regels),
        ),
    )


def write_entries_json(entries: list[dict[str, Any]]) -> None:
    years = list(occurrence_years())
    payload = []
    for entry in entries:
        dn = entry["datum_norm"]
        vorm = dn.get("vorm") or "dag"
        item: dict[str, Any] = {
            "id": entry["id"],
            "soort": entry["soort"],
            "cyclus": entry.get("cyclus") or "jaar",
            "vorm": vorm,
            "naam": entry["namen"]["primair"],
            "alternatief": entry["namen"].get("alternatief") or [],
            "titels": entry.get("titels") or [],
            "samenvatting": (entry.get("samenvatting") or "").strip(),
            "url": entry_permalink(entry),
            "lagenlanden": bool(entry.get("lagenlanden")),
            "status": entry.get("status") or "stub",
            "observances": entry.get("observances") or [],
            "onderdrukt_wekelijks_vasten": bool(
                entry.get("onderdrukt_wekelijks_vasten")
            ),
            "icoon": (entry.get("icoon") or {}).get("bestand")
            if (entry.get("icoon") or {}).get("rechten") == "ok"
            else None,
        }
        if entry.get("vastenniveau"):
            item["vastenniveau"] = entry["vastenniveau"]
        if vorm == "weekdagen":
            item["weekdagen"] = list(dn["weekdagen"])
            item["feestdatum"] = None
        elif vorm == "periode" and dn.get("van") and dn.get("tot"):
            item["van"] = dn["van"]
            item["tot"] = dn["tot"]
            item["feestdatum"] = dn["van"]
        elif entry.get("cyclus") == "paascyclus" and vorm in {
            "periode",
            "periode_hybride",
        }:
            item["van_offset_dagen"] = dn["van_offset_dagen"]
            if vorm == "periode":
                item["tot_offset_dagen"] = dn["tot_offset_dagen"]
            else:
                item["tot"] = dn["tot_mmdd"]
            item["feestdatum"] = None
            periods: dict[str, dict[str, str]] = {}
            for y in years:
                bounds = period_bounds_for_year(entry, y)
                if not bounds:
                    continue
                start, end = bounds
                periods[str(y)] = {
                    "van": mmdd_from_date(start),
                    "tot": mmdd_from_date(end),
                }
            item["period_occurrences"] = periods
        elif entry.get("cyclus") == "paascyclus":
            offset = dn["paascyclus_offset"]
            occ: dict[str, str] = {}
            occ_j: dict[str, str] = {}
            for y in years:
                g = pascha_offset_date(y, offset)
                occ[str(y)] = mmdd_from_date(g)
                _jy, jm, jd = gregorian_to_julian_calendar(g)
                occ_j[str(y)] = format_mmdd(jm, jd)
            item["offset_dagen"] = offset
            item["feestdatum"] = None
            item["occurrences"] = occ
            item["occurrences_juliaans"] = occ_j
        else:
            feestdatum = dn["feestdatum"]
            item["feestdatum"] = feestdatum
            item["feestdatum_juliaans"] = dn.get("juliaans")
            item["feestdatum_gregoriaans"] = dn.get("gregoriaans")
        payload.append(item)
    write_text(
        STATIC_DATA / "entries.json",
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    )



def _ics_escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def _fold(line: str) -> str:
    if len(line) <= 75:
        return line
    parts = [line[:75]]
    rest = line[75:]
    while rest:
        parts.append(" " + rest[:74])
        rest = rest[74:]
    return "\r\n".join(parts)


def build_ics(
    entries: list[dict[str, Any]],
    *,
    cal_name: str,
    stijl: str = "nieuw",
    context_entries: list[dict[str, Any]] | None = None,
) -> str:
    """Bouw ICS voor jaren huidig−2 … +25.

    ``nieuw``: vaste feesten/periodes op de feestdatum (wereldlijk = dagnaam);
    paascyclus op de berekende Orthodoxe (wereldlijke) datum.
    ``oud``: vaste feesten op Juliaanse feestdatum→wereldlijke vierdatum;
    paascyclus ongewijzigd. Wekelijks vasten blijft op burgerlijke weekdag.
    ``context_entries``: volledige set (voor vastenvrije onderdrukking van wo/vr).
    """
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    years = list(occurrence_years())
    context = context_entries if context_entries is not None else entries
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//orthodox-groningen//heiligen-lage-landen//NL",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_ics_escape(cal_name)}",
        "X-WR-TIMEZONE:UTC",
    ]

    def weekly_suppressed(day: date) -> bool:
        for e in context:
            if e.get("soort") == "vasten":
                vorm = (e.get("datum_norm") or {}).get("vorm") or "dag"
                if vorm == "weekdagen":
                    continue
            elif not e.get("onderdrukt_wekelijks_vasten"):
                continue
            bounds = period_bounds_for_year(e, day.year)
            if not bounds:
                continue
            start, end = bounds
            if start <= end:
                if start <= day <= end:
                    return True
            else:
                if day >= start or day <= end:
                    return True
        return False

    def emit_day(
        entry: dict[str, Any],
        civil: date,
        *,
        summary: str,
        uid_key: str,
        fee_label: str,
        extra_desc: list[str] | None = None,
    ) -> None:
        dt_start = civil.strftime("%Y%m%d")
        dt_end_s = (civil + timedelta(days=1)).strftime("%Y%m%d")
        uid = str(uuid.uuid5(uuid.NAMESPACE_URL, uid_key))
        desc_parts = []
        if entry.get("samenvatting"):
            desc_parts.append(entry["samenvatting"].strip())
        desc_parts.append(fee_label)
        if extra_desc:
            desc_parts.extend(extra_desc)
        for ref in entry.get("referenties") or []:
            label = ref.get("label") or "Bron"
            url = ref.get("url")
            desc_parts.append(f"Bron: {label}" + (f" ({url})" if url else ""))
        description = _ics_escape("\n".join(desc_parts))
        event = [
            "BEGIN:VEVENT",
            f"DTSTART;VALUE=DATE:{dt_start}",
            f"DTEND;VALUE=DATE:{dt_end_s}",
            f"DTSTAMP:{now}",
            f"UID:{uid}",
            f"SUMMARY:{_ics_escape(summary)}",
            f"DESCRIPTION:{description}",
            "TRANSP:TRANSPARENT",
            "END:VEVENT",
        ]
        lines.extend(event)

    for entry in entries:
        dn = entry["datum_norm"]
        vorm = dn.get("vorm") or "dag"
        if vorm == "weekdagen":
            for year in years:
                for d in iter_civil_days(date(year, 1, 1), date(year, 12, 31)):
                    if d.isoweekday() not in dn["weekdagen"]:
                        continue
                    if weekly_suppressed(d):
                        continue
                    emit_day(
                        entry,
                        d,
                        summary=entry["namen"]["primair"],
                        uid_key=f"{entry['id']}:week:{stijl}:{d.isoformat()}",
                        fee_label=(
                            f"Wekelijks vasten · "
                            f"{mmdd_label(mmdd_from_date(d))} {year}"
                        ),
                    )
            continue

        if vorm in {"periode", "periode_hybride"}:
            for year in years:
                bounds = period_bounds_for_year(entry, year)
                if not bounds:
                    continue
                start, end = bounds
                if start <= end:
                    days = list(iter_civil_days(start, end))
                else:
                    days = list(iter_civil_days(start, date(year, 12, 31)))
                    days += list(iter_civil_days(date(year, 1, 1), end))
                for d in days:
                    feast_mmdd = mmdd_from_date(d)
                    if stijl == "oud" and dn.get("van") and dn.get("tot"):
                        civil = julian_feast_to_civil_date(year, feast_mmdd)
                        summary = (
                            f"{entry['namen']['primair']} "
                            f"({mmdd_label(feast_mmdd)} Juliaans)"
                        )
                        uid_key = f"{entry['id']}:oud:{year}:{feast_mmdd}"
                        fee_label = (
                            f"Periode · Juliaans {mmdd_label(feast_mmdd)} {year}"
                        )
                    else:
                        civil = d
                        summary = entry["namen"]["primair"]
                        uid_key = f"{entry['id']}:{stijl}:{year}:{feast_mmdd}"
                        fee_label = (
                            f"Vastenperiode · {mmdd_label(feast_mmdd)} {year}"
                        )
                    emit_day(
                        entry,
                        civil,
                        summary=summary,
                        uid_key=uid_key,
                        fee_label=fee_label,
                    )
            continue

        for year in years:
            if entry.get("cyclus") == "paascyclus":
                civil = pascha_offset_date(
                    year, entry["datum_norm"]["paascyclus_offset"]
                )
                summary = entry["namen"]["primair"]
                if stijl == "oud":
                    summary = f"{summary} (Orthodoxe paascyclus)"
                uid_key = f"{entry['id']}:{stijl}:{year}:paas"
                fee_label = f"Wereldlijke datum: {mmdd_label(mmdd_from_date(civil))} {year}"
            else:
                feestdatum = entry["datum_norm"]["feestdatum"]
                if stijl == "oud":
                    civil = julian_feast_to_civil_date(year, feestdatum)
                    summary = (
                        f"{entry['namen']['primair']} "
                        f"({mmdd_label(feestdatum)} Juliaans)"
                    )
                    uid_key = f"{entry['id']}:oud:{year}:{feestdatum}"
                    fee_label = f"Feestdatum: {mmdd_label(feestdatum)} {year}"
                else:
                    month, day = parse_mmdd(feestdatum)
                    civil = date(year, month, day)
                    summary = entry["namen"]["primair"]
                    uid_key = f"{entry['id']}:nieuw:{year}:{feestdatum}"
                    fee_label = f"Feestdatum: {mmdd_label(feestdatum)} {year}"
            emit_day(
                entry,
                civil,
                summary=summary,
                uid_key=uid_key,
                fee_label=fee_label,
            )
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(line) for line in lines) + "\r\n"


def _ics_subset_key(kinds: frozenset[str]) -> str | None:
    mapping = {
        frozenset({"heilige", "feest", "vasten"}): "alles",
        frozenset({"heilige"}): "heiligen",
        frozenset({"feest"}): "feesten",
        frozenset({"vasten"}): "vasten",
        frozenset({"heilige", "feest"}): "heiligen-feesten",
        frozenset({"heilige", "vasten"}): "heiligen-vasten",
        frozenset({"feest", "vasten"}): "feesten-vasten",
    }
    return mapping.get(kinds)


def write_ics(entries: list[dict[str, Any]]) -> None:
    STATIC_ICS.mkdir(parents=True, exist_ok=True)
    combos = [
        frozenset({"heilige", "feest", "vasten"}),
        frozenset({"heilige"}),
        frozenset({"feest"}),
        frozenset({"vasten"}),
        frozenset({"heilige", "feest"}),
        frozenset({"heilige", "vasten"}),
        frozenset({"feest", "vasten"}),
    ]
    labels = {
        "alles": "Heiligenkalender (alles)",
        "heiligen": "Heiligen",
        "feesten": "Feesten (vast + paascyclus)",
        "vasten": "Vasten",
        "heiligen-feesten": "Heiligen + feesten",
        "heiligen-vasten": "Heiligen + vasten",
        "feesten-vasten": "Feesten + vasten",
    }
    for kinds in combos:
        key = _ics_subset_key(kinds)
        assert key
        subset = [e for e in entries if e["soort"] in kinds]
        for stijl, suffix in (("nieuw", "nieuw"), ("oud", "oud")):
            name = f"{labels[key]} — {suffix}"
            filename = f"{key}-{suffix}.ics"
            write_text(
                STATIC_ICS / filename,
                build_ics(
                    subset,
                    cal_name=name,
                    stijl=stijl,
                    context_entries=entries,
                ),
            )


def clean_generated() -> None:
    for rel in (
        "content/dag",
        "content/heiligen",
        "content/feesten",
        "content/vasten",
        "static/data/entries.json",
    ):
        path = SITE / rel
        if path.is_dir():
            shutil.rmtree(path)
        elif path.is_file():
            path.unlink()
    datum_dir = SITE / "content" / "datum"
    if datum_dir.is_dir():
        for path in datum_dir.iterdir():
            if path.name == "_index.md":
                continue
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
    for ics in (SITE / "static" / "ics").glob("*.ics"):
        ics.unlink()



def main() -> int:
    args = parse_args()
    if args.clean:
        clean_generated()
    entries = load_entries()
    ensure_hand_owned_indexes()
    ensure_achtergrond_topics()
    write_vasten_uitleg()
    write_generated_indexes()
    for entry in entries:
        write_entry_page(entry)
    write_entries_json(entries)
    write_ics(entries)
    print(f"Gegenereerd: {len(entries)} entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
