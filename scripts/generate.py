"""Genereer Hugo-content, entries.json en ICS-feeds."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import uuid
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from load_entries import load_entries  # noqa: E402
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


def entry_permalink(entry: dict[str, Any]) -> str:
    kind = "feesten" if entry["soort"] == "feest" else "heiligen"
    # Leading slash: Hugo canonifyURLs zet baseURL-prefix voor Pages.
    return f"/{kind}/{entry['id']}/"


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


def write_entry_page(entry: dict[str, Any]) -> None:
    kind = "feesten" if entry["soort"] == "feest" else "heiligen"
    title = entry["namen"]["primair"]
    feestdatum = entry["datum_norm"].get("feestdatum")
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
    if feestdatum:
        fm.append(f"feestdatum: {feestdatum}")
    if entry.get("cyclus") == "paascyclus":
        fm.append(f"paascyclus_offset: {entry['datum_norm']['paascyclus_offset']}")
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
    if entry.get("cyclus") == "paascyclus":
        offset = entry["datum_norm"]["paascyclus_offset"]
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
    else:
        assert feestdatum
        body.append(
            f"**Feestdag:** {mmdd_label(feestdatum)} "
            f"(zelfde datum in de nieuwe/Gregoriaanse én de oude/Juliaanse kalender)"
        )
        dn = entry["datum_norm"]
        if dn.get("gregoriaans") or dn.get("juliaans"):
            parts = []
            if dn.get("gregoriaans"):
                parts.append(f"Gregoriaans {mmdd_label(dn['gregoriaans'])}")
            if dn.get("juliaans"):
                parts.append(f"Juliaans {mmdd_label(dn['juliaans'])}")
            body.append("")
            body.append("**Expliciete notatie:** " + "; ".join(parts))
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
    if feestdatum:
        body.append(f"[Datumpagina {mmdd_label(feestdatum)}](/datum/{feestdatum}/)")
        body.append("")
    write_text(CONTENT / kind / f"{entry['id']}.md", "\n".join(fm + ["", *body]))


def write_date_pages(entries: list[dict[str, Any]]) -> None:
    years = list(occurrence_years())
    by_date: dict[str, list[tuple[dict[str, Any], int | None]]] = defaultdict(list)
    for entry in entries:
        if entry.get("cyclus") == "paascyclus":
            offset = entry["datum_norm"]["paascyclus_offset"]
            for y in years:
                mmdd = mmdd_from_date(pascha_offset_date(y, offset))
                by_date[mmdd].append((entry, y))
            continue
        feestdatum = entry["datum_norm"]["feestdatum"]
        by_date[feestdatum].append((entry, None))
        for extra in entry.get("datum_extra_norm") or []:
            by_date[extra["feestdatum"]].append((entry, None))

    for mmdd, items in sorted(by_date.items()):
        # Vaste entries eerst (uniek), daarna paascyclus gegroepeerd per id.
        fixed: list[dict[str, Any]] = []
        movable: dict[str, dict[str, Any]] = {}
        movable_years: dict[str, list[int]] = defaultdict(list)
        seen_fixed: set[str] = set()
        for entry, year in items:
            if year is None:
                if entry["id"] in seen_fixed:
                    continue
                seen_fixed.add(entry["id"])
                fixed.append(entry)
            else:
                movable[entry["id"]] = entry
                movable_years[entry["id"]].append(year)

        title = f"{mmdd_label(mmdd)}"
        lines = [
            "---",
            f"title: {yaml_quote(title)}",
            f"feestdatum: {mmdd}",
            "type: datum",
            "---",
            "",
            "Dit is een **datumpagina**: feesten en heiligen waarvan de feestdag "
            f"**{mmdd_label(mmdd)}** is — in de nieuwe (Gregoriaanse) én de oude "
            "(Juliaanse) kalender dezelfde dagnaam — plus paascyclus-dagen die in "
            f"bepaalde jaren ({years[0]}–{years[-1]}) op deze wereldlijke datum vallen.",
            "",
        ]
        if not fixed and not movable:
            lines.append("_Geen feesten of heiligen op deze datum._")
        for entry in fixed:
            link = entry_permalink(entry)
            kind_label = "Feest" if entry["soort"] == "feest" else "Heilige"
            lines.append(f"- **[{entry['namen']['primair']}]({link})** ({kind_label})")
            if entry.get("samenvatting"):
                lines.append(f"  {entry['samenvatting'].strip().splitlines()[0]}")
        for eid, entry in sorted(movable.items(), key=lambda kv: kv[1]["namen"]["primair"]):
            link = entry_permalink(entry)
            ys = ", ".join(str(y) for y in sorted(movable_years[eid]))
            lines.append(
                f"- **[{entry['namen']['primair']}]({link})** (paascyclus; in {ys})"
            )
            if entry.get("samenvatting"):
                lines.append(f"  {entry['samenvatting'].strip().splitlines()[0]}")
        lines.append("")
        write_text(CONTENT / "datum" / f"{mmdd}.md", "\n".join(lines))


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
        CONTENT / "datum" / "_index.md",
        """---
title: "Datums"
---

Datumpagina's: alle feesten en heiligen op een kalenderdatum (MM-DD).
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
            "path": CONTENT / "overzicht" / "_index.md",
            "title": "Overzicht",
            "layout": "overzicht",
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
        "description": "Hoe we vandaag rekenen op de nieuwe of oude kalender",
    },
    {
        "id": "feestdatum",
        "title": "Feestdatum",
        "description": "Wat een vaste feestdatum wel en niet betekent",
    },
    {
        "id": "datumpagina",
        "title": "Datumpagina’s",
        "description": "Bladeren via de jaarkalender naar een willekeurige dag",
    },
    {
        "id": "kleuren",
        "title": "Kleuren in de jaarkalender",
        "description": "Legenda van de kleuren op de jaarkalender",
    },
    {
        "id": "agenda",
        "title": "Agenda (ICS)",
        "description": "Abonneren op heiligen- en feestfeeds in nieuw of oud",
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


def write_entries_json(entries: list[dict[str, Any]]) -> None:
    years = list(occurrence_years())
    payload = []
    for entry in entries:
        item: dict[str, Any] = {
            "id": entry["id"],
            "soort": entry["soort"],
            "cyclus": entry.get("cyclus") or "jaar",
            "naam": entry["namen"]["primair"],
            "alternatief": entry["namen"].get("alternatief") or [],
            "titels": entry.get("titels") or [],
            "samenvatting": (entry.get("samenvatting") or "").strip(),
            "url": entry_permalink(entry),
            "lagenlanden": bool(entry.get("lagenlanden")),
            "status": entry.get("status") or "stub",
            "observances": entry.get("observances") or [],
            "icoon": (entry.get("icoon") or {}).get("bestand")
            if (entry.get("icoon") or {}).get("rechten") == "ok"
            else None,
        }
        if entry.get("cyclus") == "paascyclus":
            offset = entry["datum_norm"]["paascyclus_offset"]
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
            feestdatum = entry["datum_norm"]["feestdatum"]
            item["feestdatum"] = feestdatum
            item["feestdatum_juliaans"] = entry["datum_norm"].get("juliaans")
            item["feestdatum_gregoriaans"] = entry["datum_norm"].get("gregoriaans")
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
) -> str:
    """Bouw ICS voor jaren huidig−2 … +25.

    ``nieuw``: vaste feesten op de feestdatum (wereldlijk = dagnaam);
    paascyclus op de berekende Orthodoxe (wereldlijke) datum.
    ``oud``: vaste feesten op Juliaanse feestdatum→wereldlijke vierdatum
    (offset 13/14 jaargevoelig); paascyclus ongewijzigd (zelfde Orthodoxe datum).
    """
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    years = list(occurrence_years())
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//orthodox-groningen//heiligen-lage-landen//NL",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_ics_escape(cal_name)}",
        "X-WR-TIMEZONE:UTC",
    ]
    for entry in entries:
        for year in years:
            if entry.get("cyclus") == "paascyclus":
                civil = pascha_offset_date(year, entry["datum_norm"]["paascyclus_offset"])
                summary = entry["namen"]["primair"]
                if stijl == "oud":
                    summary = f"{summary} (Orthodoxe paascyclus)"
                uid_key = f"{entry['id']}:{stijl}:{year}:paas"
                fee_label = mmdd_label(mmdd_from_date(civil))
            else:
                feestdatum = entry["datum_norm"]["feestdatum"]
                if stijl == "oud":
                    civil = julian_feast_to_civil_date(year, feestdatum)
                    summary = (
                        f"{entry['namen']['primair']} "
                        f"({mmdd_label(feestdatum)} Juliaans)"
                    )
                    uid_key = f"{entry['id']}:oud:{year}:{feestdatum}"
                    fee_label = mmdd_label(feestdatum)
                else:
                    month, day = parse_mmdd(feestdatum)
                    civil = date(year, month, day)
                    summary = entry["namen"]["primair"]
                    uid_key = f"{entry['id']}:nieuw:{year}:{feestdatum}"
                    fee_label = mmdd_label(feestdatum)
            dt_start = civil.strftime("%Y%m%d")
            dt_end_s = (civil + timedelta(days=1)).strftime("%Y%m%d")
            uid = str(uuid.uuid5(uuid.NAMESPACE_URL, uid_key))
            desc_parts = []
            if entry.get("samenvatting"):
                desc_parts.append(entry["samenvatting"].strip())
            if entry.get("cyclus") == "paascyclus":
                desc_parts.append(f"Wereldlijke datum: {fee_label} {year}")
            else:
                desc_parts.append(f"Feestdatum: {fee_label}")
                if stijl == "oud":
                    desc_parts.append(
                        f"In westerse agenda's: {mmdd_label(mmdd_from_date(civil))} {year} "
                        "(Juliaanse feestdatum omgezet; offset 13 tot 2100, daarna 14)."
                    )
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
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(line) for line in lines) + "\r\n"


def write_ics(entries: list[dict[str, Any]]) -> None:
    STATIC_ICS.mkdir(parents=True, exist_ok=True)
    subsets = {
        "alles": entries,
        "heiligen": [e for e in entries if e["soort"] == "heilige"],
        "feesten": [e for e in entries if e["soort"] == "feest"],
    }
    labels = {
        "alles": "Heiligenkalender (alles)",
        "heiligen": "Heiligen",
        "feesten": "Feesten (vast + paascyclus)",
    }
    for key, subset in subsets.items():
        for stijl, suffix in (("nieuw", "nieuw"), ("oud", "oud")):
            name = f"{labels[key]} — {suffix}"
            filename = f"{key}-{suffix}.ics"
            write_text(
                STATIC_ICS / filename,
                build_ics(subset, cal_name=name, stijl=stijl),
            )


def clean_generated() -> None:
    for rel in (
        "content/dag",
        "content/datum",
        "content/heiligen",
        "content/feesten",
        "static/data/entries.json",
    ):
        path = SITE / rel
        if path.is_dir():
            shutil.rmtree(path)
        elif path.is_file():
            path.unlink()
    for ics in (SITE / "static" / "ics").glob("*.ics"):
        ics.unlink()


def main() -> int:
    args = parse_args()
    if args.clean:
        clean_generated()
    entries = load_entries()
    ensure_hand_owned_indexes()
    ensure_achtergrond_topics()
    write_generated_indexes()
    for entry in entries:
        write_entry_page(entry)
    write_date_pages(entries)
    write_entries_json(entries)
    write_ics(entries)
    print(f"Gegenereerd: {len(entries)} entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
