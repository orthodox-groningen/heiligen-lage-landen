# TODO

Open werk volgens het verbeterplan. Vink af per afgeronde wijziging.

- [x] Beleid en datamodel: selectiecriteria, `betekenis_lage_landen`,
      `selectie`, `id_aliassen`, aangescherpte `curated` voor heiligen.
- [x] Generatie en index: betekenis-sectie, Hugo-aliases, `entries.json`,
      beheer-selectielijst; heiligenindex toont en zoekt alternatieve namen.
- [x] Datahygiëne: merges (Lebuïnus, Alberik), titels Nederlands/correct,
      «Icoon in parochie» uit titels.
- [x] Inventaris: alle heiligen gescored (`selectie` in YAML);
      gatenlijst + Johannes en Sophrony op toevoegen; C-heiligen niet
      automatisch (`docs/inventaris.md`, `/beheer/selectie/`).
- [x] Kerninhoud: ontbrekenden + Johannes van Shanghai + Sophrony + kernset
      met betekenis, verhaal, referenties; `curated` waar de lat gehaald wordt.
- [x] Kalenderranden: voor-/nafeesten van de twaalf, synaxisdagen, Pokrov,
      teruggave Hemelvaart/Pinksteren; zondagen rond Kerst/Theofanie via
      `datum.weekdag_relatief`.
- [ ] Iconen: legale bestanden voor de curated kern (`rechten: ok`).
- [ ] CI en parochie: pytest in `pages.yml`; Den Haag-default documenteren;
      `bronnen.yaml` opschonen.
