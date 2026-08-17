"""Nederlandse perikoop-verwijzing → OSIS-hoofdstuk voor debijbel.nl.

De browser bouwt de URL; deze module is de canonieke boekmapping
(tests + documentatie). Spiegel de tabel in ``site/assets/js/calendar.js``.
"""

from __future__ import annotations

import re

# Langste eerst bij matching (1 Joh. vóór Joh.).
BOEK_OSIS: dict[str, str] = {
    "1 Joh.": "1JN",
    "2 Joh.": "2JN",
    "3 Joh.": "3JN",
    "1 Kor.": "1CO",
    "2 Kor.": "2CO",
    "1 Petr.": "1PE",
    "2 Petr.": "2PE",
    "1 Tess.": "1TH",
    "2 Tess.": "2TH",
    "1 Tim.": "1TI",
    "2 Tim.": "2TI",
    "Ef.": "EPH",
    "Fil.": "PHP",
    "Gal.": "GAL",
    "Hand.": "ACT",
    "Heb.": "HEB",
    "Jak.": "JAS",
    "Joh.": "JHN",
    "Jud.": "JUD",
    "Kol.": "COL",
    "Luc.": "LUK",
    "Mark.": "MRK",
    "Matt.": "MAT",
    "Rom.": "ROM",
    "Tit.": "TIT",
}

_BOEKEN_LANGSTE_EERST = tuple(sorted(BOEK_OSIS, key=len, reverse=True))

DEBIJBEL_BASIS = "https://www.debijbel.nl/bijbel"
STANDAARD_VERTALING = "NBV21"


def osis_hoofdstuk(ref: str) -> str | None:
    """Eerste boek + eerste hoofdstuk, bijv. ``Rom. 13:11-14:4`` → ``ROM.13``."""
    text = str(ref or "").strip()
    if not text:
        return None
    lower = text.lower()
    for boek in _BOEKEN_LANGSTE_EERST:
        if lower.startswith(boek.lower()):
            rest = text[len(boek) :].lstrip()
            match = re.match(r"(\d+)", rest)
            if not match:
                return None
            return f"{BOEK_OSIS[boek]}.{match.group(1)}"
    return None


def ref_delen(ref: str) -> list[str]:
    """Splits ``Matt. 26:2-20; Joh. 13:3-17``; laat ``Matt. 4:25; 5:1-13`` heel."""
    delen: list[str] = []
    buf = ""
    for raw in str(ref or "").split(";"):
        piece = raw.strip()
        if not piece:
            continue
        if buf and osis_hoofdstuk(piece) is None:
            buf = f"{buf}; {piece}"
        elif buf:
            delen.append(buf)
            buf = piece
        else:
            buf = piece
    if buf:
        delen.append(buf)
    return delen


def debijbel_url(ref: str, vertaling: str = STANDAARD_VERTALING) -> str | None:
    osis = osis_hoofdstuk(ref)
    if not osis:
        return None
    versie = (vertaling or STANDAARD_VERTALING).strip() or STANDAARD_VERTALING
    return f"{DEBIJBEL_BASIS}/{versie}/{osis}"
