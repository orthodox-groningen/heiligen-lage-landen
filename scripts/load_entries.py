"""Laden en normaliseren van YAML-entries."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from kalender import normalize_dates, parse_mmdd

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / "data"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
ENTRY_SUBDIRS = ("feesten", "heiligen", "vasten")
NAMEN_PATH = DATA_ROOT / "namen.yaml"


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_namen_catalogus() -> dict[str, dict[str, Any]]:
    """Canonieke namen uit data/namen.yaml (entries + labels).

    ``entries`` wint bij laden over namen in individuele YAML-bestanden.
    """
    if not NAMEN_PATH.is_file():
        return {}
    raw = load_yaml(NAMEN_PATH) or {}
    entries = raw.get("entries") or {}
    if not isinstance(entries, dict):
        raise ValueError(f"{NAMEN_PATH}: 'entries' moet een mapping zijn")
    out: dict[str, dict[str, Any]] = {}
    for eid, val in entries.items():
        if not isinstance(val, dict) or not val.get("primair"):
            raise ValueError(f"{NAMEN_PATH}: entries.{eid}: primair ontbreekt")
        item = {"primair": str(val["primair"]).strip()}
        alts = val.get("alternatief") or []
        if alts:
            item["alternatief"] = [str(a).strip() for a in alts if str(a).strip()]
        out[str(eid)] = item
    return out


def load_namen_labels() -> dict[str, dict[str, Any]]:
    """Vrije labels (Boterweek e.d.) zonder eigen entry-bestand."""
    if not NAMEN_PATH.is_file():
        return {}
    raw = load_yaml(NAMEN_PATH) or {}
    labels = raw.get("labels") or {}
    if not isinstance(labels, dict):
        raise ValueError(f"{NAMEN_PATH}: 'labels' moet een mapping zijn")
    out: dict[str, dict[str, Any]] = {}
    for lid, val in labels.items():
        if not isinstance(val, dict) or not val.get("primair"):
            raise ValueError(f"{NAMEN_PATH}: labels.{lid}: primair ontbreekt")
        item = {"primair": str(val["primair"]).strip()}
        alts = val.get("alternatief") or []
        if alts:
            item["alternatief"] = [str(a).strip() for a in alts if str(a).strip()]
        out[str(lid)] = item
    return out


def load_bronnen() -> dict[str, dict[str, Any]]:
    path = DATA_ROOT / "bronnen" / "bronnen.yaml"
    raw = load_yaml(path) or {}
    items = raw.get("bronnen") or []
    out: dict[str, dict[str, Any]] = {}
    for item in items:
        bron_id = item["id"]
        out[bron_id] = item
    return out


def iter_entry_files() -> list[Path]:
    files: list[Path] = []
    for sub in ENTRY_SUBDIRS:
        folder = DATA_ROOT / sub
        if folder.is_dir():
            files.extend(sorted(folder.glob("*.yaml")))
    return files


def load_raw_entries() -> list[tuple[Path, dict[str, Any]]]:
    result: list[tuple[Path, dict[str, Any]]] = []
    for path in iter_entry_files():
        data = load_yaml(path)
        if not isinstance(data, dict):
            raise ValueError(f"{path}: root moet een mapping zijn")
        result.append((path, data))
    return result


def _resolve_referenties(
    entry: dict[str, Any],
    bronnen: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    refs = list(entry.get("referenties") or [])
    resolved: list[dict[str, Any]] = []
    for ref in refs:
        item = dict(ref)
        bron_id = item.get("bron_id")
        if bron_id:
            bron = bronnen.get(bron_id)
            if not bron:
                raise ValueError(f"Onbekende bron_id: {bron_id}")
            item.setdefault("label", bron.get("naam") or bron_id)
            if bron.get("url") and "url" not in item:
                item["url"] = bron["url"]
        resolved.append(item)
    return resolved


def _stijl(datum: dict[str, Any], path: Path) -> str:
    stijl = (datum.get("stijl") or "gregoriaans").strip().lower()
    if stijl not in {"gregoriaans", "juliaans"}:
        raise ValueError(f"{path}: onbekende stijl {stijl!r}")
    return stijl


def normalize_entry(
    path: Path,
    raw: dict[str, Any],
    bronnen: dict[str, dict[str, Any]],
    namen_catalogus: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    entry = dict(raw)
    entry_id = entry.get("id") or path.stem
    entry["id"] = entry_id
    if not ID_RE.match(entry_id):
        raise ValueError(f"{path}: ongeldige id {entry_id!r}")

    soort = entry.get("soort")
    if soort not in {"heilige", "feest", "vasten"}:
        raise ValueError(f"{path}: onbekende soort {soort!r}")

    datum = dict(entry.get("datum") or {})
    cyclus = entry.get("cyclus")
    if not cyclus:
        if datum.get("weekdagen"):
            cyclus = "wekelijks"
        elif datum.get("paascyclus"):
            cyclus = "paascyclus"
        else:
            cyclus = "jaar"
    entry["cyclus"] = cyclus
    paas = datum.get("paascyclus")
    weekdagen = datum.get("weekdagen")

    if weekdagen:
        if cyclus != "wekelijks":
            raise ValueError(f"{path}: datum.weekdagen vereist cyclus: wekelijks")
        days = sorted({int(d) for d in weekdagen})
        if any(d < 1 or d > 7 for d in days):
            raise ValueError(f"{path}: weekdagen moeten 1–7 (ISO) zijn")
        entry["datum_norm"] = {
            "stijl": _stijl(datum, path),
            "feestdatum": None,
            "weekdagen": days,
            "vorm": "weekdagen",
        }
        entry["datum_extra_norm"] = []
    elif paas:
        if cyclus != "paascyclus":
            raise ValueError(f"{path}: datum.paascyclus vereist cyclus: paascyclus")
        anker = paas.get("anker") or "pascha"
        if anker != "pascha":
            raise ValueError(f"{path}: alleen anker 'pascha' wordt ondersteund")
        stijl = _stijl(datum, path)
        if "offset_dagen" in paas:
            offset = int(paas["offset_dagen"])
            entry["datum_norm"] = {
                "stijl": stijl,
                "feestdatum": None,
                "paascyclus_offset": offset,
                "paascyclus_anker": anker,
                "vorm": "dag",
            }
        elif "van_offset_dagen" in paas:
            van_o = int(paas["van_offset_dagen"])
            if "tot_offset_dagen" in paas:
                tot_o = int(paas["tot_offset_dagen"])
                entry["datum_norm"] = {
                    "stijl": stijl,
                    "feestdatum": None,
                    "paascyclus_offset": van_o,
                    "paascyclus_anker": anker,
                    "van_offset_dagen": van_o,
                    "tot_offset_dagen": tot_o,
                    "vorm": "periode",
                }
            elif datum.get("tot"):
                parse_mmdd(datum["tot"])
                entry["datum_norm"] = {
                    "stijl": stijl,
                    "feestdatum": None,
                    "paascyclus_offset": van_o,
                    "paascyclus_anker": anker,
                    "van_offset_dagen": van_o,
                    "tot_mmdd": datum["tot"],
                    "vorm": "periode_hybride",
                }
            else:
                raise ValueError(
                    f"{path}: paascyclus.van_offset_dagen vereist "
                    "tot_offset_dagen of datum.tot"
                )
        else:
            raise ValueError(f"{path}: paascyclus zonder bruikbare offsets")
        entry["datum_extra_norm"] = []
    elif datum.get("van") and datum.get("tot"):
        if cyclus not in {"jaar", "wekelijks"}:
            # vaste jaarcyclus-periode
            pass
        parse_mmdd(datum["van"])
        parse_mmdd(datum["tot"])
        entry["datum_norm"] = {
            "stijl": _stijl(datum, path),
            "feestdatum": datum["van"],
            "van": datum["van"],
            "tot": datum["tot"],
            "vorm": "periode",
        }
        entry["datum_extra_norm"] = []
    else:
        if "waarde" not in datum:
            raise ValueError(f"{path}: datum.waarde ontbreekt")
        stijl = datum.get("stijl") or "gregoriaans"
        dates = normalize_dates(datum["waarde"], stijl)
        if datum.get("gregoriaans"):
            parse_mmdd(datum["gregoriaans"])
            dates["gregoriaans"] = datum["gregoriaans"]
        if datum.get("juliaans"):
            parse_mmdd(datum["juliaans"])
            dates["juliaans"] = datum["juliaans"]
        dates["vorm"] = "dag"
        entry["datum_norm"] = dates

        extra_norm: list[dict[str, Any]] = []
        for extra in datum.get("extra") or []:
            e_stijl = extra.get("stijl") or stijl
            e_dates = normalize_dates(extra["waarde"], e_stijl)
            extra_norm.append(
                {
                    **e_dates,
                    "toelichting": extra.get("toelichting") or "",
                }
            )
        entry["datum_extra_norm"] = extra_norm

    entry["referenties"] = _resolve_referenties(entry, bronnen)
    entry["status"] = entry.get("status") or "stub"
    entry["lagenlanden"] = bool(
        entry.get("lagenlanden", entry.get("soort") == "heilige")
    )
    entry["observances"] = list(entry.get("observances") or [])
    if not entry["observances"]:
        if entry["soort"] == "heilige":
            entry["observances"] = ["heilige"]
        elif entry["soort"] == "vasten":
            entry["observances"] = ["vasten"]
        else:
            entry["observances"] = ["feest"]
    entry["onderdrukt_wekelijks_vasten"] = bool(
        entry.get("onderdrukt_wekelijks_vasten")
    )
    niveau = entry.get("vastenniveau")
    if niveau is not None:
        allowed = {"streng", "wijn_olie", "vis", "lichter", "vrij"}
        if niveau not in allowed:
            raise ValueError(f"{path}: onbekend vastenniveau {niveau!r}")
        entry["vastenniveau"] = niveau
        if niveau == "vrij":
            entry["onderdrukt_wekelijks_vasten"] = True
    entry["source_path"] = str(path.relative_to(REPO_ROOT)).replace("\\", "/")

    file_namen = dict(entry.get("namen") or {})
    catalog = (namen_catalogus or {}).get(entry_id)
    if catalog:
        entry["namen"] = {
            "primair": catalog["primair"],
            "alternatief": list(catalog.get("alternatief") or []),
        }
    else:
        entry["namen"] = file_namen
    if "primair" not in entry["namen"]:
        raise ValueError(
            f"{path}: namen.primair ontbreekt "
            f"(zet in het YAML-bestand of in data/namen.yaml)"
        )
    return entry


def _sort_key(entry: dict[str, Any]) -> tuple:
    dn = entry["datum_norm"]
    vorm = dn.get("vorm") or "dag"
    if entry.get("cyclus") == "wekelijks":
        return (2, tuple(dn.get("weekdagen") or []), entry["id"])
    if entry.get("cyclus") == "paascyclus":
        return (1, dn.get("paascyclus_offset") or 0, entry["id"])
    if vorm == "periode":
        return (0, dn.get("van") or dn.get("feestdatum") or "", entry["id"])
    return (0, dn.get("feestdatum") or "", entry["id"])


def load_entries() -> list[dict[str, Any]]:
    bronnen = load_bronnen()
    namen_catalogus = load_namen_catalogus()
    entries = [
        normalize_entry(path, raw, bronnen, namen_catalogus)
        for path, raw in load_raw_entries()
    ]
    ids = [e["id"] for e in entries]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"Dubbele id's: {sorted(dupes)}")
    return sorted(entries, key=_sort_key)
