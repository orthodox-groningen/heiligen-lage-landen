"""Schrijf data/feesten/*.yaml voor paascyclus-catalogus."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from paascyclus_catalogus import DEFAULT_REFS, PAASCYCLUS  # noqa: E402

OUT = ROOT / "data" / "feesten"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for item in PAASCYCLUS:
        lines: list[str] = [
            f"id: {item['id']}",
            "soort: feest",
            "status: curated",
            "cyclus: paascyclus",
            "lage_landen: false",
            "namen:",
            f'  primair: "{item["namen"]["primair"]}"',
        ]
        if item["namen"].get("alternatief"):
            lines.append("  alternatief:")
            for alt in item["namen"]["alternatief"]:
                lines.append(f'    - "{alt}"')
        lines.append("observances:")
        for obs in item["observances"]:
            lines.append(f"  - {obs}")
        lines.extend(
            [
                "datum:",
                "  stijl: gregoriaans",
                "  paascyclus:",
                "    anker: pascha",
                f"    offset_dagen: {item['offset_dagen']}",
                "samenvatting: |",
            ]
        )
        for ln in item["samenvatting"].strip().splitlines():
            lines.append(f"  {ln}")
        lines.append("verhaal: |")
        for ln in item["verhaal"].strip().splitlines():
            lines.append(f"  {ln}")
        lines.append("referenties:")
        for ref in DEFAULT_REFS:
            lines.append(f"  - bron_id: {ref['bron_id']}")
            if ref.get("url"):
                lines.append(f'    url: "{ref["url"]}"')
            if ref.get("isbn"):
                lines.append(f'    isbn: "{ref["isbn"]}"')
            if ref.get("locator"):
                lines.append(f'    locator: "{ref["locator"]}"')
            lines.append(f'    geraadpleegd: "{ref["geraadpleegd"]}"')
        lines.append("")
        path = OUT / f"{item['id']}.yaml"
        path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
