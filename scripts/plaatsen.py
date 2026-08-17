"""Laden van data/plaatsen.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PLAATSEN_PATH = REPO_ROOT / "data" / "plaatsen.yaml"
ID_RE = __import__("re").compile(r"^[a-z0-9][a-z0-9_-]*$")


_PLAATSEN_CACHE: dict[str, dict[str, Any]] | None = None


def load_plaatsen() -> dict[str, dict[str, Any]]:
    """id → plaatsrecord. Volgorde van het YAML-bestand."""
    global _PLAATSEN_CACHE
    if _PLAATSEN_CACHE is not None:
        return _PLAATSEN_CACHE
    raw = yaml.safe_load(PLAATSEN_PATH.read_text(encoding="utf-8")) or {}
    items = raw.get("plaatsen") or []
    out: dict[str, dict[str, Any]] = {}
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"{PLAATSEN_PATH}: plaatsen[{i}] is geen mapping")
        pid = str(item.get("id") or "").strip()
        if not pid or not ID_RE.fullmatch(pid):
            raise ValueError(f"{PLAATSEN_PATH}: plaatsen[{i}]: ongeldig id")
        if pid in out:
            raise ValueError(f"{PLAATSEN_PATH}: dubbele plaats-id {pid!r}")
        naam = str(item.get("naam") or "").strip()
        if not naam:
            raise ValueError(f"{PLAATSEN_PATH}: {pid}: naam ontbreekt")
        try:
            lat = float(item["lat"])
            lon = float(item["lon"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{PLAATSEN_PATH}: {pid}: lat/lon ontbreekt") from exc
        soort = str(item.get("soort") or "plaats").strip()
        if soort not in {"plaats", "streek"}:
            raise ValueError(f"{PLAATSEN_PATH}: {pid}: onbekende soort {soort!r}")
        alts = [str(a).strip() for a in (item.get("alternatief") or []) if str(a).strip()]
        streek = str(item.get("streek") or "").strip()
        rec: dict[str, Any] = {
            "id": pid,
            "naam": naam,
            "alternatief": alts,
            "lat": lat,
            "lon": lon,
            "soort": soort,
        }
        if streek:
            rec["streek"] = streek
        out[pid] = rec
    for rec in out.values():
        streek = rec.get("streek")
        if streek and streek not in out:
            raise ValueError(
                f"{PLAATSEN_PATH}: {rec['id']}: onbekende streek {streek!r}"
            )
        if streek and out[streek].get("soort") != "streek":
            raise ValueError(
                f"{PLAATSEN_PATH}: {rec['id']}: streek {streek!r} is geen streek"
            )
    _PLAATSEN_CACHE = out
    return out


def plaats_zoektekst(plaats: dict[str, Any], by_id: dict[str, dict[str, Any]]) -> str:
    parts = [plaats["naam"], plaats["id"], *(plaats.get("alternatief") or [])]
    streek_id = plaats.get("streek")
    if streek_id and streek_id in by_id:
        streek = by_id[streek_id]
        parts.extend(
            [streek["naam"], streek["id"], *(streek.get("alternatief") or [])]
        )
    return " ".join(parts)


def locatie_namen(
    ids: list[str], by_id: dict[str, dict[str, Any]]
) -> list[str]:
    namen: list[str] = []
    for pid in ids:
        rec = by_id.get(pid)
        namen.append(rec["naam"] if rec else pid)
    return namen


def locatie_zoektekst(
    ids: list[str], by_id: dict[str, dict[str, Any]]
) -> str:
    chunks = [plaats_zoektekst(by_id[pid], by_id) for pid in ids if pid in by_id]
    return " ".join(chunks)
