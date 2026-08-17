"""CI, parochie-default en broncatalogus (stap 8)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from load_entries import load_yaml  # noqa: E402
from validate import collect_bronnen_errors  # noqa: E402


def test_pages_yml_draait_pytest_voor_generate() -> None:
    text = (ROOT / ".github" / "workflows" / "pages.yml").read_text(
        encoding="utf-8"
    )
    pytest_at = text.find("python -m pytest -q")
    generate_at = text.find("python scripts/generate.py --clean")
    assert pytest_at != -1
    assert generate_at != -1
    assert pytest_at < generate_at


def test_validate_yml_draait_pytest() -> None:
    text = (ROOT / ".github" / "workflows" / "validate.yml").read_text(
        encoding="utf-8"
    )
    assert "python -m pytest -q" in text


def test_lezingen_default_is_den_haag_niet_groningen() -> None:
    cfg = load_yaml(ROOT / "data" / "lezingen" / "config.yaml")
    assert cfg["parochie"] == "den-haag"
    groningen = ROOT / "data" / "lezingen" / "parochies" / "groningen.yaml"
    assert groningen.is_file()
    raw = load_yaml(groningen)
    assert raw["parochie"] == "groningen"
    assert list(raw.get("overrides") or []) == []


def test_bronnen_catalogus_unieke_ids() -> None:
    assert collect_bronnen_errors() == []
    items = load_yaml(ROOT / "data" / "bronnen" / "bronnen.yaml")["bronnen"]
    ids = [item["id"] for item in items]
    assert "orthodoxwiki-pascha-note" not in ids
    assert ids.count("orthodoxwiki-pascha") == 1
    assert ids.count("oca-calendar") == 1
