"""Generatie van heiligenpagina’s, entries.json en beheer-selectie."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate import (  # noqa: E402
    CONTENT,
    _split_hugo_markdown,
    render_beheer_selectie,
    write_beheer_selectie,
    write_entries_json,
    write_entry_page,
    write_plaatsen_json,
)
from load_entries import load_entries  # noqa: E402


def _heilige(**overrides):
    entry = {
        "id": "voorbeeld",
        "soort": "heilige",
        "bronlaag": "encyclopedie",
        "cyclus": "jaar",
        "lage_landen": True,
        "source_path": "data/heiligen/voorbeeld.yaml",
        "namen": {"primair": "Voorbeeld", "alternatief": ["Altnaam"]},
        "datum_norm": {
            "feestdatum": "11-07",
            "vorm": "dag",
            "stijl": "gregoriaans",
        },
        "titels": [],
        "referenties": [],
        "id_aliassen": [],
        "betekenis_lage_landen": "",
        "selectie": "nader-onderzoek",
        "selectie_toelichting": "",
        "observances": ["heilige"],
        "onderdrukt_wekelijks_vasten": False,
    }
    entry.update(overrides)
    return entry


def test_entry_page_heeft_betekenis_en_aliases(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            betekenis_lage_landen="Predikte onder de Friezen.",
            id_aliassen=["oud-id"],
            selectie="voldoet",
            selectie_toelichting="niet op de publieke pagina",
        )
    )
    text = (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    meta, body = _split_hugo_markdown(text)
    assert meta["aliases"] == ["/heiligen/oud-id/"]
    assert "selectie" not in meta
    assert "niet op de publieke pagina" not in body
    assert "## Betekenis voor de Lage Landen" in body
    assert "Predikte onder de Friezen." in body
    assert "## Over de plaats in deze kalender" not in body
    assert "nagekeken aan een lexikon" not in body
    # Bronnoot ná inhoud, onder kop Over de bronnen
    assert "## Over de bronnen" in body
    assert body.index("## Betekenis voor de Lage Landen") < body.index("## Over de bronnen")
    assert body.index("## Verder lezen en kijken") < body.index("## Over de bronnen")
    assert "open naslagwerken" in body
    assert body.index("## Over de bronnen") < body.index("open naslagwerken")
    assert "## Verder lezen en kijken" in body
    assert "## Referenties" not in body
    assert "Synaxarion:" not in body


def test_entry_page_selectie_paragraaf_bij_nader_onderzoek(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="nader-onderzoek",
            selectie_toelichting="Korte beheerzin.",
            selectie_toelichting_publiek="Uitleg voor bezoekers over het grensgeval.",
        )
    )
    text = (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    meta, body = _split_hugo_markdown(text)
    assert "selectie" not in meta
    assert "## Over de plaats in deze kalender" in body
    assert "nog niet uitgemaakt" in body
    assert "Uitleg voor bezoekers over het grensgeval." in body
    assert "Korte beheerzin." not in body
    assert body.index("## Verder lezen en kijken") < body.index(
        "## Over de plaats in deze kalender"
    )


def test_entry_page_selectie_fallback_toelichting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="kandidaat-schrappen",
            selectie_toelichting="Alleen cultus, geen werk hier.",
        )
    )
    text = (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    body = _split_hugo_markdown(text)[1]
    assert "## Over de plaats in deze kalender" in body
    assert "ter discussie" in body
    assert "Alleen cultus, geen werk hier." in body


def test_entry_page_extra_yaml_veld_breekt_niet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="voldoet",
            onderzoek_notitie="Mag in YAML staan zonder render.",
        )
    )
    text = (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    assert "onderzoek_notitie" not in text
    assert "Mag in YAML staan" not in text


def test_entry_page_plaatsen_als_namen_en_rustplaats(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            locaties=["utrecht", "drongen"],
            rustplaats={
                "plaats": "echternach",
                "toelichting": "Abdij van Echternach",
            },
        )
    )
    text = (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    meta, body = _split_hugo_markdown(text)
    assert meta["locaties"] == ["Utrecht", "Drongen"]
    assert meta["locatie_ids"] == ["utrecht", "drongen"]
    assert meta["locatie_items"] == [
        {"id": "utrecht", "naam": "Utrecht", "soort": "plaats"},
        {"id": "drongen", "naam": "Drongen", "soort": "plaats"},
    ]
    assert "utrecht" not in meta["locaties"]
    assert "Utrecht" in meta["locatie_zoek"]
    assert "Vlaanderen" in meta["locatie_zoek"]
    assert meta["rustplaats_plaats"] == "Echternach"
    assert meta["rustplaats_toelichting"] == "Abdij van Echternach"
    # Plaatsen/rustplaats horen in de Hugo-infobox (front matter), niet in de body.
    assert "**Plaatsen:**" not in body
    assert "**Rustplaats:**" not in body
    assert "[7 november](/datum/?dag=11-07)" in body or "**Feestdag:**" in body


def test_entry_page_infobox_velden_in_front_matter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="voldoet",
            titels=["Apostel van de Friezen"],
            periode="658–739",
            vastenniveau="vis",
            onderdrukt_wekelijks_vasten=True,
        )
    )
    text = (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    meta, body = _split_hugo_markdown(text)
    assert meta["titels"] == ["Apostel van de Friezen"]
    assert meta["periode"] == "658–739"
    assert meta["vastenniveau"] == "vis"
    assert meta["onderdrukt_wekelijks_vasten"] is True
    assert meta["feestdatum"] == "11-07"
    assert "*Apostel van de Friezen*" not in body
    assert "**Periode:**" not in body
    assert "**Vastenniveau" not in body


def test_entry_page_referentie_inhoud_wint_van_opmerking(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="voldoet",
            betekenis_lage_landen="Werkte hier.",
            referenties=[
                {
                    "label": "Lexikon",
                    "url": "https://example.org/lex",
                    "geraadpleegd": "2026-08-20",
                    "inhoud": "Lexikonvita over de Friese missie.",
                    "opmerking": "interne notitie niet tonen",
                }
            ],
        )
    )
    body = _split_hugo_markdown(
        (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    )[1]
    assert "## Verder lezen en kijken" in body
    assert "Lexikonvita over de Friese missie." in body
    assert "interne notitie niet tonen" not in body
    assert "geraadpleegd 2026-08-20" in body


def test_entry_page_selectie_na_verhaal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="nader-onderzoek",
            selectie_toelichting="Grensgeval.",
            betekenis_lage_landen="Indirecte rol.",
            verhaal="Korte vita.",
        )
    )
    body = _split_hugo_markdown(
        (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    )[1]
    assert body.index("## Betekenis voor de Lage Landen") < body.index("## Verhaal")
    assert body.index("## Verhaal") < body.index("## Verder lezen en kijken")
    assert body.index("## Verder lezen en kijken") < body.index(
        "## Over de plaats in deze kalender"
    )


def test_entry_page_feestdag_link_en_geen_synaxarion_voet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(_heilige(selectie="voldoet"))
    meta, body = _split_hugo_markdown(
        (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    )
    assert meta["feestdatum"] == "11-07"
    assert "**Feestdag:** [7 november](/datum/?dag=11-07)" in body
    assert "Synaxarion:" not in body
    assert "/synaxarion/" not in body


def test_entry_page_over_bronnen_toelichting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            selectie="voldoet",
            over_bronnen="De vita van X is de hoofdbron.",
        )
    )
    body = _split_hugo_markdown(
        (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    )[1]
    assert "## Over de bronnen" in body
    assert "De vita van X is de hoofdbron." in body
    assert body.index("De vita van X is de hoofdbron.") < body.index("**Bron:**")


def test_entry_page_nagekeken_bronzin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            bronlaag="nagekeken",
            betekenis_lage_landen="Predikte onder de Friezen.",
            verhaal="Een vita.",
        )
    )
    text = (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    assert "nagekeken aan een lexikon" in text
    assert "open naslagwerken" not in text
    assert "Deze pagina is nog een stub" not in text


def test_entry_page_icoon_alleen_bij_rechten_ok(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_entry_page(
        _heilige(
            icoon={
                "bestand": "iconen/willibrord.jpg",
                "rechten": "ok",
                "bron": "Wikimedia Commons",
                "licentie": "Publiek domein",
            }
        )
    )
    meta, _body = _split_hugo_markdown(
        (content / "heiligen" / "voorbeeld.md").read_text(encoding="utf-8")
    )
    assert meta["icoon"] == "/iconen/willibrord.jpg"
    assert meta["icoon_bron"] == "Wikimedia Commons"
    assert meta["icoon_licentie"] == "Publiek domein"
    write_entry_page(
        _heilige(
            id="zonder",
            icoon={"bestand": "iconen/x.jpg", "rechten": "onbekend"},
        )
    )
    meta2, _ = _split_hugo_markdown(
        (content / "heiligen" / "zonder.md").read_text(encoding="utf-8")
    )
    assert "icoon" not in meta2


def test_entries_json_heeft_betekenis_alleen_bij_heiligen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    static = tmp_path / "static" / "data"
    monkeypatch.setattr("generate.STATIC_DATA", static)
    heilige = _heilige(
        betekenis_lage_landen="Voor de Lage Landen.",
        locaties=["utrecht"],
        rustplaats={"plaats": "echternach", "toelichting": "Abdij"},
    )
    feest = {
        **_heilige(id="kerst", soort="feest"),
        "namen": {"primair": "Kerst", "alternatief": []},
        "source_path": "data/feesten/kerst.yaml",
        "observances": ["feest"],
        "betekenis_lage_landen": "",
    }
    write_entries_json([heilige, feest])
    payload = json.loads((static / "entries.json").read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in payload}
    assert by_id["voorbeeld"]["betekenis_lage_landen"] == "Voor de Lage Landen."
    assert "betekenis_lage_landen" not in by_id["kerst"]
    assert "selectie" not in by_id["voorbeeld"]
    assert by_id["voorbeeld"]["bronlaag"] == "encyclopedie"
    assert by_id["voorbeeld"]["locaties"] == ["utrecht"]
    assert by_id["voorbeeld"]["rustplaats"]["plaats"] == "echternach"
    assert "locaties" not in by_id["kerst"]


def test_beheer_selectie_groepeert_en_toont_toelichting() -> None:
    body = render_beheer_selectie(
        [
            _heilige(
                id="willibrord",
                namen={"primair": "Willibrord", "alternatief": []},
                selectie="voldoet",
                source_path="data/heiligen/willibrord.yaml",
            ),
            _heilige(
                id="fridolin",
                namen={"primair": "Fridolin", "alternatief": []},
                selectie="kandidaat-schrappen",
                selectie_toelichting="Vooral Boven-Rijn.",
                source_path="data/heiligen/fridolin.yaml",
            ),
            _heilige(
                id="bavo",
                namen={"primair": "Bavo", "alternatief": []},
                source_path="data/heiligen/bavo.yaml",
            ),
        ]
    )
    assert "## Voldoet (1)" in body
    assert "[Willibrord](/heiligen/willibrord/)" in body
    assert "## Nader onderzoek (1)" in body
    assert "[Bavo](/heiligen/bavo/)" in body
    assert "## Kandidaat om te schrappen (1)" in body
    assert "Vooral Boven-Rijn." in body


def test_write_beheer_selectie_naar_beheer_map(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = tmp_path / "content"
    monkeypatch.setattr("generate.CONTENT", content)
    write_beheer_selectie(load_entries())
    path = content / "beheer" / "selectie.md"
    meta, body = _split_hugo_markdown(path.read_text(encoding="utf-8"))
    assert meta["title"] == "Selectie heiligen"
    assert meta["generator"] == "scripts/generate.py"
    assert "Willibrord" in body
    assert "Nader onderzoek" in body
    assert "lubuinus.yaml" not in body
    assert "alberik.yaml" not in body
    assert "lebuinus.yaml" in body
    assert "albericus-van-utrecht.yaml" in body
    heiligen = [e for e in load_entries() if e["soort"] == "heilige"]
    n_voldoet = sum(1 for e in heiligen if e["selectie"] == "voldoet")
    n_nader = sum(1 for e in heiligen if e["selectie"] == "nader-onderzoek")
    n_kand = sum(1 for e in heiligen if e["selectie"] == "kandidaat-schrappen")
    assert f"## Voldoet ({n_voldoet})" in body
    assert f"## Nader onderzoek ({n_nader})" in body
    assert f"## Kandidaat om te schrappen ({n_kand})" in body
    assert "Rath Melsigi" in body


def test_heiligen_list_layout_zoekt_alternatieve_namen() -> None:
    layout = (ROOT / "site" / "layouts" / "heiligen" / "list.html").read_text(
        encoding="utf-8"
    )
    assert "heiligen-zoek" in layout
    assert "alternatief" in layout
    assert "entry-filter.js" in layout
    assert "heiligen-kaart" in layout
    assert "locatie_zoek" in layout
    assert "vendor/leaflet/leaflet.js" in layout
    js = (ROOT / "site" / "assets" / "js" / "entry-filter.js").read_text(
        encoding="utf-8"
    )
    assert "data-zoek" in js
    assert "toLocaleLowerCase" in js
    assert 'params.get("plaats")' in js
    assert "heiligen-filter" in js
    kaart = (ROOT / "site" / "assets" / "js" / "heiligen-kaart.js").read_text(
        encoding="utf-8"
    )
    assert "plaatsen.json" in kaart
    assert "tile.openstreetmap.org" in kaart
    assert "unpkg.com" not in kaart


def test_write_plaatsen_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    static = tmp_path / "static" / "data"
    monkeypatch.setattr("generate.STATIC_DATA", static)
    write_plaatsen_json()
    payload = json.loads((static / "plaatsen.json").read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in payload}
    assert by_id["utrecht"]["naam"] == "Utrecht"
    assert by_id["vlaanderen"]["soort"] == "streek"
    assert "lat" in by_id["utrecht"] and "lon" in by_id["utrecht"]
