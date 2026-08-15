"""Juliaanse ↔ Gregoriaanse conversie voor vaste feestdagen (offset tot 2100)."""

from __future__ import annotations

from datetime import date, timedelta

# Liturgische offset Juliaans ↔ Gregoriaans tot 28 februari 2100.
OFFSET_DAYS = 13
REF_YEAR = 2001  # niet-schrikkeljaar voor MM-DD-normalisatie


def parse_mmdd(value: str) -> tuple[int, int]:
    parts = value.strip().split("-")
    if len(parts) != 2:
        raise ValueError(f"Datum moet MM-DD zijn, kreeg: {value!r}")
    month_s, day_s = parts
    month, day = int(month_s), int(day_s)
    date(REF_YEAR, month, day)  # valideert
    return month, day


def format_mmdd(month: int, day: int) -> str:
    return f"{month:02d}-{day:02d}"


def _as_date(month: int, day: int) -> date:
    return date(REF_YEAR, month, day)


def julian_to_gregorian(month: int, day: int) -> tuple[int, int]:
    d = _as_date(month, day) + timedelta(days=OFFSET_DAYS)
    return d.month, d.day


def gregorian_to_julian(month: int, day: int) -> tuple[int, int]:
    d = _as_date(month, day) - timedelta(days=OFFSET_DAYS)
    return d.month, d.day


def normalize_dates(mmdd: str, stijl: str = "gregoriaans") -> dict[str, str]:
    """Geef canonieke MM-DD in beide stijlen.

    ``stijl`` is de betekenis van ``mmdd`` zoals de beheerder die invoerde.
    Default: gregoriaans.
    """
    style = (stijl or "gregoriaans").strip().lower()
    if style not in {"gregoriaans", "juliaans"}:
        raise ValueError(f"Onbekende stijl: {stijl!r}")
    month, day = parse_mmdd(mmdd)
    if style == "gregoriaans":
        g_m, g_d = month, day
        j_m, j_d = gregorian_to_julian(month, day)
    else:
        j_m, j_d = month, day
        g_m, g_d = julian_to_gregorian(month, day)
    return {
        "invoer": format_mmdd(month, day),
        "stijl": style,
        "gregoriaans": format_mmdd(g_m, g_d),
        "juliaans": format_mmdd(j_m, j_d),
    }
