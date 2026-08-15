"""Laden en normaliseren van YAML-entries."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from kalender import normalize_dates

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / "data"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


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
    for sub in ("feesten", "heiligen"):
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


def normalize_entry(
    path: Path,
    raw: dict[str, Any],
    bronnen: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    entry = dict(raw)
    entry_id = entry.get("id") or path.stem
    entry["id"] = entry_id
    if not ID_RE.match(entry_id):
        raise ValueError(f"{path}: ongeldige id {entry_id!r}")

    datum = dict(entry.get("datum") or {})
    if "waarde" not in datum:
        raise ValueError(f"{path}: datum.waarde ontbreekt")
    stijl = datum.get("stijl") or "gregoriaans"
    dates = normalize_dates(datum["waarde"], stijl)
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
    entry["lagenlanden"] = bool(entry.get("lagenlanden", entry.get("soort") == "heilige"))
    entry["cyclus"] = entry.get("cyclus") or "jaar"
    entry["source_path"] = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    entry["namen"] = dict(entry.get("namen") or {})
    if "primair" not in entry["namen"]:
        raise ValueError(f"{path}: namen.primair ontbreekt")
    return entry


def load_entries() -> list[dict[str, Any]]:
    bronnen = load_bronnen()
    entries = [
        normalize_entry(path, raw, bronnen) for path, raw in load_raw_entries()
    ]
    ids = [e["id"] for e in entries]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"Dubbele id's: {sorted(dupes)}")
    return sorted(entries, key=lambda e: (e["datum_norm"]["feestdatum"], e["id"]))
