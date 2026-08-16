"""Vul ontbrekende url/isbn/locator in referenties vanuit bronnen.yaml.

Herschrijft alleen ontbrekende locator-regels; laat overige YAML-opmaak intact.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

BRON_LINE = re.compile(r"^(\s*)- bron_id:\s*(\S+)\s*$")
LOCATOR_LINE = re.compile(r"^\s+(url|isbn|locator)\s*:")


def load_bronnen() -> dict[str, dict]:
    raw = yaml.safe_load((DATA / "bronnen" / "bronnen.yaml").read_text(encoding="utf-8"))
    return {b["id"]: b for b in (raw.get("bronnen") or [])}


def enrich_text(text: str, bronnen: dict[str, dict]) -> tuple[str, int]:
    lines = text.splitlines()
    out: list[str] = []
    added = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        m = BRON_LINE.match(line)
        if not m:
            out.append(line)
            i += 1
            continue
        indent, bron_id = m.group(1), m.group(2)
        out.append(line)
        i += 1
        block: list[str] = []
        while i < len(lines):
            nxt = lines[i]
            if BRON_LINE.match(nxt) or (
                nxt.strip()
                and not nxt.startswith(" ")
                and not nxt.startswith("\t")
            ):
                break
            if nxt.startswith(indent + " ") or nxt.startswith(indent + "\t") or nxt == "":
                # Nog onderdeel van deze referentie zolang dieper geïndenteerd.
                if nxt and not (nxt.startswith(indent + " ") or nxt.startswith(indent + "\t")):
                    break
                block.append(nxt)
                i += 1
                continue
            break
        has_locator = any(LOCATOR_LINE.match(b) for b in block)
        if not has_locator:
            bron = bronnen.get(bron_id)
            field_indent = indent + "  "
            if bron and bron.get("url"):
                out.append(f'{field_indent}url: "{bron["url"]}"')
                added += 1
            elif bron and bron.get("opmerking"):
                note = bron["opmerking"].replace('"', '\\"')
                out.append(f'{field_indent}locator: "{note}"')
                added += 1
            elif bron and bron.get("naam"):
                out.append(
                    f'{field_indent}locator: "Broncatalogus: {bron["naam"]} (id {bron_id})"'
                )
                added += 1
        out.extend(block)
    ending = "\n" if text.endswith("\n") else ""
    return "\n".join(out) + ending, added


def main() -> int:
    bronnen = load_bronnen()
    total = 0
    files = 0
    for sub in ("feesten", "heiligen"):
        for path in sorted((DATA / sub).glob("*.yaml")):
            original = path.read_text(encoding="utf-8")
            updated, n = enrich_text(original, bronnen)
            if n:
                path.write_text(updated, encoding="utf-8", newline="\n")
                files += 1
                total += n
                print(f"{path.relative_to(ROOT)} (+{n})")
    print(f"Klaar: {total} locator(s) in {files} bestand(en).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
