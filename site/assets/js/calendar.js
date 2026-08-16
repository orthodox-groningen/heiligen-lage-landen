(() => {
  const STORAGE_KEY = "kalender-stijl";
  const YEAR_KEY = "kalender-jaar";
  const MONTHS = [
    "",
    "januari",
    "februari",
    "maart",
    "april",
    "mei",
    "juni",
    "juli",
    "augustus",
    "september",
    "oktober",
    "november",
    "december",
  ];
  const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

  function siteBase() {
    const fromBody = document.body && document.body.getAttribute("data-base");
    if (fromBody) {
      return fromBody.endsWith("/") ? fromBody : fromBody + "/";
    }
    const path = window.location.pathname;
    if (path.endsWith("/")) return window.location.origin + path;
    const slash = path.lastIndexOf("/");
    return window.location.origin + path.slice(0, slash + 1);
  }

  function assetUrl(rel) {
    return new URL(rel.replace(/^\//, ""), siteBase()).href;
  }

  /** Stabiele URL naar een uitleg-onderwerp: site/content/uitleg/<id>.md */
  function achtergrondUrl(id) {
    return assetUrl(`uitleg/${id}/`);
  }

  function achtergrondLink(id, text, className) {
    const cls = className || "text-link";
    return (
      `<a class="${cls}" href="${achtergrondUrl(id)}" data-achtergrond="${id}">` +
      `${text}</a>`
    );
  }

  function getStyle() {
    const params = new URLSearchParams(window.location.search);
    const fromQuery = params.get("stijl");
    if (fromQuery === "juliaans" || fromQuery === "gregoriaans") {
      try {
        localStorage.setItem(STORAGE_KEY, fromQuery);
      } catch (_) {}
      return fromQuery;
    }
    try {
      return localStorage.getItem(STORAGE_KEY) || "gregoriaans";
    } catch (_) {
      return "gregoriaans";
    }
  }

  function setStyle(style) {
    try {
      localStorage.setItem(STORAGE_KEY, style);
    } catch (_) {}
    document.querySelectorAll(".style-btn[data-style]").forEach((btn) => {
      btn.setAttribute("aria-pressed", btn.dataset.style === style ? "true" : "false");
    });
  }

  function julianGregorianOffsetDays(year) {
    return Math.floor(year / 100) - Math.floor(year / 400) - 2;
  }

  function mmddFromDate(d) {
    return (
      String(d.getMonth() + 1).padStart(2, "0") +
      "-" +
      String(d.getDate()).padStart(2, "0")
    );
  }

  function addDays(d, n) {
    const x = new Date(d.getFullYear(), d.getMonth(), d.getDate());
    x.setDate(x.getDate() + n);
    return x;
  }

  function todayMmdd(style) {
    const civil = new Date();
    if (style === "juliaans") {
      return mmddFromDate(
        addDays(civil, -julianGregorianOffsetDays(civil.getFullYear()))
      );
    }
    return mmddFromDate(civil);
  }

  function civilTodayMmdd() {
    return mmddFromDate(new Date());
  }

  function mmddInRange(mmdd, van, tot) {
    if (!van || !tot) return false;
    if (van <= tot) return van <= mmdd && mmdd <= tot;
    return mmdd >= van || mmdd <= tot;
  }

  function isoWeekdayFromMmdd(mmdd, year) {
    const [m, d] = mmdd.split("-").map(Number);
    const js = new Date(year, m - 1, d).getDay();
    return js === 0 ? 7 : js;
  }

  function civilMmddForView(mmdd, style, year) {
    if (style !== "juliaans") return mmdd;
    return shiftMmdd(mmdd, julianGregorianOffsetDays(year));
  }

  function entryMmddOnYear(entry, year, style) {
    if (!entry) return null;
    if (entry.cyclus === "paascyclus" && entry.occurrences) {
      const map =
        style === "juliaans"
          ? entry.occurrences_juliaans || {}
          : entry.occurrences || {};
      return map[String(year)] || null;
    }
    return entry.feestdatum || null;
  }

  function entryMatchesMmdd(entry, mmdd, year, style, allEntries) {
    if (!entry || !mmdd) return false;
    if (entry.vorm === "weekdagen") {
      if (isWeeklyFastSuppressed(allEntries || [], mmdd, year, style)) {
        return false;
      }
      const civil = civilMmddForView(mmdd, style, year);
      return (entry.weekdagen || []).includes(isoWeekdayFromMmdd(civil, year));
    }
    if (entry.van && entry.tot && entry.vorm === "periode") {
      return mmddInRange(mmdd, entry.van, entry.tot);
    }
    if (entry.period_occurrences) {
      const p = entry.period_occurrences[String(year)];
      if (!p) return false;
      const civil = civilMmddForView(mmdd, style, year);
      return mmddInRange(civil, p.van, p.tot);
    }
    return entryMmddOnYear(entry, year, style) === mmdd;
  }

  function isWeeklyFastSuppressed(entries, mmdd, year, style) {
    return (entries || []).some((e) => {
      if (!e || !e.onderdrukt_wekelijks_vasten) return false;
      if (e.vorm === "weekdagen") return false;
      if (e.van && e.tot && e.vorm === "periode") {
        return mmddInRange(mmdd, e.van, e.tot);
      }
      if (e.period_occurrences) {
        const p = e.period_occurrences[String(year)];
        if (!p) return false;
        const civil = civilMmddForView(mmdd, style, year);
        return mmddInRange(civil, p.van, p.tot);
      }
      return entryMmddOnYear(e, year, style) === mmdd;
    });
  }

  function entriesOnMmdd(entries, mmdd, style, year) {
    return (entries || []).filter((e) =>
      entryMatchesMmdd(e, mmdd, year, style, entries)
    );
  }

  function kindLabel(entry) {
    if (entry.soort === "vasten") {
      if (entry.vorm === "weekdagen") return "Vasten (wekelijks)";
      if (entry.vorm === "periode" || entry.vorm === "periode_hybride") {
        return "Vastenperiode";
      }
      return "Vasten";
    }
    if (entry.cyclus === "paascyclus") return "Paascyclus";
    if (entry.soort === "feest") return "Feest";
    return "Heilige";
  }

  function addObservances(set, entry) {
    const obs =
      entry.observances && entry.observances.length
        ? entry.observances
        : [
            entry.soort === "heilige"
              ? "heilige"
              : entry.soort === "vasten"
                ? "vasten"
                : "feest",
          ];
    for (const o of obs) set.add(o);
  }

  function label(mmdd) {
    const [m, d] = mmdd.split("-").map(Number);
    return `${d} ${MONTHS[m]}`;
  }

  function shiftMmdd(mmdd, deltaDays) {
    const [m, d] = mmdd.split("-").map(Number);
    // Schrikkeljaar: 29 februari blijft bereikbaar in de jaarcyclus.
    return mmddFromDate(addDays(new Date(2024, m - 1, d), deltaDays));
  }

  function getViewMmdd(style) {
    const dag = new URLSearchParams(window.location.search).get("dag");
    if (dag && /^\d{2}-\d{2}$/.test(dag)) return dag;
    return todayMmdd(style);
  }

  function setViewMmdd(mmdd) {
    const url = new URL(window.location.href);
    const style = getStyle();
    if (mmdd === todayMmdd(style)) url.searchParams.delete("dag");
    else url.searchParams.set("dag", mmdd);
    window.history.pushState({}, "", url);
    refresh();
  }

  async function applyStyle(style) {
    const url = new URL(window.location.href);
    url.searchParams.set("stijl", style);
    // Feestdatum in de URL blijft; “vandaag” hangt van de stijl af.
    window.history.replaceState({}, "", url);
    setStyle(style);
    await refresh();
  }

  function updateHeading(style) {
    const heading = document.getElementById("today-heading");
    if (!heading) return;
    const view = getViewMmdd(style);
    const isToday = view === todayMmdd(style);
    const titleText = isToday ? `Vandaag: ${label(view)}` : label(view);
    let titleInner = titleText;
    if (style === "juliaans" && isToday) {
      titleInner +=
        ` <span class="today-civil-hint">Wereldlijk: ${label(civilTodayMmdd())}</span>`;
    } else if (style === "juliaans" && !isToday) {
      const off = julianGregorianOffsetDays(new Date().getFullYear());
      titleInner +=
        ` <span class="today-civil-hint">Wereldlijk: ${label(shiftMmdd(view, off))}</span>`;
    }
    heading.innerHTML =
      `<button type="button" class="day-step" data-day-delta="-1" aria-label="Vorige dag">&lt;</button>` +
      `<span class="day-step-gap" aria-hidden="true"></span>` +
      `<span class="today-title-hint" data-open-nieuw-oud tabindex="0">${titleInner}</span>` +
      `<span class="day-step-gap" aria-hidden="true"></span>` +
      `<button type="button" class="day-step" data-day-delta="1" aria-label="Volgende dag">&gt;</button>`;
    wireNieuwOudTriggers(heading);
    wireDaySteps(heading);
  }

  function wireDaySteps(root) {
    (root || document).querySelectorAll("[data-day-delta]").forEach((btn) => {
      if (btn.dataset.boundDay === "1") return;
      btn.dataset.boundDay = "1";
      btn.addEventListener("click", (ev) => {
        ev.preventDefault();
        ev.stopPropagation();
        const delta = Number(btn.dataset.dayDelta);
        if (!delta) return;
        const style = getStyle();
        setViewMmdd(shiftMmdd(getViewMmdd(style), delta));
      });
    });
  }

  function updateNote(style) {
    const cardNote = document.getElementById("today-note");
    if (!cardNote) return;
    const view = getViewMmdd(style);
    if (view !== todayMmdd(style)) {
      cardNote.textContent = "";
      cardNote.hidden = true;
      return;
    }
    if (style === "juliaans") {
      cardNote.textContent = "";
      cardNote.hidden = true;
      return;
    }
    cardNote.textContent = `Oud/Juliaans vandaag: ${label(todayMmdd("juliaans"))}.`;
    cardNote.hidden = false;
  }

  let nieuwOudCloseTimer = null;
  let nieuwOudAnchor = null;

  function fillNieuwOudDialog(style) {
    const body = document.getElementById("nieuw-oud-body");
    const title = document.getElementById("nieuw-oud-title");
    if (!body) return;
    const today = todayMmdd(style);
    if (style === "juliaans") {
      if (title) title.textContent = "Oude kalender (Juliaans)";
      body.innerHTML =
        `<p>Dat is ${label(civilTodayMmdd())} (nieuw/Gregoriaans)..` +
        `De Gregoriaanse kalender is de wereldlijke kalender.</p>` +
        `<div class="style-toggle popover-style" role="group" aria-label="Kalender voor vandaag">` +
        `<button type="button" data-style="gregoriaans" class="style-btn" aria-pressed="false">Nieuw</button>` +
        `<button type="button" data-style="juliaans" class="style-btn" aria-pressed="true">Oud</button>` +
        `</div>`;
    } else {
      if (title) title.textContent = "Nieuwe/Gregoriaanse kalender";
      body.innerHTML =
        `<p>Dat is ${label(todayMmdd("juliaans"))} (oud/Juliaans).` +
        `De Gregoriaanse kalender is de wereldlijke kalender.</p>` +
        `<div class="style-toggle popover-style" role="group" aria-label="Kalender voor vandaag">` +
        `<button type="button" data-style="gregoriaans" class="style-btn" aria-pressed="true">Nieuw</button>` +
        `<button type="button" data-style="juliaans" class="style-btn" aria-pressed="false">Oud</button>` +
        `</div>`;
    }
    body.querySelectorAll(".style-btn[data-style]").forEach((btn) => {
      btn.addEventListener("click", async (ev) => {
        ev.preventDefault();
        ev.stopPropagation();
        cancelNieuwOudClose();
        await applyStyle(btn.dataset.style);
        nieuwOudAnchor =
          document.querySelector("#today-heading [data-open-nieuw-oud]") ||
          nieuwOudAnchor;
        fillNieuwOudDialog(btn.dataset.style);
        if (nieuwOudAnchor) positionNieuwOudPopover(nieuwOudAnchor);
        const dlg = document.getElementById("nieuw-oud-dialog");
        if (dlg) dlg.hidden = false;
      });
    });
  }

  function positionNieuwOudPopover(trigger) {
    const dlg = document.getElementById("nieuw-oud-dialog");
    if (!dlg || !trigger) return;
    dlg.style.left = "0px";
    dlg.style.top = "0px";
    const gap = 8;
    const rect = trigger.getBoundingClientRect();
    const pop = dlg.getBoundingClientRect();
    let left = rect.left;
    let top = rect.bottom + gap;
    if (left + pop.width > window.innerWidth - 8) {
      left = Math.max(8, window.innerWidth - pop.width - 8);
    }
    if (top + pop.height > window.innerHeight - 8) {
      top = Math.max(8, rect.top - pop.height - gap);
    }
    dlg.style.left = `${Math.max(8, left)}px`;
    dlg.style.top = `${top}px`;
  }

  function closeNieuwOudDialog() {
    const dlg = document.getElementById("nieuw-oud-dialog");
    if (!dlg) return;
    dlg.hidden = true;
    nieuwOudAnchor = null;
  }

  function cancelNieuwOudClose() {
    if (nieuwOudCloseTimer) {
      clearTimeout(nieuwOudCloseTimer);
      nieuwOudCloseTimer = null;
    }
  }

  function scheduleNieuwOudClose() {
    cancelNieuwOudClose();
    nieuwOudCloseTimer = setTimeout(closeNieuwOudDialog, 180);
  }

  function openNieuwOudDialog(trigger) {
    const dlg = document.getElementById("nieuw-oud-dialog");
    if (!dlg) return;
    cancelNieuwOudClose();
    nieuwOudAnchor = trigger || document.querySelector("[data-open-nieuw-oud]");
    fillNieuwOudDialog(getStyle());
    dlg.hidden = false;
    positionNieuwOudPopover(nieuwOudAnchor);
  }

  function wireNieuwOudTriggers(root) {
    (root || document).querySelectorAll("[data-open-nieuw-oud]").forEach((el) => {
      if (el.dataset.bound === "1") return;
      el.dataset.bound = "1";
      el.addEventListener("mouseenter", () => openNieuwOudDialog(el));
      el.addEventListener("mouseleave", scheduleNieuwOudClose);
      el.addEventListener("focus", () => openNieuwOudDialog(el));
      el.addEventListener("blur", scheduleNieuwOudClose);
      el.addEventListener("click", (ev) => {
        ev.preventDefault();
        ev.stopPropagation();
        const dlg = document.getElementById("nieuw-oud-dialog");
        if (dlg && !dlg.hidden) {
          closeNieuwOudDialog();
        } else {
          openNieuwOudDialog(el);
        }
      });
    });
    const dlg = document.getElementById("nieuw-oud-dialog");
    if (dlg && dlg.dataset.boundHover !== "1") {
      dlg.dataset.boundHover = "1";
      dlg.addEventListener("mouseenter", cancelNieuwOudClose);
      dlg.addEventListener("mouseleave", scheduleNieuwOudClose);
    }
  }

  function firstLetter(name) {
    const ch = (name || "").trim().charAt(0).toUpperCase();
    return LETTERS.includes(ch) ? ch : "#";
  }

  async function loadEntries() {
    const url = assetUrl("data/entries.json");
    const res = await fetch(url);
    if (!res.ok) throw new Error(`entries.json (${res.status}) ${url}`);
    return res.json();
  }

  function renderToday(entries, style) {
    const cardEntries = document.getElementById("today-entries");
    if (!cardEntries) return;
    updateHeading(style);
    updateNote(style);
    const view = getViewMmdd(style);
    const year = new Date().getFullYear();
    const matched = entriesOnMmdd(entries, view, style, year);
    if (!matched.length) {
      cardEntries.innerHTML =
        "<p>Geen feest, heilige of vasten uit deze collectie op deze kalenderdatum.</p>";
      return;
    }
    cardEntries.innerHTML =
      "<ul>" +
      matched
        .map((e) => {
          const kind = kindLabel(e);
          const summary = e.samenvatting
            ? `<div class="muted">${e.samenvatting}</div>`
            : "";
          return `<li><a href="${assetUrl(e.url.replace(/^\//, ""))}">${e.naam}</a> <span class="meta">(${kind})</span>${summary}</li>`;
        })
        .join("") +
      "</ul>";
  }

  function dayClass(kinds) {
    const hasF = kinds.has("feest");
    const hasH = kinds.has("heilige");
    const hasV = kinds.has("vasten");
    if (hasF && hasH && hasV) return "day-feest-heilige-vasten";
    if (hasF && hasV) return "day-feest-vasten";
    if (hasH && hasV) return "day-heilige-vasten";
    if (hasF && hasH) return "day-beide";
    if (hasV) return "day-vasten";
    if (hasF) return "day-feest";
    if (hasH) return "day-heilige";
    return "";
  }

  let viewYear = new Date().getFullYear();
  try {
    const stored = localStorage.getItem(YEAR_KEY);
    if (stored) viewYear = parseInt(stored, 10) || viewYear;
  } catch (_) {}

  function renderYearGrid(entries, style) {
    const root = document.getElementById("year-grid");
    if (!root) return;
    const yearEl = document.getElementById("kalender-jaar");
    if (yearEl) yearEl.textContent = String(viewYear);

    const byDay = new Map();
    for (const e of entries) {
      if (!e) continue;
      if (e.vorm === "weekdagen") {
        const daysInYear =
          (viewYear % 4 === 0 && viewYear % 100 !== 0) || viewYear % 400 === 0
            ? 366
            : 365;
        for (let i = 0; i < daysInYear; i++) {
          const d = new Date(viewYear, 0, 1 + i);
          const iso = d.getDay() === 0 ? 7 : d.getDay();
          if (!(e.weekdagen || []).includes(iso)) continue;
          const mmdd = mmddFromDate(d);
          if (isWeeklyFastSuppressed(entries, mmdd, viewYear, "gregoriaans")) {
            continue;
          }
          if (!byDay.has(mmdd)) byDay.set(mmdd, new Set());
          addObservances(byDay.get(mmdd), e);
        }
        continue;
      }
      if (e.period_occurrences) {
        const p = e.period_occurrences[String(viewYear)];
        if (!p) continue;
        const start = new Date(
          viewYear,
          Number(p.van.slice(0, 2)) - 1,
          Number(p.van.slice(3, 5))
        );
        const end = new Date(
          viewYear,
          Number(p.tot.slice(0, 2)) - 1,
          Number(p.tot.slice(3, 5))
        );
        for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
          const mmdd = mmddFromDate(d);
          if (!byDay.has(mmdd)) byDay.set(mmdd, new Set());
          addObservances(byDay.get(mmdd), e);
        }
        continue;
      }
      if (e.vorm === "periode" && e.van && e.tot) {
        const leap = 2024;
        const start = new Date(
          leap,
          Number(e.van.slice(0, 2)) - 1,
          Number(e.van.slice(3, 5))
        );
        let end = new Date(
          leap,
          Number(e.tot.slice(0, 2)) - 1,
          Number(e.tot.slice(3, 5))
        );
        const wrap = start > end;
        if (wrap) end = new Date(leap, 11, 31);
        for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
          const mmdd = mmddFromDate(d);
          if (!byDay.has(mmdd)) byDay.set(mmdd, new Set());
          addObservances(byDay.get(mmdd), e);
        }
        if (wrap) {
          const end2 = new Date(
            leap,
            Number(e.tot.slice(0, 2)) - 1,
            Number(e.tot.slice(3, 5))
          );
          for (
            let d = new Date(leap, 0, 1);
            d <= end2;
            d.setDate(d.getDate() + 1)
          ) {
            const mmdd = mmddFromDate(d);
            if (!byDay.has(mmdd)) byDay.set(mmdd, new Set());
            addObservances(byDay.get(mmdd), e);
          }
        }
        continue;
      }
      let mmdd = null;
      if (e.cyclus === "paascyclus") {
        mmdd = (e.occurrences || {})[String(viewYear)] || null;
      } else {
        mmdd = e.feestdatum || null;
      }
      if (!mmdd) continue;
      if (!byDay.has(mmdd)) byDay.set(mmdd, new Set());
      addObservances(byDay.get(mmdd), e);
    }

    const civilToday = civilTodayMmdd();
    const dow = ["ma", "di", "wo", "do", "vr", "za", "zo"];
    let html = "";
    for (let month = 1; month <= 12; month++) {
      html += `<section class="month-card"><h2>${MONTHS[month]} ${viewYear}</h2><div class="month-days">`;
      for (const d of dow) html += `<div class="dow">${d}</div>`;
      const first = new Date(viewYear, month - 1, 1);
      let start = (first.getDay() + 6) % 7;
      for (let i = 0; i < start; i++) html += `<div></div>`;
      const daysInMonth = new Date(viewYear, month, 0).getDate();
      for (let day = 1; day <= daysInMonth; day++) {
        const mmdd =
          String(month).padStart(2, "0") + "-" + String(day).padStart(2, "0");
        const kinds = byDay.get(mmdd) || new Set();
        const color = dayClass(kinds);
        const has = kinds.size > 0;
        const isToday =
          viewYear === new Date().getFullYear() && mmdd === civilToday;
        const cls = ["day", has ? "has-entry" : "", color, isToday ? "is-today" : ""]
          .filter(Boolean)
          .join(" ");
        html += `<a class="${cls}" href="${assetUrl("datum/" + mmdd + "/")}" title="${label(mmdd)}">${day}</a>`;
      }
      html += `</div></section>`;
    }
    root.innerHTML = html;
  }

  function initYearControls(entries, style) {
    const prev = document.getElementById("year-prev");
    const next = document.getElementById("year-next");
    if (!prev || !next) return;
    prev.onclick = () => {
      viewYear -= 1;
      try {
        localStorage.setItem(YEAR_KEY, String(viewYear));
      } catch (_) {}
      renderYearGrid(entries, style);
    };
    next.onclick = () => {
      viewYear += 1;
      try {
        localStorage.setItem(YEAR_KEY, String(viewYear));
      } catch (_) {}
      renderYearGrid(entries, style);
    };
  }

  /* ---- Overzicht ---- */
  let browseMode = "letter";
  let activeLetter = "A";
  let activeMonth = "01";
  let searchQuery = "";

  function matchesSearch(entry, q) {
    if (!q) return true;
    const hay = [entry.naam, ...(entry.alternatief || [])]
      .join(" ")
      .toLocaleLowerCase("nl");
    return hay.includes(q);
  }

  function checkedShows(name) {
    return Array.from(
      document.querySelectorAll(`input[name="${name}"]:checked`)
    ).map((el) => el.value);
  }

  function filterEntries(entries, shows) {
    return entries.filter((e) => shows.includes(e.soort));
  }

  function entrySortMmdd(entry, year) {
    if (entry.vorm === "weekdagen") return "99-99";
    if (entry.period_occurrences) {
      const p = entry.period_occurrences[String(year)];
      return (p && p.van) || "99-99";
    }
    if (entry.van) return entry.van;
    return entryMmddOnYear(entry, year, "gregoriaans") || "99-99";
  }

  function entryTouchesMonth(entry, year, mm) {
    if (entry.vorm === "weekdagen") return false;
    if (entry.period_occurrences) {
      const p = entry.period_occurrences[String(year)];
      if (!p) return false;
      return p.van.startsWith(mm + "-") || p.tot.startsWith(mm + "-") ||
        (p.van < mm + "-01" && p.tot > mm + "-31");
    }
    if (entry.van && entry.tot) {
      for (const part of [entry.van, entry.tot]) {
        if (part.startsWith(mm + "-")) return true;
      }
      if (entry.van <= entry.tot) {
        return entry.van.slice(0, 2) <= mm && entry.tot.slice(0, 2) >= mm;
      }
      return entry.van.slice(0, 2) <= mm || entry.tot.slice(0, 2) >= mm;
    }
    const fd = entryMmddOnYear(entry, year, "gregoriaans");
    return Boolean(fd && fd.startsWith(mm + "-"));
  }

  function renderOverzicht(entries) {
    const list = document.getElementById("overzicht-list");
    const hint = document.getElementById("overzicht-hint");
    const letterNav = document.getElementById("letter-nav");
    const monthNav = document.getElementById("month-nav");
    if (!list) return;

    const shows = checkedShows("show");
    const filtered = filterEntries(entries, shows).filter((e) =>
      matchesSearch(e, searchQuery)
    );

    if (letterNav) {
      letterNav.hidden = browseMode !== "letter";
      letterNav.innerHTML = LETTERS.map((L) => {
        const count = filtered.filter((e) => firstLetter(e.naam) === L).length;
        const pressed = L === activeLetter ? "true" : "false";
        return `<button type="button" class="letter-btn" data-letter="${L}" aria-pressed="${pressed}" ${count ? "" : "disabled"}>${L}</button>`;
      }).join("");
      letterNav.querySelectorAll(".letter-btn").forEach((btn) => {
        btn.onclick = () => {
          activeLetter = btn.dataset.letter;
          renderOverzicht(entries);
        };
      });
    }

    if (monthNav) {
      monthNav.hidden = browseMode !== "maand";
      const year = new Date().getFullYear();
      monthNav.innerHTML = MONTHS.slice(1)
        .map((name, i) => {
          const mm = String(i + 1).padStart(2, "0");
          const count = filtered.filter((e) => entryTouchesMonth(e, year, mm))
            .length;
          const pressed = mm === activeMonth ? "true" : "false";
          return `<button type="button" class="letter-btn" data-month="${mm}" aria-pressed="${pressed}" ${count ? "" : "disabled"}>${name.slice(0, 3)}</button>`;
        })
        .join("");
      monthNav.querySelectorAll(".letter-btn").forEach((btn) => {
        btn.onclick = () => {
          activeMonth = btn.dataset.month;
          renderOverzicht(entries);
        };
      });
    }

    let subset;
    const year = new Date().getFullYear();
    if (browseMode === "letter") {
      subset = filtered.filter((e) => firstLetter(e.naam) === activeLetter);
      if (hint) {
        hint.textContent = `Letter ${activeLetter}: ${subset.length} item(s).`;
      }
      subset.sort((a, b) => a.naam.localeCompare(b.naam, "nl"));
    } else {
      subset = filtered.filter((e) => entryTouchesMonth(e, year, activeMonth));
      if (hint) {
        hint.textContent = `${MONTHS[parseInt(activeMonth, 10)]} ${year}: ${subset.length} item(s).`;
      }
      subset.sort((a, b) => {
        const fa = entrySortMmdd(a, year);
        const fb = entrySortMmdd(b, year);
        return fa.localeCompare(fb) || a.naam.localeCompare(b.naam, "nl");
      });
    }

    list.innerHTML = subset
      .map((e) => {
        const kind = kindLabel(e);
        let when = "—";
        if (e.vorm === "weekdagen") when = "wekelijks";
        else if (e.van && e.tot) when = `${label(e.van)} – ${label(e.tot)}`;
        else if (e.period_occurrences) {
          const p = e.period_occurrences[String(year)];
          when = p ? `${label(p.van)} – ${label(p.tot)}` : "paascyclus";
        } else {
          const fd = entryMmddOnYear(e, year, "gregoriaans");
          when = fd ? label(fd) : "paascyclus";
        }
        return `<li><a href="${assetUrl(e.url.replace(/^\//, ""))}">${e.naam}</a> <span class="meta">${when} · ${kind}</span></li>`;
      })
      .join("");
  }

  function initOverzicht(entries) {
    if (!document.querySelector("[data-overzicht]")) return;
    document.querySelectorAll(".browse-mode .style-btn").forEach((btn) => {
      btn.onclick = () => {
        browseMode = btn.dataset.browse;
        document.querySelectorAll(".browse-mode .style-btn").forEach((b) => {
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        renderOverzicht(entries);
      };
    });
    document.querySelectorAll('input[name="show"]').forEach((el) => {
      el.addEventListener("change", () => renderOverzicht(entries));
    });
    const search = document.getElementById("overzicht-search");
    if (search) {
      search.addEventListener("input", () => {
        searchQuery = (search.value || "").trim().toLocaleLowerCase("nl");
        renderOverzicht(entries);
      });
    }
    renderOverzicht(entries);
  }

  /* ---- Agenda ICS ---- */
  function icsFilename() {
    const shows = checkedShows("ics-show");
    const stijl =
      (document.querySelector('input[name="ics-stijl"]:checked') || {}).value ||
      "nieuw";
    if (!shows.length) return null;
    const set = new Set(shows);
    const mapping = [
      [["heilige", "feest", "vasten"], "alles"],
      [["heilige"], "heiligen"],
      [["feest"], "feesten"],
      [["vasten"], "vasten"],
      [["heilige", "feest"], "heiligen-feesten"],
      [["heilige", "vasten"], "heiligen-vasten"],
      [["feest", "vasten"], "feesten-vasten"],
    ];
    let key = null;
    for (const [need, name] of mapping) {
      if (need.length === set.size && need.every((k) => set.has(k))) {
        key = name;
        break;
      }
    }
    return key ? `${key}-${stijl}.ics` : null;
  }

  function updateAgendaUi() {
    if (!document.querySelector("[data-agenda]")) return;
    const file = icsFilename();
    const link = document.getElementById("ics-download");
    const hint = document.getElementById("ics-hint");
    const all = document.getElementById("ics-all-links");
    if (link) {
      if (file) {
        link.href = assetUrl("ics/" + file);
        link.classList.remove("is-disabled");
        link.textContent = "ICS: " + file;
      } else {
        link.removeAttribute("href");
        link.classList.add("is-disabled");
        link.textContent = "Kies minstens één categorie";
      }
    }
    if (hint) {
      const stijl =
        (document.querySelector('input[name="ics-stijl"]:checked') || {}).value ||
        "nieuw";
      hint.innerHTML =
        stijl === "oud"
          ? `Oude kalender: afspraken op burgerlijke vierdatum (+13). Titel bevat de Juliaanse feestdatum. ${achtergrondLink("nieuw-oud", "Meer uitleg")}`
          : `Nieuwe kalender: afspraken op de feestdatum zelf. ${achtergrondLink("nieuw-oud", "Meer uitleg")}`;
    }
    if (all) {
      const files = [
        "alles-nieuw",
        "alles-oud",
        "heiligen-nieuw",
        "heiligen-oud",
        "feesten-nieuw",
        "feesten-oud",
        "vasten-nieuw",
        "vasten-oud",
        "heiligen-feesten-nieuw",
        "heiligen-feesten-oud",
        "heiligen-vasten-nieuw",
        "heiligen-vasten-oud",
        "feesten-vasten-nieuw",
        "feesten-vasten-oud",
      ];
      all.innerHTML = files
        .map((f) => `<li><a href="${assetUrl("ics/" + f + ".ics")}">${f}.ics</a></li>`)
        .join("");
    }
  }

  function initAgenda() {
    if (!document.querySelector("[data-agenda]")) return;
    document
      .querySelectorAll('input[name="ics-show"], input[name="ics-stijl"]')
      .forEach((el) => el.addEventListener("change", updateAgendaUi));
    updateAgendaUi();
  }

  async function refresh() {
    const style = getStyle();
    setStyle(style);
    updateHeading(style);
    updateNote(style);
    try {
      const entries = await loadEntries();
      renderToday(entries, style);
      renderYearGrid(entries, style);
      initYearControls(entries, style);
      initOverzicht(entries);
      initAgenda();
    } catch (err) {
      const cardEntries = document.getElementById("today-entries");
      if (cardEntries) {
        cardEntries.innerHTML =
          "<p>Kon kalenderdata niet laden. Vernieuw de pagina of probeer later opnieuw.</p>";
      }
      console.error(err);
    }
  }

  document.querySelectorAll(".style-btn[data-style]").forEach((btn) => {
    btn.addEventListener("click", () => {
      applyStyle(btn.dataset.style);
    });
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeNieuwOudDialog();
  });

  window.addEventListener("popstate", () => {
    refresh();
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      wireNieuwOudTriggers(document);
      refresh();
    });
  } else {
    wireNieuwOudTriggers(document);
    refresh();
  }
})();
