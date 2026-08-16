"""Resolutie van Apostel- en Evangelielezingen (Moskou / ROCOR-fallback).

Normatieve regels: docs/specs/lezingen.md
Data: data/lezingen/
"""

from __future__ import annotations

import calendar
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml

from kalender import (
    gregorian_to_julian_calendar,
    mmdd_from_date,
    parse_mmdd,
    pascha_offset_date,
    orthodox_pascha,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "docs" / "specs" / "lezingen.md"
DATA_DIR = REPO_ROOT / "data" / "lezingen"
VOORBEELD_FENCE = re.compile(
    r"```lezingen-voorbeeld\s*\n(.*?)```",
    re.DOTALL,
)

WEEKDAG_NL = {
    1: "Maandag",
    2: "Dinsdag",
    3: "Woensdag",
    4: "Donderdag",
    5: "Vrijdag",
    6: "Zaterdag",
    7: "Zondag",
}

# Vaste override-id → Nederlandse liturgische dagnaam
OVERRIDE_NAMEN: dict[str, str] = {
    "pascha": "Pascha",
    "lichte-maandag": "Lichte maandag",
    "thomaszondag": "Thomaszondag",
    "zondag-mirredraagsters": "Zondag van de mirredraagsters",
    "zondag-verlamde": "Zondag van de verlamde",
    "midden-pinksterfeest": "Midden-Pinksterfeest",
    "zondag-samaritaanse": "Zondag van de Samaritaanse",
    "zondag-blinde": "Zondag van de blinde",
    "hemelvaart": "Hemelvaart",
    "zondag-vaderen-eerste-concilie": "Zondag van de heilige Vaderen (Eerste Concilie)",
    "pinksteren": "Pinksteren",
    "geestesmaandag": "Maandag van de Heilige Geest",
    "allerheiligen-zondag": "Allerheiligenzondag",
    "zondag-laatste-oordeel": "Zondag van het Laatste Oordeel",
    "vergevingszondag": "Vergevingszondag",
    "zondag-orthodoxie": "Zondag van de Orthodoxie",
    "zondag-gregorius-palamas": "Zondag van Gregorius Palamas",
    "zondag-kruisverering": "Zondag van de Kruisverering",
    "zondag-johannes-klimacus": "Zondag van Johannes Klimacus",
    "zondag-maria-van-egypte": "Zondag van Maria van Egypte",
    "lazarus-zaterdag": "Lazaruszaterdag",
    "palmzondag": "Palmzondag",
    "grote-donderdag": "Heilige grote donderdag",
    "grote-zaterdag": "Heilige grote zaterdag",
    "besnijdenis-des-heren": "Besnijdenis des Heren",
    "theofanie": "Theofanie",
    "ontmoeting-in-de-tempel": "Ontmoeting in de tempel",
    "aankondiging": "Aankondiging",
    "geboorte-johannes-doper": "Geboorte van Johannes de Doper",
    "petrus-en-paulus": "Petrus en Paulus",
    "transfiguratie": "Transfiguratie",
    "ontslapen-moeder-gods": "Ontslapen van de Moeder Gods",
    "onthoofding-johannes-doper": "Onthoofding van Johannes de Doper",
    "geboorte-moeder-gods": "Geboorte van de Moeder Gods",
    "kruisverheffing": "Kruisverheffing",
    "tempelgang-moeder-gods": "Tempelgang van de Moeder Gods",
    "kerst": "Kerst",
}


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
    daglabel: str = ""
    toelichting: str = ""
    status: str = "onbekend"  # gevonden | geen_liturgie | onbekend

    def as_dict(self) -> dict[str, Any]:
        return {
            "apostel": [a.as_dict() for a in self.apostel],
            "evangelie": [e.as_dict() for e in self.evangelie],
            "regels": list(self.regels),
            "override_id": self.override_id,
            "daglabel": self.daglabel,
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


_WEEKREEKS: dict[tuple[str, int, int], dict[str, Any]] | None = None


def load_weekreeks() -> dict[tuple[str, int, int], dict[str, Any]]:
    global _WEEKREEKS
    if _WEEKREEKS is not None:
        return _WEEKREEKS
    path = DATA_DIR / "weekreeks.yaml"
    out: dict[tuple[str, int, int], dict[str, Any]] = {}
    if path.is_file():
        raw = load_yaml(path) or {}
        for row in raw.get("dagen") or []:
            key = (str(row["periode"]), int(row["week"]), int(row["weekdag"]))
            out[key] = row
    _WEEKREEKS = out
    return out


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


def _civil_date(jaar: int, mmdd: str, stijl: str) -> date:
    """Wereldlijke datum bij gegeven kalenderdagnaam."""
    month, day = parse_mmdd(mmdd)
    if stijl == "oud":
        from kalender import julian_calendar_to_gregorian

        return julian_calendar_to_gregorian(jaar, month, day)
    return date(jaar, month, day)


def _iso_weekday(d: date) -> int:
    """1=ma … 7=zo."""
    return d.isoweekday()


def lucaanse_sprong_maandag(jaar: int) -> date:
    """Maandag na de zondag na Kruisverheffing (14 sept., feestdatum).

    Als 14 sept. zelf zondag is, geldt de *volgende* zondag als
    «Неделя по Воздвижении».
    """
    exaltation = date(jaar, 9, 14)
    if exaltation.isoweekday() == 7:
        nedelya = exaltation + timedelta(days=7)
    else:
        # eerstvolgende zondag strikt na 14 sept.
        nedelya = exaltation + timedelta(days=(7 - exaltation.isoweekday()))
    return nedelya + timedelta(days=1)


def _week_index_pascha(offset: int) -> tuple[int, int] | None:
    """(week, weekdag) in paasperiode; week 1 = Pascha-zondag … week 8 = Pinksteren."""
    if offset < 0 or offset > 49:
        return None
    week = offset // 7 + 1
    rem = offset % 7
    weekday = 7 if rem == 0 else rem
    return week, weekday


def _week_index_na_pinksteren(offset_from_pentecost: int) -> tuple[int, int] | None:
    """(week, weekdag) na Pinksteren; week 1 ma = Geestesmaandag, zo = Allerheiligen."""
    if offset_from_pentecost < 1:
        return None
    week = (offset_from_pentecost - 1) // 7 + 1
    weekday = (offset_from_pentecost - 1) % 7 + 1
    return week, weekday


def _week_index_triodion(offset: int) -> tuple[str, int, int] | None:
    """(periode, week, weekdag) voor Triodion/vasten (negatieve Pascha-offset).

    Tollenaar-zondag = -70 -> tabel week 33; Vergeving = -49 -> week 36;
    Grote Vasten week 1 ma = -48.
    """
    if offset == -70:
        return ("na_pinksteren", 33, 7)
    if offset == -63:
        return ("na_pinksteren", 34, 7)
    if offset == -56:
        return ("na_pinksteren", 35, 7)
    if offset == -49:
        return ("na_pinksteren", 36, 7)
    if -69 <= offset <= -64:
        return ("na_pinksteren", 34, offset + 70)
    if -62 <= offset <= -57:
        return ("na_pinksteren", 35, offset + 63)
    if -55 <= offset <= -50:
        return ("na_pinksteren", 36, offset + 56)
    if -48 <= offset <= -9:
        rel = offset - (-48)
        week = rel // 7 + 1
        weekday = rel % 7 + 1
        if week > 6:
            return None
        return ("vasten", week, weekday)
    if -6 <= offset <= -2:
        return ("vasten", 7, offset + 7)
    return None


def _ordinal_nl(n: int) -> str:
    return f"{n}e"


def liturgische_daglabel(
    jaar: int,
    mmdd: str,
    stijl: str = "nieuw",
    *,
    override_id: str | None = None,
) -> str:
    """Nederlandse aanduiding van de liturgische dag."""
    if override_id and override_id in OVERRIDE_NAMEN:
        return OVERRIDE_NAMEN[override_id]

    civil = _civil_date(jaar, mmdd, stijl)
    pascha = orthodox_pascha(jaar)
    # Pascha can fall in previous civil year for early Julian dates — use year of civil
    if civil < pascha - timedelta(days=80):
        pascha = orthodox_pascha(jaar - 1)
    elif civil > pascha + timedelta(days=320):
        pascha = orthodox_pascha(jaar + 1)

    offset = (civil - pascha).days
    weekday = _iso_weekday(civil)
    wd_name = WEEKDAG_NL[weekday]

    if override_id:
        return OVERRIDE_NAMEN.get(override_id, override_id)

    # Named Sundays by offset (fallback when no override)
    named = {
        0: "Pascha",
        7: "Thomaszondag",
        14: "Zondag van de mirredraagsters",
        21: "Zondag van de verlamde",
        24: "Midden-Pinksterfeest",
        28: "Zondag van de Samaritaanse",
        35: "Zondag van de blinde",
        39: "Hemelvaart",
        42: "Zondag van de heilige Vaderen",
        49: "Pinksteren",
        50: "Maandag van de Heilige Geest",
        56: "Allerheiligenzondag",
        -70: "Zondag van de tollenaar en de farizeeër",
        -63: "Zondag van de verloren zoon",
        -56: "Zondag van het Laatste Oordeel",
        -49: "Vergevingszondag",
        -8: "Lazaruszaterdag",
        -7: "Palmzondag",
        -3: "Heilige grote donderdag",
        -2: "Heilige grote vrijdag",
        -1: "Heilige grote zaterdag",
    }
    if offset in named:
        return named[offset]

    if 1 <= offset <= 6:
        return f"{wd_name} van de Lichte Week"
    if 0 < offset < 49 and weekday == 7:
        n = offset // 7 + 1  # 2..8
        return f"{_ordinal_nl(n)} zondag van Pascha"
    if 0 < offset < 49:
        week = offset // 7 + 1
        return f"{wd_name} van de {_ordinal_nl(week)} week van Pascha"

    pentecost = pascha + timedelta(days=49)
    if civil >= pentecost:
        off_p = (civil - pentecost).days
        if off_p == 0:
            return "Pinksteren"
        week, wd = _week_index_na_pinksteren(off_p) or (0, 0)
        if week and wd == 7:
            return f"{_ordinal_nl(week)} zondag na Pinksteren"
        if week:
            return f"{wd_name} van de {_ordinal_nl(week)} week na Pinksteren"

    if offset < 0:
        # Lent weekdays
        if -48 <= offset <= -9:
            rel = offset - (-48)
            week = rel // 7 + 1
            return f"{wd_name} van de {_ordinal_nl(week)} week van de Grote Vasten"
        if -6 <= offset <= -2:
            return f"Heilige grote {wd_name.lower()}"
        if -70 < offset < 0 and weekday == 7:
            return "Zondag (Triodion)"

    return wd_name


def _lookup_weekreeks(
    periode: str,
    week: int,
    weekdag: int,
) -> dict[str, Any] | None:
    return load_weekreeks().get((periode, week, weekdag))


def _resolve_weekreeks(
    jaar: int,
    mmdd: str,
    stijl: str,
) -> LezingenResultaat | None:
    civil = _civil_date(jaar, mmdd, stijl)
    pascha = orthodox_pascha(jaar)
    if civil < pascha - timedelta(days=80):
        pascha = orthodox_pascha(jaar - 1)
    elif civil > pascha + timedelta(days=320):
        pascha = orthodox_pascha(jaar + 1)

    offset = (civil - pascha).days
    pentecost = pascha + timedelta(days=49)
    regels = ["R3"]

    # --- Paasperiode inkl. Pinksteren ---
    if 0 <= offset <= 49:
        idx = _week_index_pascha(offset)
        if not idx:
            return None
        week, weekday = idx
        row = _lookup_weekreeks("pascha", week, weekday)
        if not row:
            return None
        return LezingenResultaat(
            apostel=_refs(row.get("apostel")),
            evangelie=_refs(row.get("evangelie")),
            regels=regels,
            daglabel=liturgische_daglabel(jaar, mmdd, stijl),
            toelichting="R3 paasperiode",
            status="gevonden",
        )

    # --- Na Pinksteren (tot Triodion) ---
    if civil > pentecost:
        off_p = (civil - pentecost).days
        idx = _week_index_na_pinksteren(off_p)
        if not idx:
            return None
        apostol_week, weekday = idx

        # Lucaanse sprong: Evangelie vanaf maandag na zondag-na-Kruisverheffing
        # gebruikt week 18, 19, … uit de tabel (Moskou).
        luke_mon = lucaanse_sprong_maandag(civil.year)
        gospel_week = apostol_week
        if civil >= luke_mon:
            gospel_week = 18 + (civil - luke_mon).days // 7
            regels = ["R3", "R3-lucaans"]

        a_row = _lookup_weekreeks("na_pinksteren", apostol_week, weekday)
        g_row = _lookup_weekreeks("na_pinksteren", gospel_week, weekday)
        if not a_row and not g_row:
            return None

        status = "gevonden"
        apostel = _refs((a_row or {}).get("apostel"))
        evangelie = _refs((g_row or {}).get("evangelie"))
        if (a_row or {}).get("status") == "geen_liturgie" and not apostel and not evangelie:
            status = "geen_liturgie"

        return LezingenResultaat(
            apostel=apostel,
            evangelie=evangelie,
            regels=regels,
            daglabel=liturgische_daglabel(jaar, mmdd, stijl),
            toelichting="+".join(regels),
            status=status if (apostel or evangelie or status == "geen_liturgie") else "onbekend",
        )

    # --- Triodion / vasten ---
    if offset < 0:
        idx = _week_index_triodion(offset)
        if not idx:
            return None
        periode, week, weekday = idx
        row = _lookup_weekreeks(periode, week, weekday)
        if not row:
            return None
        if row.get("status") == "geen_liturgie":
            return LezingenResultaat(
                regels=["R4"],
                daglabel=liturgische_daglabel(jaar, mmdd, stijl),
                toelichting="Geen liturgie met Apostel/Evangelie van de dag",
                status="geen_liturgie",
            )
        return LezingenResultaat(
            apostel=_refs(row.get("apostel")),
            evangelie=_refs(row.get("evangelie")),
            regels=["R3"],
            daglabel=liturgische_daglabel(jaar, mmdd, stijl),
            toelichting="R3 triodion/vasten",
            status="gevonden",
        )

    return None


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
        oid = str(ov.get("id") or "")
        return LezingenResultaat(
            apostel=_refs(ov.get("apostel")),
            evangelie=_refs(ov.get("evangelie")),
            regels=regels,
            override_id=oid,
            daglabel=liturgische_daglabel(jaar, mmdd, stijl, override_id=oid),
            toelichting="+".join(regels),
            status="gevonden",
        )

    wr = _resolve_weekreeks(jaar, mmdd, stijl)
    if wr is not None and wr.status in {"gevonden", "geen_liturgie"}:
        if not wr.daglabel:
            wr.daglabel = liturgische_daglabel(jaar, mmdd, stijl)
        return wr

    return LezingenResultaat(
        status="onbekend",
        daglabel=liturgische_daglabel(jaar, mmdd, stijl),
        toelichting="Geen override en geen weekreeks-treffer.",
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


def iter_year_mmdds(jaar: int, stijl: str) -> list[str]:
    """Alle geldige MM-DD in ``jaar`` voor de gekozen stijl."""
    out: list[str] = []
    if stijl == "nieuw":
        for month in range(1, 13):
            days = calendar.monthrange(jaar, month)[1]
            for day in range(1, days + 1):
                out.append(f"{month:02d}-{day:02d}")
        return out
    from kalender import julian_calendar_to_gregorian

    cursor = julian_calendar_to_gregorian(jaar, 1, 1)
    end = julian_calendar_to_gregorian(jaar + 1, 1, 1)
    while cursor < end:
        _jy, jm, jd = gregorian_to_julian_calendar(cursor)
        if _jy == jaar:
            out.append(f"{jm:02d}-{jd:02d}")
        cursor += timedelta(days=1)
    return out


def build_lezingen_dagen_payload(
    years: range | list[int],
    *,
    overrides: list[dict[str, Any]] | None = None,
    full_year: bool = True,
) -> dict[str, Any]:
    """Precompute lezingen: stijl → jaar → mmdd → resultaat (+ daglabel)."""
    ovs = overrides if overrides is not None else load_overrides()
    out: dict[str, Any] = {"nieuw": {}, "oud": {}}
    for stijl in ("nieuw", "oud"):
        by_year: dict[str, dict[str, Any]] = {}
        for year in years:
            by_mmdd: dict[str, Any] = {}
            if full_year:
                mmdds = iter_year_mmdds(year, stijl)
            else:
                mmdds = []
                for ov in ovs:
                    match = ov.get("match") or {}
                    if "paascyclus_offset" in match:
                        mmdds.append(
                            _mmdd_for_offset(
                                year, int(match["paascyclus_offset"]), stijl
                            )
                        )
                    elif "mmdd" in match:
                        mmdds.append(str(match["mmdd"]))
                mmdds = list(dict.fromkeys(mmdds))
            for mmdd in mmdds:
                try:
                    result = resolve_lezingen(year, mmdd, stijl, overrides=ovs)
                except ValueError:
                    continue
                if result.status == "onbekend" and not result.daglabel:
                    continue
                payload = result.as_dict()
                by_mmdd[mmdd] = payload
            if by_mmdd:
                by_year[str(year)] = by_mmdd
        out[stijl] = by_year
    return out
