"""Pas beste geverifieerde URLs toe op heiligen-referenties."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
HEILIGEN = ROOT / "data" / "heiligen"
REF_DATE = "2026-08-16"
EIR3_LOCATOR = "Interne notities; nader te specificeren in curated entries."

# Per id: lijst (label, url) — alleen HTTP-200 geverifieerd.
BESTE: dict[str, list[tuple[str, str]]] = {
    "acharius-van-doornik": [
        ("Wikipedia (NL) — Acharius", "https://nl.wikipedia.org/wiki/Acharius"),
    ],
    "adela-van-vlaanderen": [
        ("Wikipedia (NL) — Adela van Mesen", "https://nl.wikipedia.org/wiki/Adela_van_Mesen"),
    ],
    "adelbert": [
        (
            "Wikipedia (NL) — Adelbert van Egmond",
            "https://nl.wikipedia.org/wiki/Adelbert_van_Egmond",
        ),
        (
            "Heiligenlexikon — Adelbert van Egmond",
            "https://www.heiligenlexikon.de/BiographienA/Adalbert_von_Egmond.html",
        ),
    ],
    "adelgonda": [
        (
            "Wikipedia (NL) — Aldegonda van Maubeuge",
            "https://nl.wikipedia.org/wiki/Aldegonda_van_Maubeuge",
        ),
        (
            "heiligen.net — Aldegondis",
            "https://www.heiligen.net/heiligen/01/30/01-30-0684-aldegondis.php",
        ),
    ],
    "agricolaus-van-maastricht": [
        (
            "Wikipedia (NL) — Lijst van bisschoppen van Maastricht",
            "https://nl.wikipedia.org/wiki/Lijst_van_bisschoppen_van_Maastricht",
        ),
    ],
    "albericus-van-utrecht": [
        (
            "Wikipedia (NL) — Alberik I van Utrecht",
            "https://nl.wikipedia.org/wiki/Alberik_I_van_Utrecht",
        ),
    ],
    "alberik": [
        (
            "Wikipedia (NL) — Alberik I van Utrecht",
            "https://nl.wikipedia.org/wiki/Alberik_I_van_Utrecht",
        ),
    ],
    "alena-van-dilbeek": [
        ("Wikipedia (NL) — Alena (heilige)", "https://nl.wikipedia.org/wiki/Alena_(heilige)"),
    ],
    "amalberga-van-susteren": [
        (
            "heiligen.net — Amalberga",
            "https://www.heiligen.net/heiligen/11/21/11-21-0900-amalberga.php",
        ),
    ],
    "amalberga-van-temse": [
        (
            "Wikipedia (NL) — Amalberga van Temse",
            "https://nl.wikipedia.org/wiki/Amalberga_van_Temse",
        ),
        (
            "heiligen.net — Amalberga",
            "https://www.heiligen.net/heiligen/07/10/07-10-0772-amalberga.php",
        ),
    ],
    "amandus-van-maastricht": [
        ("Wikipedia (NL) — Amandus", "https://nl.wikipedia.org/wiki/Amandus"),
    ],
    "ansfried-van-utrecht": [
        ("Wikipedia (NL) — Ansfried", "https://nl.wikipedia.org/wiki/Ansfried"),
        (
            "heiligen.net — Ansfried",
            "https://www.heiligen.net/heiligen/05/03/05-03-1010-ansfried.php",
        ),
    ],
    "aubertus-van-kamerijk": [
        (
            "Wikipedia (NL) — Autbertus van Kamerijk",
            "https://nl.wikipedia.org/wiki/Autbertus_van_Kamerijk",
        ),
    ],
    "bavo": [
        ("Wikipedia (NL) — Bavo van Gent", "https://nl.wikipedia.org/wiki/Bavo_van_Gent"),
    ],
    "bernulphus": [
        ("Wikipedia (NL) — Bernulphus", "https://nl.wikipedia.org/wiki/Bernulphus"),
    ],
    "bonifatius": [
        (
            "Wikipedia (NL) — Bonifatius (heilige)",
            "https://nl.wikipedia.org/wiki/Bonifatius_(heilige)",
        ),
        (
            "heiligen.net — Bonifatius",
            "https://www.heiligen.net/heiligen/06/05/06-05-0754-bonifatius.php",
        ),
        ("OrthodoxWiki — Bonifatius", "https://orthodoxwiki.org/Boniface"),
        (
            "Heiligenlexikon — Bonifatius",
            "https://www.heiligenlexikon.de/BiographienB/Bonifatius.html",
        ),
    ],
    "cunera": [
        ("Wikipedia (NL) — Cunera", "https://nl.wikipedia.org/wiki/Cunera"),
    ],
    "domitianus": [
        (
            "Wikipedia (NL) — Domitianus van Hoei",
            "https://nl.wikipedia.org/wiki/Domitianus_van_Hoei",
        ),
    ],
    "dymphna": [
        ("Wikipedia (NL) — Dymphna", "https://nl.wikipedia.org/wiki/Dymphna"),
        ("OrthodoxWiki — Dymphna", "https://orthodoxwiki.org/Dymphna"),
    ],
    "egbert-van-rathmelsigi": [
        (
            "Wikipedia (NL) — Egbert van Rathmelsigi",
            "https://nl.wikipedia.org/wiki/Egbert_van_Rathmelsigi",
        ),
    ],
    "eligius": [
        ("Wikipedia (NL) — Eligius", "https://nl.wikipedia.org/wiki/Eligius"),
    ],
    "engelmund": [
        ("Wikipedia (NL) — Engelmundus", "https://nl.wikipedia.org/wiki/Engelmundus"),
        (
            "heiligen.net — Engelmundus",
            "https://www.heiligen.net/heiligen/06/21/06-21-0739-engelmundus.php",
        ),
    ],
    "ermelindis": [
        (
            "Wikipedia (NL) — Ermelindis van Meldert",
            "https://nl.wikipedia.org/wiki/Ermelindis_van_Meldert",
        ),
    ],
    "floribert": [
        (
            "Wikipedia (NL) — Floribertus van Luik",
            "https://nl.wikipedia.org/wiki/Floribertus_van_Luik",
        ),
    ],
    "foillan": [
        ("Wikipedia (NL) — Foillan", "https://nl.wikipedia.org/wiki/Foillan"),
    ],
    "folciunus": [
        ("Wikipedia (NL) — Folcuin", "https://nl.wikipedia.org/wiki/Folcuin"),
        ("Wikipedia (EN) — Folcuin", "https://en.wikipedia.org/wiki/Folcwin"),
    ],
    "frederich": [
        (
            "Wikipedia (NL) — Frederik van Utrecht",
            "https://nl.wikipedia.org/wiki/Frederik_van_Utrecht",
        ),
    ],
    "fridolin": [
        (
            "Wikipedia (NL) — Fridolin van Säckingen",
            "https://nl.wikipedia.org/wiki/Fridolin_van_S%C3%A4ckingen",
        ),
    ],
    "gertrudis": [
        (
            "Wikipedia (NL) — Gertrudis van Nijvel",
            "https://nl.wikipedia.org/wiki/Gertrudis_van_Nijvel",
        ),
    ],
    "gommar": [
        (
            "Wikipedia (NL) — Gommarus van Lier",
            "https://nl.wikipedia.org/wiki/Gommarus_van_Lier",
        ),
    ],
    "gregorius-van-utrecht": [
        (
            "Wikipedia (NL) — Gregorius van Utrecht",
            "https://nl.wikipedia.org/wiki/Gregorius_van_Utrecht",
        ),
        (
            "heiligen.net — Gregorius",
            "https://www.heiligen.net/heiligen/08/25/08-25-0775-gregorius.php",
        ),
    ],
    "gudula-van-brussel": [
        ("Wikipedia (NL) — Sint-Goedele", "https://nl.wikipedia.org/wiki/Sint-Goedele"),
        (
            "heiligen.net — Goedele",
            "https://www.heiligen.net/heiligen/01/08/01-08-0712-goedele.php",
        ),
    ],
    "hubertus-van-maastricht": [
        (
            "Wikipedia (NL) — Hubertus van Luik",
            "https://nl.wikipedia.org/wiki/Hubertus_van_Luik",
        ),
        (
            "heiligen.net — Hubertus",
            "https://www.heiligen.net/heiligen/11/03/11-03-0727-hubertus.php",
        ),
    ],
    "hunger-van-utrecht": [
        (
            "Wikipedia (NL) — Hunger van Utrecht",
            "https://nl.wikipedia.org/wiki/Hunger_van_Utrecht",
        ),
        (
            "heiligen.net — Hunger",
            "https://www.heiligen.net/heiligen/12/22/12-22-0866-hunger.php",
        ),
    ],
    "iduberga": [
        ("Wikipedia (NL) — Iduberga", "https://nl.wikipedia.org/wiki/Iduberga"),
        ("Wikipedia (NL) — Ida van Nijvel", "https://nl.wikipedia.org/wiki/Ida_van_Nijvel"),
    ],
    "jeroen-van-noordwijk": [
        (
            "Wikipedia (NL) — Jeroen van Noordwijk",
            "https://nl.wikipedia.org/wiki/Jeroen_van_Noordwijk",
        ),
        (
            "heiligen.net — Jeroen",
            "https://www.heiligen.net/heiligen/08/17/08-17-0856-jeroen.php",
        ),
    ],
    "lambertus": [
        (
            "Wikipedia (NL) — Lambertus van Maastricht",
            "https://nl.wikipedia.org/wiki/Lambertus_van_Maastricht",
        ),
        (
            "heiligen.net — Lambertus",
            "https://www.heiligen.net/heiligen/09/17/09-17-0705-lambertus.php",
        ),
    ],
    "lebuinus": [
        ("Wikipedia (NL) — Lebuïnus", "https://nl.wikipedia.org/wiki/Lebu%C3%AFnus"),
    ],
    "lubuinus": [
        ("Wikipedia (NL) — Lebuïnus", "https://nl.wikipedia.org/wiki/Lebu%C3%AFnus"),
    ],
    "ludger": [
        ("Wikipedia (NL) — Ludger", "https://nl.wikipedia.org/wiki/Ludger"),
        (
            "heiligen.net — Ludger",
            "https://www.heiligen.net/heiligen/03/26/03-26-0809-ludger.php",
        ),
    ],
    "medardus": [
        (
            "Wikipedia (NL) — Medardus van Noyon",
            "https://nl.wikipedia.org/wiki/Medardus_van_Noyon",
        ),
    ],
    "oda-van-amay": [
        ("Wikipedia (NL) — Oda van Amay", "https://nl.wikipedia.org/wiki/Oda_van_Amay"),
    ],
    "oda-van-de-peel": [
        ("Wikipedia (NL) — Oda van Brabant", "https://nl.wikipedia.org/wiki/Oda_van_Brabant"),
    ],
    "odrada": [
        ("Wikipedia (NL) — Odrada van Alem", "https://nl.wikipedia.org/wiki/Odrada_van_Alem"),
    ],
    "plechelm-von-odilienberg": [
        ("Wikipedia (NL) — Plechelmus", "https://nl.wikipedia.org/wiki/Plechelmus"),
    ],
    "quirillus-van-tongern": [
        ("Wikipedia (NL) — Quirillus", "https://nl.wikipedia.org/wiki/Quirillus"),
    ],
    "radboud": [
        (
            "Wikipedia (NL) — Radboud van Utrecht",
            "https://nl.wikipedia.org/wiki/Radboud_van_Utrecht",
        ),
        (
            "heiligen.net — Radboud",
            "https://www.heiligen.net/heiligen/11/29/11-29-0917-radboud.php",
        ),
    ],
    "remaclus": [
        ("Wikipedia (NL) — Remaclus", "https://nl.wikipedia.org/wiki/Remaclus"),
    ],
    "swidbert": [
        ("Wikipedia (NL) — Suitbertus", "https://nl.wikipedia.org/wiki/Suitbertus"),
    ],
    "theodaard-van-maastricht": [
        ("Wikipedia (NL) — Theodardus", "https://nl.wikipedia.org/wiki/Theodardus"),
        (
            "Wikipedia (EN) — Theodardus van Maastricht",
            "https://en.wikipedia.org/wiki/Theodard_of_Maastricht",
        ),
    ],
    "trudo": [
        ("Wikipedia (NL) — Trudo", "https://nl.wikipedia.org/wiki/Trudo"),
    ],
    "ultan": [
        ("Wikipedia (EN) — Ultan", "https://en.wikipedia.org/wiki/Saint_Ultan"),
        (
            "heiligen.net — Ultan",
            "https://www.heiligen.net/heiligen/05/02/05-02-0686-ultan.php",
        ),
    ],
    "walburga": [
        ("Wikipedia (NL) — Walburga", "https://nl.wikipedia.org/wiki/Walburga"),
    ],
    "walfridus-bedum": [
        ("Wikipedia (NL) — Walfridus", "https://nl.wikipedia.org/wiki/Walfridus"),
    ],
    "werenfrid": [
        (
            "Wikipedia (NL) — Werenfried van Elst",
            "https://nl.wikipedia.org/wiki/Werenfried_van_Elst",
        ),
        (
            "heiligen.net — Werenfridus",
            "https://www.heiligen.net/heiligen/08/14/08-14-0760-werenfridus.php",
        ),
    ],
    "willibrord": [
        ("Wikipedia (NL) — Willibrord", "https://nl.wikipedia.org/wiki/Willibrord"),
        (
            "heiligen.net — Willibrord",
            "https://www.heiligen.net/heiligen/11/07/11-07-0739-willibrord.php",
        ),
        ("OrthodoxWiki — Willibrord", "https://orthodoxwiki.org/Willibrord"),
    ],
    "winnibald": [
        ("Wikipedia (NL) — Winnibald", "https://nl.wikipedia.org/wiki/Winnibald"),
        ("Wikipedia (NL) — Wunibald", "https://nl.wikipedia.org/wiki/Wunibald"),
    ],
    "winnocus": [
        ("Wikipedia (EN) — Winnoc", "https://en.wikipedia.org/wiki/Saint_Winnoc"),
    ],
    "wiro": [
        (
            "Wikipedia (NL) — Wiro van Roermond",
            "https://nl.wikipedia.org/wiki/Wiro_van_Roermond",
        ),
    ],
    "woutruide": [
        ("Wikipedia (NL) — Waldetrudis", "https://nl.wikipedia.org/wiki/Waldetrudis"),
    ],
    "wulfram": [
        ("Wikipedia (NL) — Wulfram", "https://nl.wikipedia.org/wiki/Wulfram"),
        (
            "heiligen.net — Wulfram",
            "https://www.heiligen.net/heiligen/03/20/03-20-0720-wulfram.php",
        ),
    ],
}


def write_refs(path: Path, refs: list[dict]) -> None:
    text = path.read_text(encoding="utf-8")
    head, sep, _tail = text.partition("referenties:")
    if not sep:
        raise SystemExit(f"geen referenties: {path}")
    lines = ["referenties:"]
    for r in refs:
        if "label" in r:
            lines.append(f'  - label: "{r["label"]}"')
            lines.append(f'    url: "{r["url"]}"')
            lines.append(f'    geraadpleegd: "{r.get("geraadpleegd", REF_DATE)}"')
        elif r.get("bron_id") == "eir3app":
            lines.append("  - bron_id: eir3app")
            lines.append(f'    locator: "{r.get("locator", EIR3_LOCATOR)}"')
            lines.append(f'    geraadpleegd: "{r.get("geraadpleegd", REF_DATE)}"')
        else:
            raise SystemExit(f"onverwachte ref in {path}: {r}")
    lines.append("")
    path.write_text(head + "\n".join(lines), encoding="utf-8", newline="\n")


def main() -> None:
    changed = 0
    for path in sorted(HEILIGEN.glob("*.yaml")):
        hid = path.stem
        specific = BESTE.get(hid)
        refs: list[dict] = []
        if specific:
            for label, url in specific:
                refs.append({"label": label, "url": url, "geraadpleegd": REF_DATE})
        else:
            # Geen specifieke pagina gevonden: eir3app-locator behouden.
            refs.append(
                {
                    "bron_id": "eir3app",
                    "locator": EIR3_LOCATOR,
                    "geraadpleegd": REF_DATE,
                }
            )
        write_refs(path, refs)
        print("updated", hid, f"({len(refs)} refs)")
        changed += 1
    print(f"done, {changed} files")


if __name__ == "__main__":
    main()
