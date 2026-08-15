(() => {
  const STORAGE_KEY = "kalender-stijl";
  const OFFSET_DAYS = 13; // tot 2100
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

  function siteBase() {
    const fromBody = document.body && document.body.getAttribute("data-base");
    if (fromBody) {
      return fromBody.endsWith("/") ? fromBody : fromBody + "/";
    }
    // Fallback: map-URL van de huidige pagina (werkt op / en /preview/).
    const path = window.location.pathname;
    if (path.endsWith("/")) {
      return window.location.origin + path;
    }
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
      } catch (_) {
        /* private mode */
      }
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
    } catch (_) {
      /* private mode */
    }
    document.querySelectorAll(".style-btn").forEach((btn) => {
      btn.setAttribute("aria-pressed", btn.dataset.style === style ? "true" : "false");
    });
  }

  function mmddFromDate(d) {
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${m}-${day}`;
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

  function stylePhrase(style) {
    return style === "juliaans"
      ? "Juliaans, oude kalender"
      : "Gregoriaans, nieuwe kalender";
  }

  function todayMmdd(style) {
    const civil = new Date();
    if (style === "juliaans") {
      return mmddFromDate(addDays(civil, -OFFSET_DAYS));
    }
    return mmddFromDate(civil);
  }

  function civilTodayMmdd() {
    return mmddFromDate(new Date());
  }

  function updateHeading(style) {
    const heading = document.getElementById("today-heading");
    if (!heading) return;
    const today = todayMmdd(style);
    heading.textContent = `Vandaag · ${label(today)} (${stylePhrase(style)})`;
  }

  function updateNote(style) {
    const cardNote = document.getElementById("today-note");
    if (!cardNote) return;
    const civil = civilTodayMmdd();
    if (style === "juliaans") {
      cardNote.textContent =
        `Burgerlijk in Nederland is het ${label(civil)} (Gregoriaans, nieuwe kalender).`;
    } else {
      cardNote.textContent =
        `In de oude/Juliaanse tijdrekening is het vandaag ${label(todayMmdd("juliaans"))}.`;
    }
  }

  async function loadEntries() {
    const url = assetUrl("data/entries.json");
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`entries.json niet geladen (${res.status}) via ${url}`);
    }
    return res.json();
  }

  function renderToday(entries, style) {
    const cardEntries = document.getElementById("today-entries");
    if (!cardEntries) return;

    updateHeading(style);
    updateNote(style);

    const today = todayMmdd(style);
    const matched = entries.filter((e) => e && e.feestdatum === today);

    if (matched.length === 0) {
      cardEntries.innerHTML =
        "<p>Geen feest of heilige uit deze collectie op deze kalenderdatum.</p>";
      return;
    }

    const items = matched
      .map((e) => {
        const kind = e.soort === "feest" ? "Feest" : "Heilige";
        const summary = e.samenvatting
          ? `<div class="muted">${e.samenvatting}</div>`
          : "";
        const href = assetUrl(e.url.replace(/^\//, ""));
        return `<li><a href="${href}">${e.naam}</a> <span class="meta">(${kind})</span>${summary}</li>`;
      })
      .join("");
    cardEntries.innerHTML = `<ul>${items}</ul>`;
  }

  function renderYearGrid(entries, style) {
    const root = document.getElementById("year-grid");
    if (!root) return;
    const byDay = new Map();
    for (const e of entries) {
      if (!e || !e.feestdatum) continue;
      const mmdd = e.feestdatum;
      if (!byDay.has(mmdd)) byDay.set(mmdd, []);
      byDay.get(mmdd).push(e);
    }

    const year = new Date().getFullYear();
    const today = todayMmdd(style);
    const dow = ["ma", "di", "wo", "do", "vr", "za", "zo"];
    let html = "";
    for (let month = 1; month <= 12; month++) {
      html += `<section class="month-card"><h2>${MONTHS[month]}</h2><div class="month-days">`;
      for (const d of dow) html += `<div class="dow">${d}</div>`;
      const first = new Date(year, month - 1, 1);
      let start = (first.getDay() + 6) % 7;
      for (let i = 0; i < start; i++) html += `<div></div>`;
      const daysInMonth = new Date(year, month, 0).getDate();
      for (let day = 1; day <= daysInMonth; day++) {
        const mmdd = `${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
        const has = byDay.has(mmdd);
        const isToday = mmdd === today;
        const href = assetUrl(`datum/${mmdd}/`);
        const cls = ["day", has ? "has-entry" : "", isToday ? "is-today" : ""]
          .filter(Boolean)
          .join(" ");
        html += `<a class="${cls}" href="${href}" title="${label(mmdd)}">${day}</a>`;
      }
      html += `</div></section>`;
    }
    root.innerHTML = html;
  }

  async function refresh() {
    const style = getStyle();
    setStyle(style);
    // Datum in de titel meteen zetten, ook als de data-fetch faalt.
    updateHeading(style);
    updateNote(style);
    try {
      const entries = await loadEntries();
      renderToday(entries, style);
      renderYearGrid(entries, style);
    } catch (err) {
      const cardEntries = document.getElementById("today-entries");
      if (cardEntries) {
        cardEntries.innerHTML =
          "<p>Kon kalenderdata niet laden. Vernieuw de pagina of probeer later opnieuw.</p>";
      }
      console.error(err);
    }
  }

  document.querySelectorAll(".style-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const style = btn.dataset.style;
      const url = new URL(window.location.href);
      url.searchParams.set("stijl", style);
      window.history.replaceState({}, "", url);
      setStyle(style);
      refresh();
    });
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", refresh);
  } else {
    refresh();
  }
})();
