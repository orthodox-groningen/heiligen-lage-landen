"""Effectief vastenniveau voor één kalenderdag.

Spiegel de rangorde en mengregel in ``site/assets/js/calendar.js``
(``mixVastenniveau``). Wijzigingen hier óók daar doorvoeren.

Rang (strenger → soepeler): streng < wijn_olie < vis < lichter < vrij.
``lichter`` is een seizoenslabel; bij vergelijking telt het als ``wijn_olie``,
zodat een feest met ``vis`` een lichte vastenperiode wél versoepelt.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

NIVEAU_RANK = {
    "streng": 0,
    "wijn_olie": 1,
    "vis": 2,
    "lichter": 3,
    "vrij": 4,
}

# lichter ≈ wijn_olie als dagbasis, zodat vis een echte versoepeling is.
COMPARE_RANK = {
    "streng": 0,
    "wijn_olie": 1,
    "lichter": 1,
    "vis": 2,
    "vrij": 3,
}

NIVEAU_LABELS = {
    "streng": "streng",
    "wijn_olie": "wijn en olie",
    "vis": "vis",
    "lichter": "lichter",
    "vrij": "vastenvrij",
}

GROTE_WEEK_ID = "grote-week"


def _naam(entry: dict[str, Any]) -> str:
    if entry.get("naam"):
        return str(entry["naam"])
    namen = entry.get("namen") or {}
    if namen.get("primair"):
        return str(namen["primair"])
    return str(entry.get("id") or "")


def _vorm(entry: dict[str, Any]) -> str:
    if entry.get("vorm"):
        return str(entry["vorm"])
    dn = entry.get("datum_norm") or {}
    return str(dn.get("vorm") or "dag")


def is_weekly_entry(entry: dict[str, Any]) -> bool:
    return _vorm(entry) == "weekdagen"


def is_period_entry(entry: dict[str, Any]) -> bool:
    vorm = _vorm(entry)
    if vorm in {"periode", "periode_hybride"}:
        return True
    if entry.get("van") and entry.get("tot"):
        return True
    if entry.get("period_occurrences"):
        return True
    return False


def _observances(entry: dict[str, Any]) -> list[str]:
    obs = entry.get("observances")
    if obs:
        return list(obs)
    soort = entry.get("soort")
    if soort == "heilige":
        return ["heilige"]
    if soort == "vasten":
        return ["vasten"]
    return ["feest"]


def _more_lenient(a: str, b: str) -> str:
    return a if COMPARE_RANK[a] >= COMPARE_RANK[b] else b


def _stricter(a: str, b: str) -> str:
    return a if COMPARE_RANK[a] <= COMPARE_RANK[b] else b


@dataclass(frozen=True)
class VastenIndicatie:
    niveau: str
    tekst: str
    periode_id: str | None = None
    versoepeld_door_id: str | None = None
    weekend: bool = False


def _tekst(
    *,
    niveau: str,
    bron: str,
    versoepeld_door: str | None = None,
    weekend: bool = False,
    weekday: int | None = None,
) -> str:
    if niveau == "vrij":
        return f"Vastenvrij — {bron}"
    label = NIVEAU_LABELS.get(niveau, niveau)
    line = f"Vasten: {label} — {bron}"
    if versoepeld_door:
        line += f", versoepeld ({versoepeld_door})"
    elif weekend and weekday == 6:
        line += " (zaterdag)"
    elif weekend and weekday == 7:
        line += " (zondag)"
    return line


def mix_vastenniveau(
    day_entries: list[dict[str, Any]],
    weekday: int,
) -> VastenIndicatie | None:
    """Bepaal het geldende vastenniveau voor de entries van één dag.

    ``weekday`` is ISO: 1=maandag … 7=zondag.
    ``day_entries`` zijn de entries die die dag raken (wekelijks al
    weggelaten als een periode het onderdrukt).
    """
    periods = [
        e
        for e in day_entries
        if is_period_entry(e)
        and not is_weekly_entry(e)
        and (e.get("soort") == "vasten" or e.get("vastenniveau"))
    ]
    weekly = [e for e in day_entries if is_weekly_entry(e)]
    day_feasts = [
        e
        for e in day_entries
        if e.get("vastenniveau")
        and not is_period_entry(e)
        and not is_weekly_entry(e)
    ]

    vrij_periods = [e for e in periods if e.get("vastenniveau") == "vrij"]
    if vrij_periods:
        bron = vrij_periods[0]
        return VastenIndicatie(
            niveau="vrij",
            tekst=_tekst(niveau="vrij", bron=_naam(bron)),
            periode_id=bron.get("id"),
        )

    in_grote_week = any(e.get("id") == GROTE_WEEK_ID for e in periods)

    if periods:
        base_entry = min(
            periods,
            key=lambda e: COMPARE_RANK.get(e.get("vastenniveau") or "streng", 0),
        )
        base = str(base_entry.get("vastenniveau") or "streng")
        weekend = False
        if (
            weekday in (6, 7)
            and COMPARE_RANK[base] == COMPARE_RANK["streng"]
            and not in_grote_week
        ):
            base = "wijn_olie"
            weekend = True

        relaxers = [
            e
            for e in day_feasts
            if COMPARE_RANK[str(e["vastenniveau"])] > COMPARE_RANK[base]
        ]
        versoepeld = None
        effective = base
        if relaxers:
            versoepeld = max(
                relaxers, key=lambda e: COMPARE_RANK[str(e["vastenniveau"])]
            )
            effective = str(versoepeld["vastenniveau"])

        if in_grote_week and COMPARE_RANK[effective] > COMPARE_RANK["wijn_olie"]:
            effective = "wijn_olie"

        return VastenIndicatie(
            niveau=effective,
            tekst=_tekst(
                niveau=effective,
                bron=_naam(base_entry),
                versoepeld_door=_naam(versoepeld) if versoepeld else None,
                weekend=weekend and not versoepeld,
                weekday=weekday,
            ),
            periode_id=base_entry.get("id"),
            versoepeld_door_id=(versoepeld or {}).get("id") if versoepeld else None,
            weekend=weekend and not versoepeld,
        )

    tightening = [
        e for e in day_feasts if "vasten" in _observances(e)
    ]
    relaxing = [e for e in day_feasts if "vasten" not in _observances(e)]

    if tightening:
        chosen = min(
            tightening, key=lambda e: COMPARE_RANK[str(e["vastenniveau"])]
        )
        niveau = str(chosen["vastenniveau"])
        if weekly:
            niveau = _stricter(niveau, str(weekly[0].get("vastenniveau") or "wijn_olie"))
        return VastenIndicatie(
            niveau=niveau,
            tekst=_tekst(niveau=niveau, bron=_naam(chosen)),
            versoepeld_door_id=None,
        )

    if weekly:
        weekly_level = str(weekly[0].get("vastenniveau") or "wijn_olie")
        if relaxing:
            chosen = max(
                relaxing, key=lambda e: COMPARE_RANK[str(e["vastenniveau"])]
            )
            feast_level = str(chosen["vastenniveau"])
            effective = _more_lenient(weekly_level, feast_level)
            if effective == "vrij":
                return VastenIndicatie(
                    niveau="vrij",
                    tekst=_tekst(niveau="vrij", bron=_naam(chosen)),
                )
            if COMPARE_RANK[feast_level] > COMPARE_RANK[weekly_level]:
                return VastenIndicatie(
                    niveau=effective,
                    tekst=_tekst(
                        niveau=effective,
                        bron=_naam(weekly[0]),
                        versoepeld_door=_naam(chosen),
                    ),
                    versoepeld_door_id=chosen.get("id"),
                )
        return VastenIndicatie(
            niveau=weekly_level,
            tekst=_tekst(niveau=weekly_level, bron=_naam(weekly[0])),
        )

    vrij_feasts = [e for e in relaxing if e.get("vastenniveau") == "vrij"]
    if vrij_feasts:
        chosen = vrij_feasts[0]
        return VastenIndicatie(
            niveau="vrij",
            tekst=_tekst(niveau="vrij", bron=_naam(chosen)),
        )

    return None
