"""Valideer YAML-entries tegen schema en inhoudsregels."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from load_entries import load_entries, load_raw_entries, load_yaml  # noqa: E402

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
SELECTIE_WAARDEN = frozenset({"voldoet", "nader-onderzoek", "kandidaat-schrappen"})
AANVULLENDE_BRON_IDS = frozenset({"wiki-heiligen", "hnet"})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Valideer heiligenkalender-data.")
    parser.add_argument(
        "--schema",
        type=Path,
        default=ROOT / "schemas" / "entry.schema.json",
    )
    return parser.parse_args()


def referentie_is_aanvullend(ref: dict[str, Any]) -> bool:
    """Wikipedia / heiligen.net mogen curated aanvullen, niet als enige bron."""
    bron = str(ref.get("bron_id") or "").strip()
    if bron in AANVULLENDE_BRON_IDS:
        return True
    url = str(ref.get("url") or "").lower()
    if "heiligen.net" in url:
        return True
    if "wikipedia.org" in url and "orthodoxwiki.org" not in url:
        return True
    label = str(ref.get("label") or "").lower()
    if "heiligen.net" in label:
        return True
    if "wikipedia" in label and "orthodoxwiki" not in label:
        return True
    return False


def collect_content_errors(entries: list[dict[str, Any]]) -> list[str]:
    """Inhoudsregels bovenop het JSON-schema."""
    errors: list[str] = []
    living_ids = {entry["id"] for entry in entries}
    seen_aliassen: dict[str, str] = {}

    for entry in entries:
        path = entry["source_path"]
        betekenis = (entry.get("betekenis_lage_landen") or "").strip()
        text = (
            (entry.get("verhaal") or "").strip()
            or (entry.get("samenvatting") or "").strip()
            or betekenis
        )
        if text and not entry.get("referenties"):
            errors.append(
                f"{path}: verhaal/samenvatting/betekenis_lage_landen aanwezig "
                "maar referenties ontbreken"
            )
        for i, ref in enumerate(entry.get("referenties") or []):
            if not (ref.get("url") or ref.get("isbn") or ref.get("locator")):
                errors.append(
                    f"{path}: referenties[{i}]: ontbreekt url, isbn of locator"
                )
        icoon = entry.get("icoon") or {}
        if icoon.get("bestand"):
            bestand = str(icoon["bestand"]).strip().replace("\\", "/")
            if bestand.lower().startswith(("http://", "https://", "//")):
                errors.append(
                    f"{path}: icoon.bestand mag geen URL zijn; "
                    "zet een lokaal bestand onder site/static/"
                )
            if icoon.get("rechten") != "ok":
                errors.append(
                    f"{path}: icoon.bestand gezet maar icoon.rechten is niet 'ok'"
                )
            if not str(icoon.get("bron") or "").strip():
                errors.append(f"{path}: icoon.bron verplicht als bestand is gezet")
            if not str(icoon.get("licentie") or "").strip():
                errors.append(
                    f"{path}: icoon.licentie verplicht als bestand is gezet"
                )
            icon_path = ROOT / "site" / "static" / bestand
            if not icon_path.is_file():
                errors.append(f"{path}: icoonbestand ontbreekt: {bestand}")

        if entry.get("soort") == "heilige":
            sel = entry.get("selectie") or "nader-onderzoek"
            if sel not in SELECTIE_WAARDEN:
                errors.append(f"{path}: onbekende selectie {sel!r}")
            if (entry.get("status") or "stub") == "curated":
                if not betekenis:
                    errors.append(
                        f"{path}: status curated vereist betekenis_lage_landen"
                    )
                refs = list(entry.get("referenties") or [])
                if refs and all(referentie_is_aanvullend(r) for r in refs):
                    errors.append(
                        f"{path}: status curated vereist minstens één bron "
                        "naast Wikipedia/heiligen.net"
                    )

        for alias in entry.get("id_aliassen") or []:
            alias_s = str(alias).strip()
            if not alias_s:
                continue
            if not ID_PATTERN.fullmatch(alias_s):
                errors.append(f"{path}: id_aliassen: ongeldig id {alias_s!r}")
                continue
            if alias_s == entry["id"]:
                errors.append(f"{path}: id_aliassen mag het eigen id niet herhalen")
                continue
            if alias_s in living_ids:
                errors.append(
                    f"{path}: id_aliassen {alias_s!r} is nog een levend entry-id"
                )
                continue
            vorige = seen_aliassen.get(alias_s)
            if vorige:
                errors.append(
                    f"{path}: id_aliassen {alias_s!r} al gebruikt door {vorige}"
                )
            else:
                seen_aliassen[alias_s] = entry["id"]

    return errors


def collect_bronnen_errors() -> list[str]:
    """Catalogus-ids in data/bronnen/bronnen.yaml moeten uniek zijn."""
    path = ROOT / "data" / "bronnen" / "bronnen.yaml"
    raw = load_yaml(path) or {}
    seen: dict[str, int] = {}
    errors: list[str] = []
    for i, item in enumerate(raw.get("bronnen") or []):
        if not isinstance(item, dict):
            errors.append(f"{path.relative_to(ROOT)}: bronnen[{i}] is geen mapping")
            continue
        bron_id = str(item.get("id") or "").strip()
        if not bron_id:
            errors.append(f"{path.relative_to(ROOT)}: bronnen[{i}]: id ontbreekt")
            continue
        vorige = seen.get(bron_id)
        if vorige is not None:
            errors.append(
                f"{path.relative_to(ROOT)}: dubbele bron_id {bron_id!r} "
                f"(eerder bronnen[{vorige}])"
            )
        else:
            seen[bron_id] = i
    return errors


def main() -> int:
    args = parse_args()
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors: list[str] = []

    for path, raw in load_raw_entries():
        for err in sorted(validator.iter_errors(raw), key=lambda e: list(e.path)):
            loc = "/".join(str(p) for p in err.path) or "(root)"
            errors.append(f"{path.relative_to(ROOT)}: {loc}: {err.message}")

    try:
        entries = load_entries()
    except Exception as exc:  # noqa: BLE001 — CLI-rapportage
        errors.append(str(exc))
        entries = []

    errors.extend(collect_content_errors(entries))
    errors.extend(collect_bronnen_errors())

    if errors:
        print(f"{len(errors)} validatiefout(en):", file=sys.stderr)
        for line in errors:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(f"OK: {len(entries)} entries gevalideerd.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
