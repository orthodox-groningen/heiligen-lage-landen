"""Vul namen.alternatief op heiligen vanuit referentielabels (+ bekende varianten)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[1]
HEILIGEN = ROOT / "data" / "heiligen"

# Extra aliasen die in bronnen gangbaar zijn (naast wat labels al geven).
EXTRA: dict[str, list[str]] = {
    "adelbert": ["Adelbert van Egmond", "Adalbert van Egmond"],
    "adelgonda": ["Aldegonda", "Aldegonda van Maubeuge", "Aldegondis", "Aldegundis"],
    "albericus-van-utrecht": ["Alberik I van Utrecht", "Alberik van Utrecht"],
    "alberik": ["Alberik I van Utrecht", "Albericus"],
    "aubertus-van-kamerijk": ["Autbertus van Kamerijk", "Autbertus"],
    "bavo": ["Bavo van Gent", "Allowin"],
    "bonifatius": ["Bonifacius", "Wynfrith"],
    "domitianus": ["Domitianus van Hoei"],
    "dymphna": ["Dimpna", "Dymphna van Geel"],
    "eligius": ["Eloi", "Elooi"],
    "engelmund": ["Engelmundus", "Engelmundus van Velsen"],
    "ermelindis": ["Ermelindis van Meldert"],
    "floribert": ["Floribertus van Luik", "Floribertus"],
    "folciunus": ["Folcuin", "Folcwin"],
    "frederich": ["Frederik van Utrecht", "Frederik"],
    "fridolin": ["Fridolin van Säckingen"],
    "gertrudis": ["Gertrudis van Nijvel", "Geertrui"],
    "gommar": ["Gommarus", "Gommarus van Lier", "Gummarus"],
    "gudula-van-brussel": ["Goedele", "Sint-Goedele", "Gudula"],
    "hubertus-van-maastricht": ["Hubertus van Luik", "Hubertus"],
    "iduberga": ["Ida van Nijvel", "Itta van Nijvel"],
    "lambertus": ["Lambertus van Maastricht", "Lambert"],
    "lebuinus": ["Lebuïnus", "Lebuin"],
    "lubuinus": ["Lebuïnus", "Lebuinus"],
    "ludger": ["Liudger"],
    "medardus": ["Medardus van Noyon"],
    "oda-van-de-peel": ["Oda van Brabant"],
    "odrada": ["Odrada van Alem"],
    "plechelm-von-odilienberg": ["Plechelmus", "Plechelm"],
    "radboud": ["Radboud van Utrecht"],
    "swidbert": ["Suitbertus", "Suitbert", "Swidbertus"],
    "theodaard-van-maastricht": [
        "Theodardus",
        "Theodardus van Maastricht",
        "Theodard",
    ],
    "werenfrid": ["Werenfried van Elst", "Werenfridus", "Werenfried"],
    "winnibald": ["Wunibald", "Winebald"],
    "winnocus": ["Winnoc"],
    "wiro": ["Wiro van Roermond"],
    "woutruide": ["Waldetrudis", "Waudru"],
    "amandus-van-maastricht": ["Amandus", "Amand"],
    "ansfried-van-utrecht": ["Ansfried", "Ansfried van Utrecht"],
    "walfridus-bedum": ["Walfridus"],
    "acharius-van-doornik": ["Acharius", "Achaire"],
}


def norm(s: str) -> str:
    """Dedup-sleutel: casefold + spaties, diacritiek behouden (Lebuïnus ≠ Lebuinus)."""
    return re.sub(r"\s+", " ", s.strip().casefold())


def clean_label_name(raw: str) -> str | None:
    name = raw.strip()
    name = re.sub(r"\s*\([^)]*heilige[^)]*\)\s*", "", name, flags=re.I).strip()
    name = re.sub(r"\s+", " ", name)
    if not name:
        return None
    low = name.casefold()
    if "lijst van" in low:
        return None
    if low.startswith("saint "):
        name = name[6:].strip()
    # Engelse wiki-vormen met " of " → Nederlands " van "
    if re.search(r"\sof\s", name, flags=re.I):
        name = re.sub(r"\sof\s", " van ", name, flags=re.I)
    return name or None


def names_from_refs(refs: list) -> list[str]:
    out: list[str] = []
    for r in refs:
        if not isinstance(r, dict):
            continue
        label = r.get("label") or ""
        m = re.search(r"[—–]\s*(.+)$", label)
        if m:
            cleaned = clean_label_name(m.group(1))
            if cleaned:
                out.append(cleaned)
        url = r.get("url") or ""
        wm = re.search(r"wikipedia\.org/wiki/([^?#]+)", url)
        if wm:
            title = unquote(wm.group(1).replace("_", " "))
            cleaned = clean_label_name(title)
            if cleaned:
                out.append(cleaned)
    return out


def merge_alts(primair: str, existing: list[str], extras: list[str]) -> list[str]:
    seen = {norm(primair)}
    result: list[str] = []
    for name in existing + extras:
        cleaned = clean_label_name(name)
        if not cleaned:
            continue
        n = norm(cleaned)
        if not n or n in seen:
            continue
        seen.add(n)
        result.append(cleaned)
    return result


def yaml_scalar(s: str) -> str:
    if (
        re.search(r"[:#{}[\],&*?|>!%@`]", s)
        or "(" in s
        or ")" in s
        or "'" in s
        or '"' in s
        or s != s.strip()
    ):
        return json.dumps(s, ensure_ascii=False)
    return s


def rewrite_namen_block(text: str, primair: str, alts: list[str]) -> str:
    """Vervang alleen het namen-blok; volgende top-level key blijft intact."""
    m = re.search(r"(?m)^namen:\n", text)
    if not m:
        raise SystemExit("geen namen-blok")
    start = m.start()
    # Volgende top-level sleutel (kolom 0, letter)
    rest = text[m.end() :]
    m2 = re.search(r"(?m)^[a-zA-Z_][a-zA-Z0-9_]*:", rest)
    end = m.end() + m2.start() if m2 else len(text)
    lines = ["namen:\n", f"  primair: {yaml_scalar(primair)}\n"]
    if alts:
        lines.append("  alternatief:\n")
        for a in alts:
            lines.append(f"  - {yaml_scalar(a)}\n")
    return text[:start] + "".join(lines) + text[end:]


def main() -> None:
    changed = 0
    for path in sorted(HEILIGEN.glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        namen = data.get("namen") or {}
        primair = namen.get("primair") or ""
        existing = list(namen.get("alternatief") or [])
        from_refs = names_from_refs(data.get("referenties") or [])
        extras = EXTRA.get(path.stem, [])
        alts = merge_alts(primair, existing, from_refs + extras)
        if alts == existing:
            continue
        path.write_text(
            rewrite_namen_block(text, primair, alts), encoding="utf-8", newline="\n"
        )
        print(f"{path.stem}: {alts}")
        changed += 1
    print(f"done, {changed} files")


if __name__ == "__main__":
    main()
