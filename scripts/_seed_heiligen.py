"""Importeer stub-heiligen uit legacy YAML (Gregoriaanse feestdag-default)."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LEGACY = Path(r"C:\Git\orthodox-groningen\heiligen\heiligen_lage_landen_vsn_0.yaml")
OUT = ROOT / "data" / "heiligen"

MONTHS = {
    "januari": 1,
    "februari": 2,
    "maart": 3,
    "april": 4,
    "mei": 5,
    "juni": 6,
    "juli": 7,
    "augustus": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "december": 12,
}

BRON_MAP = {
    "eir3app": "eir3app",
    "eirapp": "eir3app",
    "wiki": "wiki-heiligen",
    "Wikipedia": "wiki-heiligen",
    "hnet": "hnet",
    "hlex": "hlex",
    "hlex (Markhelm)": "hlex",
}


def slugify(name: str) -> str:
    s = name.lower()
    s = (
        s.replace("ë", "e")
        .replace("é", "e")
        .replace("è", "e")
        .replace("ä", "a")
        .replace("ö", "o")
        .replace("ü", "u")
        .replace("ï", "i")
    )
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def parse_feast(text: str) -> str | None:
    # "27 november" or "26 januari (voorheen)"
    m = re.match(
        r"^\s*(\d{1,2})\s+(januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)\b",
        text.lower(),
    )
    if not m:
        return None
    day = int(m.group(1))
    month = MONTHS[m.group(2)]
    return f"{month:02d}-{day:02d}"


def main() -> int:
    raw = yaml.safe_load(LEGACY.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    written = 0
    skipped = 0
    for item in raw.get("heiligen") or []:
        naam = item.get("naam")
        feestdagen = item.get("feestdag") or []
        primary = None
        extras = []
        for fd in feestdagen:
            mmdd = parse_feast(str(fd))
            if not mmdd:
                continue
            if primary is None:
                primary = mmdd
            else:
                extras.append({"waarde": mmdd, "toelichting": str(fd)})
        if not primary:
            skipped += 1
            continue
        eid = slugify(naam)
        refs = []
        for b in item.get("bronnen") or []:
            if isinstance(b, str) and b.startswith("http"):
                refs.append(
                    {
                        "label": "Externe bron",
                        "url": b,
                        "geraadpleegd": "2026-08-15",
                    }
                )
            else:
                bron_id = BRON_MAP.get(str(b))
                if bron_id:
                    refs.append({"bron_id": bron_id, "geraadpleegd": "2026-08-15"})
                elif b:
                    refs.append(
                        {
                            "label": str(b),
                            "geraadpleegd": "2026-08-15",
                            "opmerking": "Nog te normaliseren naar bronnen.yaml",
                        }
                    )
        if not refs:
            refs.append(
                {
                    "label": "Legacy import (bron nog te verifiëren)",
                    "geraadpleegd": "2026-08-15",
                    "opmerking": "Geïmporteerd uit heiligen_lage_landen_vsn_0.yaml",
                }
            )

        doc = {
            "id": eid,
            "soort": "heilige",
            "status": "stub",
            "cyclus": "jaar",
            "lage_landen": True,
            "namen": {"primair": naam},
            "datum": {"waarde": primary, "stijl": "gregoriaans"},
        }
        if extras:
            doc["datum"]["extra"] = extras
        if item.get("alternatieve_namen"):
            doc["namen"]["alternatief"] = list(item["alternatieve_namen"])
        if item.get("titel"):
            doc["titels"] = [item["titel"]]
        if item.get("locatie"):
            doc["locaties"] = [item["locatie"]]
        if item.get("sterfjaar"):
            doc["periode"] = str(item["sterfjaar"])
        doc["samenvatting"] = (
            f"Heilige van de Lage Landen: {naam}."
            + (f" {item['titel']}." if item.get("titel") else "")
        )
        doc["referenties"] = refs

        text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False)
        (OUT / f"{eid}.yaml").write_text(text, encoding="utf-8", newline="\n")
        written += 1

    # A few curated upgrades
    curated = {
        "willibrord": {
            "status": "curated",
            "samenvatting": "Apostel van de Friezen; aartsbisschop van Utrecht.",
            "verhaal": (
                "Willibrord (ca. 658–739) predikte onder de Friezen en stichtte de zetel van Utrecht. "
                "Hij wordt gerekend tot de voornaamste heiligen van de Lage Landen. "
                "Zijn feestdag wordt in veel bronnen op 7 november gezet."
            ),
            "referenties": [
                {"bron_id": "hnet", "geraadpleegd": "2026-08-15"},
                {"bron_id": "eir3app", "geraadpleegd": "2026-08-15"},
                {"bron_id": "hlex", "geraadpleegd": "2026-08-15"},
            ],
        },
        "bonifatius": {
            "status": "curated",
            "samenvatting": "Missionaris en martelaar, verbonden met de kerstening van de Lage Landen en Germanië.",
            "verhaal": (
                "Bonifatius (Wynfreth) werkte als missionaris op het vasteland en stierf als martelaar bij Dokkum (ca. 754). "
                "Hij wordt breed vereerd in de Lage Landen; de feestdag valt op 5 juni in gangbare bronnen."
            ),
            "referenties": [
                {"bron_id": "hnet", "geraadpleegd": "2026-08-15"},
                {"bron_id": "eir3app", "geraadpleegd": "2026-08-15"},
            ],
        },
        "walfridus-bedum": {
            "status": "curated",
            "samenvatting": "Plaatselijke heilige verbonden met Bedum.",
            "verhaal": (
                "Walfridus (of Walfried) wordt in Groninger traditie verbonden met Bedum. "
                "De feestdag 22 juni volgt lokale notities; verdere hagiografische details vragen om aanvullende bronnen."
            ),
            "referenties": [
                {
                    "label": "Thabor-notities augustus 2024",
                    "geraadpleegd": "2026-08-15",
                    "opmerking": "Lokale liturgische notitie; nader te publiceren/archiveren.",
                }
            ],
        },
    }
    for eid, patch in curated.items():
        path = OUT / f"{eid}.yaml"
        if not path.exists():
            # try fuzzy
            matches = list(OUT.glob(f"*{eid.split('-')[0]}*.yaml"))
            if not matches:
                continue
            path = matches[0]
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        doc.update(patch)
        path.write_text(
            yaml.safe_dump(doc, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
            newline="\n",
        )

    print(f"written={written} skipped_no_feast={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
