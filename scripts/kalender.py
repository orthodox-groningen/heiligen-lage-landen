"""Juliaanse ↔ Gregoriaanse conversie en Orthodoxe Pascha-computus.

Feestdagen met vaste MM-DD hebben in beide kalenders dezelfde dagnaam
(bijv. Ontslapen = 15 augustus). De jaarafhankelijke offset (13 tot
28 februari 2100, daarna 14) wordt gebruikt om *vandaag* om te rekenen,
voor ICS “oud”, en om Juliaanse Pascha-data naar de wereldlijke kalender
te zetten.

Orthodox Pascha: Meeus’ Juliaanse algoritme (Alexandrijnse computus),
daarna omzetting naar de Gregoriaanse (burgerlijke) datum. Alle Orthodoxe
kerken gebruiken deze Pascha-datum.
"""

from __future__ import annotations

from datetime import date, timedelta

# Referentiejaar voor MM-DD-normalisatie zonder jaartal (niet-schrikkel).
REF_YEAR = 2001


def julian_gregorian_offset_days(year: int) -> int:
    """Verschil Gregoriaans−Juliaans in hele dagen voor een gegeven jaar.

    1900–2099 → 13, 2100–2199 → 14, enz.
    (formule: ⌊Y/100⌋ − ⌊Y/400⌋ − 2).
    """
    return year // 100 - year // 400 - 2


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


def mmdd_from_date(d: date) -> str:
    return format_mmdd(d.month, d.day)


def _julian_calendar_to_jdn(year: int, month: int, day: int) -> int:
    """Juliaanse kalenderdatum → Julian Day Number (chronologische JDN)."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083


def _gregorian_to_jdn(year: int, month: int, day: int) -> int:
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def _jdn_to_gregorian(jdn: int) -> date:
    a = jdn + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + m // 10
    return date(year, month, day)


def _jdn_to_julian_calendar(jdn: int) -> tuple[int, int, int]:
    b = jdn + 32082
    c = (4 * b + 3) // 1461
    d = b - (1461 * c) // 4
    m = (5 * d + 2) // 153
    day = d - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = c - 4800 + m // 10
    return year, month, day


def julian_calendar_to_gregorian(year: int, month: int, day: int) -> date:
    """Zet een datum op de Juliaanse kalender om naar Gregoriaans (wereldlijk)."""
    return _jdn_to_gregorian(_julian_calendar_to_jdn(year, month, day))


def gregorian_to_julian_calendar(d: date) -> tuple[int, int, int]:
    """Zet een Gregoriaanse datum om naar Juliaanse kalender Y-M-D."""
    return _jdn_to_julian_calendar(_gregorian_to_jdn(d.year, d.month, d.day))


def julian_to_gregorian(month: int, day: int, *, year: int = REF_YEAR) -> tuple[int, int]:
    """Zet Juliaanse MM-DD (in ``year``) om naar Gregoriaanse maand/dag."""
    g = julian_calendar_to_gregorian(year, month, day)
    return g.month, g.day


def gregorian_to_julian(month: int, day: int, *, year: int = REF_YEAR) -> tuple[int, int]:
    """Zet Gregoriaanse MM-DD (in ``year``) om naar Juliaanse maand/dag."""
    _y, j_m, j_d = gregorian_to_julian_calendar(date(year, month, day))
    return j_m, j_d


def civil_to_julian_mmdd(mmdd: str, *, year: int = REF_YEAR) -> str:
    month, day = parse_mmdd(mmdd)
    j_m, j_d = gregorian_to_julian(month, day, year=year)
    return format_mmdd(j_m, j_d)


def julian_to_civil_mmdd(mmdd: str, *, year: int = REF_YEAR) -> str:
    month, day = parse_mmdd(mmdd)
    g_m, g_d = julian_to_gregorian(month, day, year=year)
    return format_mmdd(g_m, g_d)


def julian_feast_to_civil_date(year: int, mmdd: str) -> date:
    """Vierdatum in de wereldlijke agenda voor een Juliaanse feestdatum in ``year``."""
    month, day = parse_mmdd(mmdd)
    return julian_calendar_to_gregorian(year, month, day)


def orthodox_pascha_julian(year: int) -> tuple[int, int]:
    """Meeus’ Juliaanse algoritme → (maand, dag) op de Juliaanse kalender."""
    a = year % 4
    b = year % 7
    c = year % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    month = (d + e + 114) // 31
    day = ((d + e + 114) % 31) + 1
    return month, day


def orthodox_pascha(year: int) -> date:
    """Orthodox Pascha als Gregoriaanse (wereldlijke) datum."""
    j_m, j_d = orthodox_pascha_julian(year)
    return julian_calendar_to_gregorian(year, j_m, j_d)


def pascha_offset_date(year: int, offset_dagen: int) -> date:
    """Gregoriaanse datum van een paascyclus-dag (offset t.o.v. Pascha)."""
    return orthodox_pascha(year) + timedelta(days=offset_dagen)


def normalize_dates(mmdd: str, stijl: str = "gregoriaans") -> dict[str, str]:
    """Normaliseer vaste invoer tot één feestdatum (MM-DD).

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
