---
title: Kleuren in de jaarkalender (technisch)
description: observances, CSS-klassen en de jaarrooster-kleur in calendar.js
uitleg_stijl: kleuren-technisch
build:
  list: never
  render: always
git_date: 2026-08-17
---

Technische bijlage bij de [uitleg Kleuren]({{% ref "/uitleg/kleuren" %}}).

## observances

Optioneel op een entry:

```yaml
observances: [feest, vasten]
```

Ontbreekt het veld, dan volgt de default uit `soort` (`heilige`, `feest`
of `vasten`). Het jaarrooster kleurt de **combinatie** van categorieën op
die burgerlijke dag (feest én vasten krijgt een eigen klasse, niet alleen
«feest»).

## CSS-klassen

Gedefinieerd in `site/assets/css/site.css`, gezet door
`site/assets/js/calendar.js`:

| Klasse | Betekenis |
| --- | --- |
| `day-feest` | alleen feest |
| `day-heilige` | alleen heilige(n) |
| `day-beide` | feest én heilige |
| `day-vasten` | alleen vasten |
| `day-feest-vasten` | feest én vasten |
| `day-heilige-vasten` | heilige én vasten |

Wekelijks wo/vr-vasten telt mee als vasten, tenzij een periode of
`onderdrukt_wekelijks_vasten` het onderdrukt. Het **niveau** (streng, vis,
…) is een aparte indicatie, geen extra kleur.
