"""Inhoudsregels van scripts/validate.py."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from load_entries import load_entries  # noqa: E402
from validate import collect_content_errors, referentie_is_aanvullend  # noqa: E402


def _heilige(**overrides):
    base = {
        "id": "voorbeeld",
        "soort": "heilige",
        "bronlaag": "encyclopedie",
        "source_path": "data/heiligen/voorbeeld.yaml",
        "referenties": [],
        "id_aliassen": [],
        "betekenis_lage_landen": "",
        "selectie": "nader-onderzoek",
    }
    base.update(overrides)
    return base


def test_aanvullende_bron_wikipedia_niet_orthodoxwiki() -> None:
    assert referentie_is_aanvullend(
        {"label": "Wikipedia (NL)", "url": "https://nl.wikipedia.org/wiki/X"}
    )
    assert referentie_is_aanvullend(
        {"bron_id": "hnet", "url": "https://www.heiligen.net/x"}
    )
    assert not referentie_is_aanvullend(
        {"label": "OrthodoxWiki", "url": "https://orthodoxwiki.org/Willibrord"}
    )
    assert not referentie_is_aanvullend(
        {"bron_id": "oca-calendar", "url": "https://www.oca.org/saints/lives"}
    )


def test_nagekeken_heilige_zonder_betekenis_faalt() -> None:
    errors = collect_content_errors(
        [
            _heilige(
                bronlaag="nagekeken",
                referenties=[
                    {
                        "label": "OrthodoxWiki",
                        "url": "https://orthodoxwiki.org/X",
                    }
                ],
            )
        ]
    )
    assert any("betekenis_lage_landen" in e for e in errors)


def test_nagekeken_heilige_alleen_wikipedia_faalt() -> None:
    errors = collect_content_errors(
        [
            _heilige(
                bronlaag="nagekeken",
                betekenis_lage_landen="Werkte onder de Friezen.",
                referenties=[
                    {
                        "label": "Wikipedia (NL) — X",
                        "url": "https://nl.wikipedia.org/wiki/X",
                    }
                ],
            )
        ]
    )
    assert any("Wikipedia/heiligen.net" in e for e in errors)


def test_nagekeken_heilige_met_betekenis_en_orthodoxwiki_ok() -> None:
    errors = collect_content_errors(
        [
            _heilige(
                bronlaag="nagekeken",
                betekenis_lage_landen="Apostel van de Friezen.",
                referenties=[
                    {
                        "label": "OrthodoxWiki",
                        "url": "https://orthodoxwiki.org/Willibrord",
                    }
                ],
            )
        ]
    )
    assert errors == []


def test_betekenis_zonder_referenties_faalt() -> None:
    errors = collect_content_errors(
        [_heilige(betekenis_lage_landen="Iets zonder bron.")]
    )
    assert any("referenties ontbreken" in e for e in errors)


def test_id_alias_niet_eigen_id_en_niet_levend() -> None:
    a = _heilige(id="lebuinus", id_aliassen=["lebuinus"])
    b = _heilige(
        id="lubuinus",
        source_path="data/heiligen/lubuinus.yaml",
        id_aliassen=[],
    )
    errors = collect_content_errors([a, b])
    assert any("eigen id" in e for e in errors)

    a2 = _heilige(id="lebuinus", id_aliassen=["lubuinus"])
    errors2 = collect_content_errors([a2, b])
    assert any("levend entry-id" in e for e in errors2)


def test_bestaande_heiligen_laden_met_selectie() -> None:
    by_id = {e["id"]: e for e in load_entries() if e["soort"] == "heilige"}
    assert by_id["willibrord"]["bronlaag"] == "nagekeken"
    assert by_id["willibrord"]["selectie"] == "voldoet"
    assert by_id["willibrord"]["betekenis_lage_landen"]
