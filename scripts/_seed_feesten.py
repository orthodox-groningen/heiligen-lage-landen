from pathlib import Path

root = Path(__file__).resolve().parents[1] / "data" / "feesten"
root.mkdir(parents=True, exist_ok=True)

feesten = [
    (
        "besnijdenis-des-heren",
        "Besnijdenis des Heren",
        "01-01",
        "Het feest van de Besnijdenis des Heren volgens de vaste jaarcyclus.",
        "Het Kind Jezus wordt volgens de wet van Mozes besneden op de achtste dag na Zijn geboorte. In de orthodoxe traditie valt dit feest op 1 januari volgens de Juliaanse kalenderrekening van de vaste cyclus.",
    ),
    (
        "theofanie",
        "Theofanie (Doop des Heren)",
        "01-06",
        "Openbaring van de Heilige Drie-eenheid bij de doop van Christus in de Jordaan.",
        "Bij de doop van Christus in de Jordaan openbaart God zich als Vader (stem), Zoon (Christus) en Heilige Geest (duif). Theofanie is een van de grote vaste feesten.",
    ),
    (
        "ontmoeting-in-de-tempel",
        "Ontmoeting in de Tempel",
        "02-02",
        "Christus wordt in de tempel gebracht; Simeon en Anna begroeten Hem.",
        "Veertig dagen na Kerst wordt het Kind naar de tempel gebracht. De rechtvaardige Simeon herkent Hem als het heil van God.",
    ),
    (
        "aankondiging",
        "Aankondiging aan de Moeder Gods",
        "03-25",
        "De aartsengel Gabriël kondigt de geboorte van Christus aan Maria aan.",
        "Op dit feest wordt herdacht dat Maria ja zegt op Gods uitnodiging; het Woord wordt vlees.",
    ),
    (
        "geboorte-johannes-doper",
        "Geboorte van Johannes de Doper",
        "06-24",
        "Feestdag van de geboorte van de Voorloper.",
        "Johannes de Doper, de Voorloper van Christus, wordt gevierd op zijn geboortefeest in de vaste jaarcyclus.",
    ),
    (
        "petrus-en-paulus",
        "H.H. Apostelen Petrus en Paulus",
        "06-29",
        "Feestdag van de eerste apostelen Petrus en Paulus.",
        "De kerk eert Petrus en Paulus als zuilen van de apostolische verkondiging.",
    ),
    (
        "transfiguratie",
        "Transfiguratie (op de berg Thabor)",
        "08-06",
        "Christus toont Zijn goddelijke heerlijkheid aan Petrus, Jakobus en Johannes.",
        "Op de berg Thabor wordt de heerlijkheid van Christus geopenbaard; Mozes en Elia verschijnen met Hem.",
    ),
    (
        "ontslapen-moeder-gods",
        "Ontslapen van de Moeder Gods",
        "08-15",
        "Het ontslapen (dood en opname) van de Moeder Gods.",
        "De Kerk viert het einde van het aardse leven van de Moeder Gods en haar overgang tot het eeuwige leven.",
    ),
    (
        "onthoofding-johannes-doper",
        "Onthoofding van Johannes de Doper",
        "08-29",
        "Gedachtenis van de marteldood van de Voorloper.",
        "Johannes wordt onthoofd op bevel van Herodes; de Kerk bewaart deze dag als vastendag in veel tradities.",
    ),
    (
        "begin-kerkelijk-jaar",
        "Begin van het kerkelijk jaar",
        "09-01",
        "Indictie: begin van het kerkelijk jaar.",
        "Op 1 september begint het kerkelijk jaar in de Byzantijnse traditie.",
    ),
    (
        "geboorte-moeder-gods",
        "Geboorte van de Moeder Gods",
        "09-08",
        "Geboortefeest van de Allerheiligste Moeder Gods.",
        "De geboorte van Maria uit Joachim en Anna wordt gevierd als begin van het heilseconomie-verhaal in de jaarcyclus.",
    ),
    (
        "kruisverheffing",
        "Kruisverheffing",
        "09-14",
        "Verheffing van het Heilig Kruis.",
        "Het Kruis van Christus wordt verhoogd en vereerd als teken van overwinning over de dood.",
    ),
    (
        "tempelgang-moeder-gods",
        "Tempelgang van de Moeder Gods",
        "11-21",
        "Maria wordt als kind in de tempel gebracht.",
        "De traditie viert dat Maria als kind aan God wordt toegewijd in de tempel te Jeruzalem.",
    ),
    (
        "kerst",
        "Kerstfeest (Geboorte van Christus)",
        "12-25",
        "Geboorte van onze Heer Jezus Christus.",
        "Christus wordt geboren in Bethlehem. Op de oude (Juliaanse) kalender valt de burgerlijke viering thans op 7 januari Gregoriaans.",
    ),
]

for eid, naam, mmdd, samenvatting, verhaal in feesten:
    text = f"""id: {eid}
soort: feest
status: curated
cyclus: jaar
lage_landen: false
namen:
  primair: "{naam}"
datum:
  waarde: "{mmdd}"
  stijl: juliaans
samenvatting: |
  {samenvatting}
verhaal: |
  {verhaal}
referenties:
  - bron_id: orthodoxwiki-pascha-note
    geraadpleegd: "2026-08-15"
  - bron_id: oca-calendar
    geraadpleegd: "2026-08-15"
"""
    (root / f"{eid}.yaml").write_text(text, encoding="utf-8", newline="\n")

print(f"wrote {len(feesten)} feesten")
