(() => {
  const STORAGE_KEY = "kalender-stijl";
  const YEAR_KEY = "kalender-jaar";
  const OFFSET_DAYS = 13;
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

  function label(mmdd) {
    const [m, d] = mmdd.split("-").map(Number);
    return `${d} ${MONTHS[m]}`;
  }

  async function applyStyle(style) {
    const url = new URL(window.location.href);
    url.searchParams.set("stijl", style);
    window.history.replaceState({}, "", url);
    setStyle(style);
    await refresh();
  }

  function updateHeading(style) {
    const heading = document.getElementById("today-heading");
    if (!heading) return;
    const today = todayMmdd(style);
    let inner =
      `<span class="today-title-hint" data-open-nieuw-oud tabindex="0">` +
      `Vandaag: ${label(today)}`;
    if (style === "juliaans") {
      inner +=
        ` <span class="today-civil-hint">Wereldlijk: ${label(civilTodayMmdd())}</span>`;
    }
    inner += `</span>`;
    heading.innerHTML = inner;
    wireNieuwOudTriggers(heading);
  }

  function updateNote(style) {
    const cardNote = document.getElementById("today-note");
    if (!cardNote) return;
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
        `<p>Deze datum is volgens de <strong>oude / Juliaanse</strong> kalender` +
        `(in de wereld is het vandaag ${label(civilTodayMmdd())}).</p>` +
        `<div class="style-toggle popover-style" role="group" aria-label="Kalender voor vandaag">` +
        `<button type="button" data-style="gregoriaans" class="style-btn" aria-pressed="false">Nieuw</button>` +
        `<button type="button" data-style="juliaans" class="style-btn" aria-pressed="true">Oud</button>` +
        `</div>`;
    } else {
      if (title) title.textContent = "Nieuwe kalender (Gregoriaans)";
      body.innerHTML =
        `<p>Deze datum is volgens de <strong>nieuwe / Gregoriaanse</strong> (wereldlijke) kalender.` +
        `(volgens de oude kalender is het vandaag ${label(civilTodayMmdd())}).</p>` +
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

  function todayMmdd(style) {
    const civil = new Date();
    if (style === "juliaans") return mmddFromDate(addDays(civil, -OFFSET_DAYS));
    return mmddFromDate(civil);
  }

  function civilTodayMmdd() {
    return mmddFromDate(new Date());
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
    const today = todayMmdd(style);
    const matched = entries.filter((e) => e && e.feestdatum === today);
    if (!matched.length) {
      cardEntries.innerHTML =
        "<p>Geen feest of heilige uit deze collectie op deze kalenderdatum.</p>";
      return;
    }
    cardEntries.innerHTML =
      "<ul>" +
      matched
        .map((e) => {
          const kind = e.soort === "feest" ? "Feest" : "Heilige";
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
    if (hasV && !hasF && !hasH) return "day-vasten";
    if (hasF && hasH) return "day-beide";
    if (hasF) return "day-feest";
    if (hasH) return "day-heilige";
    if (hasV) return "day-vasten";
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
      if (!e || !e.feestdatum) continue;
      if (!byDay.has(e.feestdatum)) byDay.set(e.feestdatum, new Set());
      byDay.get(e.feestdatum).add(e.soort);
    }

    const today = todayMmdd(style);
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
          viewYear === new Date().getFullYear() && mmdd === today;
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

  function checkedShows(name) {
    return Array.from(
      document.querySelectorAll(`input[name="${name}"]:checked`)
    ).map((el) => el.value);
  }

  function filterEntries(entries, shows) {
    return entries.filter((e) => shows.includes(e.soort));
  }

  function renderOverzicht(entries) {
    const list = document.getElementById("overzicht-list");
    const hint = document.getElementById("overzicht-hint");
    const letterNav = document.getElementById("letter-nav");
    const monthNav = document.getElementById("month-nav");
    if (!list) return;

    const shows = checkedShows("show");
    const filtered = filterEntries(entries, shows);

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
      monthNav.innerHTML = MONTHS.slice(1)
        .map((name, i) => {
          const mm = String(i + 1).padStart(2, "0");
          const count = filtered.filter((e) => e.feestdatum.startsWith(mm + "-")).length;
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
    if (browseMode === "letter") {
      subset = filtered.filter((e) => firstLetter(e.naam) === activeLetter);
      if (hint) {
        hint.textContent = `Letter ${activeLetter}: ${subset.length} item(s).`;
      }
      subset.sort((a, b) => a.naam.localeCompare(b.naam, "nl"));
    } else {
      subset = filtered.filter((e) => e.feestdatum.startsWith(activeMonth + "-"));
      if (hint) {
        hint.textContent = `${MONTHS[parseInt(activeMonth, 10)]}: ${subset.length} item(s).`;
      }
      subset.sort((a, b) => a.feestdatum.localeCompare(b.feestdatum) || a.naam.localeCompare(b.naam, "nl"));
    }

    list.innerHTML = subset
      .map((e) => {
        const kind = e.soort === "feest" ? "Feest" : "Heilige";
        return `<li><a href="${assetUrl(e.url.replace(/^\//, ""))}">${e.naam}</a> <span class="meta">${label(e.feestdatum)} · ${kind}</span></li>`;
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
    renderOverzicht(entries);
  }

  /* ---- Agenda ICS ---- */
  function icsFilename() {
    const shows = checkedShows("ics-show");
    const stijl =
      (document.querySelector('input[name="ics-stijl"]:checked') || {}).value ||
      "nieuw";
    let key = "alles";
    if (shows.includes("heilige") && !shows.includes("feest")) key = "heiligen";
    else if (shows.includes("feest") && !shows.includes("heilige")) key = "feesten";
    else if (!shows.length) key = null;
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
        link.textContent = "Kies minstens heiligen of feesten";
      }
    }
    if (hint) {
      const stijl =
        (document.querySelector('input[name="ics-stijl"]:checked') || {}).value ||
        "nieuw";
      hint.innerHTML =
        stijl === "oud"
          ? `Oude kalender: afspraken op burgerlijke vierdatum (+13). Titel bevat de Juliaanse feestdatum. <button type="button" class="text-link" data-open-nieuw-oud>Uitleg</button>`
          : `Nieuwe kalender: afspraken op de feestdatum zelf. <button type="button" class="text-link" data-open-nieuw-oud>Uitleg</button>`;
      wireNieuwOudTriggers(hint);
    }
    if (all) {
      const files = [
        "alles-nieuw",
        "alles-oud",
        "heiligen-nieuw",
        "heiligen-oud",
        "feesten-nieuw",
        "feesten-oud",
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
