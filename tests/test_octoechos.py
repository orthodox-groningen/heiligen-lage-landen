"""Toon van de week (Slavisch/Moskou): Thomaszondag = 1, Lichte Week = 1."""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from kalender import octoechos_toon, orthodox_pascha  # noqa: E402


def test_lichte_week_en_thomas_2026() -> None:
    pascha = orthodox_pascha(2026)
    assert pascha == date(2026, 4, 12)
    thomas = pascha + timedelta(days=7)
    assert thomas == date(2026, 4, 19)
    assert octoechos_toon(pascha) == 1
    assert octoechos_toon(date(2026, 4, 18)) == 1
    assert octoechos_toon(thomas) == 1
    assert octoechos_toon(date(2026, 4, 25)) == 1


def test_week_na_thomas_is_toon_2() -> None:
    assert octoechos_toon(date(2026, 4, 26)) == 2
    assert octoechos_toon(date(2026, 5, 2)) == 2
    assert octoechos_toon(date(2026, 5, 3)) == 3


def test_acht_weken_na_thomas_weer_toon_1() -> None:
    thomas = date(2026, 4, 19)
    assert octoechos_toon(thomas + timedelta(days=56)) == 1


def test_dag_voor_pascha_gebruikt_vorige_cyclus() -> None:
    assert octoechos_toon(date(2026, 4, 11)) == octoechos_toon(
        orthodox_pascha(2026) - timedelta(days=1)
    )
    assert 1 <= octoechos_toon(date(2026, 4, 11)) <= 8
