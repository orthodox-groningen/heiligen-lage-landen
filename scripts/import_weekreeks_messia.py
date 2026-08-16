"""Importeer weekreeks uit Messia-ukazatel (markdown-tabel) → data/lezingen/weekreeks.yaml.

Bron: https://messia.ru/spravki/kalendar/lkcioprc.htm
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "lezingen" / "weekreeks.yaml"

BOOKS = {
    "Деян": "Hand.",
    "Рим": "Rom.",
    "1Кор": "1 Kor.",
    "2Кор": "2 Kor.",
    "Гал": "Gal.",
    "Еф": "Ef.",
    "Флп": "Fil.",
    "Кол": "Kol.",
    "1Фес": "1 Tess.",
    "2Фес": "2 Tess.",
    "1Тим": "1 Tim.",
    "2Тим": "2 Tim.",
    "Тит": "Tit.",
    "Евр": "Heb.",
    "Иак": "Jak.",
    "1Пет": "1 Petr.",
    "2Пет": "2 Petr.",
    "1Ин": "1 Joh.",
    "2Ин": "2 Joh.",
    "3Ин": "3 Joh.",
    "Иуд": "Jud.",
    "Мф": "Matt.",
    "Мк": "Mark.",
    "Лк": "Luc.",
    "Ин": "Joh.",
}

WD_KEYS = ("пн", "вт", "ср", "чт", "пт", "сб")
WD_MAP = {k: i + 1 for i, k in enumerate(WD_KEYS)}
WD_MAP["вс"] = 7

ZACALO_TAIL = re.compile(r"/\d+[a-zA-Z\-]*\s*")
DASHES = str.maketrans({"–": "-", "—": "-", "−": "-"})


def translate_ref(raw: str) -> str | None:
    text = (raw or "").strip()
    if not text or text.startswith("("):
        return None
    low = text.lower()
    if low.startswith("на утрени") or "вечерни" in low or "преждеосв" in low:
        return None
    if low.startswith("на 6"):
        return None
    for sep in (
        "и за упок",
        "и святому",
        "и преподобн",
        "и Богородице",
        "и Отцам",
        "и за упокой",
    ):
        idx = text.find(sep)
        if idx > 0:
            text = text[:idx]
    text = ZACALO_TAIL.sub("", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\([^)]*\)", "", text)
    text = text.translate(DASHES)
    text = re.sub(r"\s+", " ", text).strip(" ;,")
    if not text:
        return None
    out = text
    for ru in sorted(BOOKS.keys(), key=len, reverse=True):
        out = re.sub(rf"(?<!\w){re.escape(ru)}\.?", BOOKS[ru], out)
    out = out.translate(DASHES)
    # Russisch: hfdstuk,vers → hfdstuk:vers (niet de punt na de boekafkorting)
    out = re.sub(r"(\d+),(\d+)", r"\1:\2", out)
    # Zelfde hoofdstuk, meer verzen: "17. 21" → "17, 21"
    out = re.sub(r"(\d)\.\s+(\d)", r"\1, \2", out)
    out = re.sub(r"\s*-\s*", "-", out)
    out = re.sub(r"\s*;\s*", "; ", out)
    out = re.sub(r"\s+", " ", out).strip()
    # Footnote debris
    out = re.sub(r"/\s*$", "", out).strip()
    if not any(out.startswith(v) for v in BOOKS.values()):
        return None
    return out


def detect_weekday(cell: str) -> int | None:
    c = (cell or "").strip().lower()
    if not c:
        return None
    # leading weekday token
    token = re.split(r"[\s,.(]", c, maxsplit=1)[0]
    if token in WD_MAP:
        return WD_MAP[token]
    if c.startswith("вс") or "вс," in c or c.startswith("вс "):
        return 7
    return None


def detect_week_header(cell: str) -> tuple[str, int] | None:
    c = cell or ""
    if "Пасхальная седмица" in c:
        return ("pascha", 1)
    m = re.search(r"(\d+)\s*седмица по Пасхе", c)
    if m:
        return ("pascha", int(m.group(1)))
    m = re.search(r"(\d+)\s*седмица по Пятиде", c)
    if m:
        return ("na_pinksteren", int(m.group(1)))
    if "Сырная" in c:
        return ("na_pinksteren", 36)
    m = re.search(r"(\d+)\s*седмица Поста", c)
    if m:
        return ("vasten", int(m.group(1)))
    if c.startswith("Страстная"):
        return ("vasten", 7)
    return None


def detect_sunday(c0: str, c1: str) -> tuple[str, int] | None:
    blob = f"{c0} {c1}"
    if "Пасха" in blob and ("вс" in blob.lower() or "Вс" in blob):
        return ("pascha", 1)
    if "Пятидесятница" in blob:
        return ("pascha", 8)
    if "о Фоме" in blob:
        return ("pascha", 2)
    if "Мироносиц" in blob:
        return ("pascha", 3)
    if "Расслабленн" in blob:
        return ("pascha", 4)
    if "Самарян" in blob:
        return ("pascha", 5)
    if "о Слепом" in blob:
        return ("pascha", 6)
    if "Святых Отец" in blob and "Вс 7" in blob:
        return ("pascha", 7)
    if "Всех Святых" in blob:
        return ("na_pinksteren", 1)
    if "Мытаре" in blob:
        return ("na_pinksteren", 33)
    if "Блудном" in blob:
        return ("na_pinksteren", 34)
    if "Страшном Суде" in blob or "мясопустная" in blob:
        return ("na_pinksteren", 35)
    if "сыропустная" in blob or "Прощеное" in blob:
        return ("na_pinksteren", 36)
    if "Закхее" in blob:
        return ("na_pinksteren", 32)
    m = re.search(r"Вс\s*(\d+)", blob)
    if m:
        n = int(m.group(1))
        # Heuristic: Вс 1–8 near Pascha block vs after Pentecost
        # Caller sets period from context; here return week only via period guess
        if "по Пасхе" in blob or n <= 8 and "Пятиде" not in blob and "Всех" not in blob:
            # Ambiguous — return None and let numbered Вс with context handle
            pass
        return ("na_pinksteren", n)
    # Lent Sundays
    if "Торжество православия" in blob:
        return ("vasten", 1)
    if "Григория Паламы" in blob:
        return ("vasten", 2)
    if re.search(r"Вс\s*3", blob) and "Пост" in blob:
        return ("vasten", 3)
    if "вербное" in blob or "ваий" in blob:
        return ("vasten", 6)  # Palm as end of week 6 / Sunday
    if "Лазарева" in blob:
        return ("vasten", 6)  # Saturday
    return None


def parse_table(text: str) -> list[dict]:
    period: str | None = None
    week: int | None = None
    entries: list[dict] = []

    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        c0, c1, _c2, apostel_raw, evangelie_raw = cells[:5]
        if c0 in {"Седмица", ""} and c1 in {"день", ""}:
            continue
        if "апостольское" in apostel_raw.lower():
            continue

        header = detect_week_header(c0)
        if header:
            period, week = header

        weekday = detect_weekday(c1) or detect_weekday(c0)
        sunday = None
        if weekday == 7 or (c0.startswith("Вс") or "Вс " in c0):
            sunday = detect_sunday(c0, c1)
            if sunday:
                period, week = sunday
                weekday = 7
            elif weekday is None:
                weekday = 7

        # Numbered Sunday rows like "| Вс 3 |" without special name
        m = re.match(r"Вс\s*(\d+)\s*$", c0.strip())
        if m and period:
            week = int(m.group(1))
            weekday = 7

        if weekday is None or period is None or week is None:
            continue

        apostel = translate_ref(apostel_raw)
        evangelie = translate_ref(evangelie_raw)

        if not apostel and not evangelie:
            if period == "vasten" and weekday <= 5:
                entries.append(
                    {
                        "periode": period,
                        "week": week,
                        "weekdag": weekday,
                        "apostel": [],
                        "evangelie": [],
                        "status": "geen_liturgie",
                    }
                )
            continue

        entries.append(
            {
                "periode": period,
                "week": week,
                "weekdag": weekday,
                "apostel": [{"ref": apostel}] if apostel else [],
                "evangelie": [{"ref": evangelie}] if evangelie else [],
            }
        )

    by_key: dict[tuple, dict] = {}
    for e in entries:
        by_key[(e["periode"], e["week"], e["weekdag"])] = e
    return list(by_key.values())


def main(src: Path) -> int:
    entries = parse_table(src.read_text(encoding="utf-8"))
    payload = {
        "bron": {
            "label": "Messia — ukazatel’ apostolskih i evangel’skih čtenij",
            "url": "https://messia.ru/spravki/kalendar/lkcioprc.htm",
            "geraadpleegd": "2026-08-16",
            "notitie": (
                "Tabellen uit Brussel/Жизнь с Богом; Lucaanse sprong volgens "
                "Moskou (maandag na zondag na Kruisverheffing) in scripts/lezingen.py."
            ),
        },
        "dagen": sorted(
            entries,
            key=lambda e: (e["periode"], e["week"], e["weekdag"]),
        ),
    }
    OUT.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
        newline="\n",
    )
    print(f"Schreef {len(entries)} dagen naar {OUT}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_weekreeks_messia.py <messia.md>")
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
