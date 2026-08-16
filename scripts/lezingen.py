"""Resolutie van Apostel- en Evangelielezingen (Moskou / ROCOR-fallback).

Normatieve regels: docs/specs/lezingen.md
Data: data/lezingen/
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from kalender import (
    gregorian_to_julian_calendar,
    mmdd_from_date,
    parse_mmdd,
    pascha_offset_date,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "docs" / "specs" / "lezingen.md"
DATA_DIR = REPO_ROOT / "data" / "lezingen"
VOORBEELD_FENCE = re.compile(
    r"```lezingen-voorbeeld\s*\n(.*?)```",
    re.DOTALL,
)


@dataclass
class LezingRef:
    ref: str
    zacalo: int | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"ref": self.ref}
        if self.zacalo is not None:
            out["zacalo"] = self.zacalo
        return out


@dataclass
class LezingenResultaat:
    apostel: list[LezingRef] = field(default_factory=list)
    evangelie: list[LezingRef] = field(default_factory=list)
    regels: list[str] = field(default_factory=list)
    override_id: str | None = None
    toelichting: str = ""
    status: str = "onbekend"  # gevonden | onbekend | pending

    def as_dict(self) -> dict[str, Any]:
        return {
            "apostel": [a.as_dict() for a in self.apostel],
            "evangelie": [e.as_dict() for e in self.evangelie],
            "regels": list(self.regels),
            "override_id": self.override_id,
            "toelichting": self.toelichting,
            "status": self.status,
        }


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_overrides() -> list[dict[str, Any]]:
    path = DATA_DIR / "feest-overrides.yaml"
    if not path.is_file():
        return []
    raw = load_yaml(path) or {}
    return list(raw.get("overrides") or [])


def _refs(items: list[dict[str, Any]] | None) -> list[LezingRef]:
    out: list[LezingRef] = []
    for item in items or []:
        out.append(
            LezingRef(
                ref=str(item["ref"]).strip(),
                zacalo=item.get("zacalo"),
            )
        )
    return out


def _mmdd_for_offset(year: int, offset: int, stijl: str) -> str:
    civil = pascha_offset_date(year, offset)
    if stijl == "oud":
        _jy, jm, jd = gregorian_to_julian_calendar(civil)
        return f"{jm:02d}-{jd:02d}"
    return mmdd_from_date(civil)


def resolve_lezingen(
    jaar: int,
    mmdd: str,
    stijl: str = "nieuw",
    *,
    overrides: list[dict[str, Any]] | None = None,
) -> LezingenResultaat:
    """Bepaal lezingen voor een kalenderdag.

    ``stijl``: ``nieuw`` (Gregoriaanse/wereldlijke MM-DD voor paascyclus) of
    ``oud`` (Juliaanse dagnaam voor paascyclus). Vaste MM-DD-overrides matchen
    altijd op de feestdatum-dagnaam.
    """
    parse_mmdd(mmdd)
    if stijl not in {"nieuw", "oud"}:
        raise ValueError(f"onbekende stijl {stijl!r}")

    for ov in overrides if overrides is not None else load_overrides():
        match = ov.get("match") or {}
        hit = False
        if "paascyclus_offset" in match:
            want = _mmdd_for_offset(jaar, int(match["paascyclus_offset"]), stijl)
            hit = want == mmdd
        elif "mmdd" in match:
            hit = match["mmdd"] == mmdd
        if not hit:
            continue
        regels = [str(r) for r in (ov.get("regels") or ["R2"])]
        return LezingenResultaat(
            apostel=_refs(ov.get("apostel")),
            evangelie=_refs(ov.get("evangelie")),
            regels=regels,
            override_id=str(ov.get("id") or ""),
            toelichting="+".join(regels),
            status="gevonden",
        )

    return LezingenResultaat(
        status="onbekend",
        toelichting="Geen override; weekreeks (R3) nog niet geïmplementeerd.",
        regels=[],
    )


def parse_spec_voorbeelden(text: str | None = None) -> list[dict[str, Any]]:
    """Parse ```lezingen-voorbeeld```-blokken uit de normatieve spec."""
    if text is None:
        text = SPEC_PATH.read_text(encoding="utf-8")
    out: list[dict[str, Any]] = []
    for block in VOORBEELD_FENCE.findall(text):
        data = yaml.safe_load(block)
        if not isinstance(data, dict):
            raise ValueError("lezingen-voorbeeld moet een YAML-mapping zijn")
        if "id" not in data or "status" not in data:
            raise ValueError("lezingen-voorbeeld vereist id en status")
        out.append(data)
    return out


def spec_body_for_uitleg(text: str | None = None) -> str:
    """Spec-inhoud zonder de machine-leesbare voorbeeldsectie (die blijft in docs)."""
    if text is None:
        text = SPEC_PATH.read_text(encoding="utf-8")
    marker = "## Machine-leesbare voorbeelden"
    idx = text.find(marker)
    if idx < 0:
        body = text
    else:
        body = text[:idx].rstrip() + "\n"
    # Strip H1 (Hugo page heeft eigen title)
    lines = body.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
        if lines and lines[0].strip() == "":
            lines = lines[1:]
    return "\n".join(lines).rstrip() + "\n"


def resultaat_matches_verwacht(
    result: LezingenResultaat,
    verwacht: dict[str, Any],
) -> list[str]:
    """Return list of mismatch messages (empty = ok)."""
    errors: list[str] = []
    exp_a = [str(x["ref"]) for x in (verwacht.get("apostel") or [])]
    exp_e = [str(x["ref"]) for x in (verwacht.get("evangelie") or [])]
    got_a = [a.ref for a in result.apostel]
    got_e = [e.ref for e in result.evangelie]
    if got_a != exp_a:
        errors.append(f"apostel: got {got_a!r}, expected {exp_a!r}")
    if got_e != exp_e:
        errors.append(f"evangelie: got {got_e!r}, expected {exp_e!r}")
    exp_r = [str(r) for r in (verwacht.get("regels") or [])]
    if exp_r and list(result.regels) != exp_r:
        errors.append(f"regels: got {result.regels!r}, expected {exp_r!r}")
    return errors
