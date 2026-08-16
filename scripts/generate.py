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
from kalender import format_mmdd, julian_to_civil_mmdd, parse_mmdd  # noqa: E402

SITE = ROOT / "site"
CONTENT = SITE / "content"
STATIC_DATA = SITE / "static" / "data"
STATIC_ICS = SITE / "static" / "ics"

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
    feestdatum = entry["datum_norm"]["feestdatum"]
    fm = [
        "---",
        f"title: {yaml_quote(title)}",
        f"slug: {entry['id']}",
        f"type: {entry['soort']}",
        f"soort: {entry['soort']}",
        f"entry_id: {entry['id']}",
        f"feestdatum: {feestdatum}",
        f"status: {entry.get('status', 'stub')}",
        f"lagenlanden: {'true' if entry.get('lagenlanden') else 'false'}",
        f"source_path: {yaml_quote(entry['source_path'])}",
    ]
    if entry.get("titels"):
        fm.append("titels:")
        for t in entry["titels"]:
            fm.append(f"  - {yaml_quote(t)}")
    icoon = entry.get("icoon") or {}
    if icoon.get("bestand") and icoon.get("rechten") == "ok":
        fm.append(f"icoon: {yaml_quote('/' + icoon['bestand'].lstrip('/'))}")
    fm.append("---")

    body: list[str] = []
    if entry.get("titels"):
        body.append("*" + " · ".join(entry["titels"]) + "*")
        body.append("")
    body.append(
        f"**Feestdag:** {mmdd_label(feestdatum)} "
        f"(zelfde datum in de nieuwe/Gregoriaanse én de oude/Juliaanse kalender)"
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
    body.append(f"[Datumpagina {mmdd_label(feestdatum)}](/datum/{feestdatum}/)")
    body.append("")
    write_text(CONTENT / kind / f"{entry['id']}.md", "\n".join(fm + ["", *body]))


def write_date_pages(entries: list[dict[str, Any]]) -> None:
    by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        by_date[entry["datum_norm"]["feestdatum"]].append(entry)
        for extra in entry.get("datum_extra_norm") or []:
            by_date[extra["feestdatum"]].append(entry)

    for mmdd, items in sorted(by_date.items()):
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for item in items:
            if item["id"] in seen:
                continue
            seen.add(item["id"])
            unique.append(item)
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
            "(Juliaanse) kalender dezelfde dagnaam.",
            "",
        ]
        if not unique:
            lines.append("_Geen feesten of heiligen op deze datum._")
        for entry in unique:
            link = entry_permalink(entry)
            kind_label = "Feest" if entry["soort"] == "feest" else "Heilige"
            lines.append(f"- **[{entry['namen']['primair']}]({link})** ({kind_label})")
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

Grote vaste feesten van de jaarcyclus (zonder paascyclus in deze MVP).
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
            "title": "Uitleg: datums en kalenders",
            "layout": "uitleg",
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
        if expected_layout is not None and meta.get("layout") != expected_layout:
            meta["layout"] = expected_layout
            write_text(path, _dump_hugo_markdown(meta, body))
            print(f"Layout hersteld naar {expected_layout!r}: {_rel(path)}")


def write_entries_json(entries: list[dict[str, Any]]) -> None:
    payload = []
    for entry in entries:
        payload.append(
            {
                "id": entry["id"],
                "soort": entry["soort"],
                "naam": entry["namen"]["primair"],
                "titels": entry.get("titels") or [],
                "samenvatting": (entry.get("samenvatting") or "").strip(),
                "url": entry_permalink(entry),
                "feestdatum": entry["datum_norm"]["feestdatum"],
                "lagenlanden": bool(entry.get("lagenlanden")),
                "status": entry.get("status") or "stub",
                "icoon": (entry.get("icoon") or {}).get("bestand")
                if (entry.get("icoon") or {}).get("rechten") == "ok"
                else None,
            }
        )
    write_text(STATIC_DATA / "entries.json", json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


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
    """Bouw ICS.

    ``stijl=nieuw``: DTSTART op de feestdatum (burgerlijk gelijk aan feestdag-naam).
    ``stijl=oud``: DTSTART op feestdatum+13 (vierdatum in westerse agenda's);
    SUMMARY bevat de Juliaanse feestdatum.
    """
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
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
        feestdatum = entry["datum_norm"]["feestdatum"]
        if stijl == "oud":
            civil = julian_to_civil_mmdd(feestdatum)
            month, day = parse_mmdd(civil)
            summary = f"{entry['namen']['primair']} ({mmdd_label(feestdatum)} Juliaans)"
            uid_key = f"{entry['id']}:oud:{feestdatum}"
        else:
            month, day = parse_mmdd(feestdatum)
            summary = entry["namen"]["primair"]
            uid_key = f"{entry['id']}:nieuw:{feestdatum}"
        anchor = date(2001, month, day)
        dt_start = anchor.strftime("%Y%m%d")
        dt_end_s = (anchor + timedelta(days=1)).strftime("%Y%m%d")
        uid = str(uuid.uuid5(uuid.NAMESPACE_URL, uid_key))
        desc_parts = []
        if entry.get("samenvatting"):
            desc_parts.append(entry["samenvatting"].strip())
        desc_parts.append(f"Feestdatum: {mmdd_label(feestdatum)}")
        if stijl == "oud":
            desc_parts.append(
                f"In westerse (burgerlijke) agenda's: {mmdd_label(format_mmdd(month, day))} "
                "(oude kalender +13 dagen tot 2100)."
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
            "RRULE:FREQ=YEARLY",
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
        "feesten": "Vaste feesten",
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
