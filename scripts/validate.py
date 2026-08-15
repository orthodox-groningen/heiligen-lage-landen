"""Valideer YAML-entries tegen schema en inhoudsregels."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from load_entries import load_entries, load_raw_entries  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Valideer heiligenkalender-data.")
    parser.add_argument(
        "--schema",
        type=Path,
        default=ROOT / "schemas" / "entry.schema.json",
    )
    return parser.parse_args()


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

    for entry in entries:
        path = entry["source_path"]
        text = (entry.get("verhaal") or "").strip() or (entry.get("samenvatting") or "").strip()
        if text and not entry.get("referenties"):
            errors.append(
                f"{path}: verhaal/samenvatting aanwezig maar referenties ontbreken"
            )
        icoon = entry.get("icoon") or {}
        if icoon.get("bestand"):
            if icoon.get("rechten") != "ok":
                errors.append(
                    f"{path}: icoon.bestand gezet maar icoon.rechten is niet 'ok'"
                )
            icon_path = ROOT / "site" / "static" / icoon["bestand"]
            if not icon_path.is_file():
                errors.append(f"{path}: icoonbestand ontbreekt: {icoon['bestand']}")

    if errors:
        print(f"{len(errors)} validatiefout(en):", file=sys.stderr)
        for line in errors:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(f"OK: {len(entries)} entries gevalideerd.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
