"""Juliaanse ↔ Gregoriaanse conversie (offset tot 2100).

Feestdagen hebben één kalenderdatum (MM-DD), die in beide kalenders
dezelfde dagnaam heeft (bijv. Ontslapen = 15 augustus). De offset wordt
alleen gebruikt om *vandaag* om te rekenen tussen burgerlijke
(Gregoriaanse) en Juliaanse tijdrekening.
"""

from __future__ import annotations

from datetime import date, timedelta

# Offset Juliaans ↔ Gregoriaans tot 28 februari 2100.
OFFSET_DAYS = 13
REF_YEAR = 2001  # niet-schrikkeljaar voor MM-DD-normalisatie


def parse_mmdd(value: str) -> tuple[int, int]:
    parts = str(value).strip().split("-")
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
    """Zet een Juliaanse kalenderdatum om naar de gelijktijdige Gregoriaanse datum."""
    d = _as_date(month, day) + timedelta(days=OFFSET_DAYS)
    return d.month, d.day


def gregorian_to_julian(month: int, day: int) -> tuple[int, int]:
    """Zet een Gregoriaanse (burgerlijke) datum om naar de gelijktijdige Juliaanse datum."""
    d = _as_date(month, day) - timedelta(days=OFFSET_DAYS)
    return d.month, d.day


def civil_to_julian_mmdd(mmdd: str) -> str:
    month, day = parse_mmdd(mmdd)
    j_m, j_d = gregorian_to_julian(month, day)
    return format_mmdd(j_m, j_d)


def julian_to_civil_mmdd(mmdd: str) -> str:
    month, day = parse_mmdd(mmdd)
    g_m, g_d = julian_to_gregorian(month, day)
    return format_mmdd(g_m, g_d)


def normalize_dates(mmdd: str, stijl: str = "gregoriaans") -> dict[str, str]:
    """Normaliseer invoer tot één feestdatum.

    ``stijl`` documenteert hoe de beheerder de waarde bedoelde (default:
    gregoriaans). De feestdatum zelf is de MM-DD van het feest en is in
    nieuwe én oude kalender dezelfde dagnaam (15 augustus = 15 augustus).
    """
    style = (stijl or "gregoriaans").strip().lower()
    if style not in {"gregoriaans", "juliaans"}:
        raise ValueError(f"Onbekende stijl: {stijl!r}")
    month, day = parse_mmdd(mmdd)
    feestdatum = format_mmdd(month, day)
    return {
        "invoer": feestdatum,
        "stijl": style,
        "feestdatum": feestdatum,
    }
