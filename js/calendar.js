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

  function getBase() {
    const scripts = document.getElementsByTagName("script");
    for (const s of scripts) {
      if (s.src && s.src.includes("/js/calendar.js")) {
        return s.src.replace(/js\/calendar\.js.*$/, "");
      }
    }
    return document.body?.dataset?.baseurl || "/";
  }

  const base = getBase();

  function getStyle() {
    const params = new URLSearchParams(window.location.search);
    const fromQuery = params.get("stijl");
    if (fromQuery === "juliaans" || fromQuery === "gregoriaans") {
      localStorage.setItem(STORAGE_KEY, fromQuery);
      return fromQuery;
    }
    return localStorage.getItem(STORAGE_KEY) || "gregoriaans";
  }

  function setStyle(style) {
    localStorage.setItem(STORAGE_KEY, style);
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
      ? "Juliaans · oude kalender"
      : "Gregoriaans · nieuwe kalender";
  }

  /** Kalenderdatum van "vandaag" in de gekozen tijdrekening. */
  function todayMmdd(style) {
    const civil = new Date();
    if (style === "juliaans") {
      return mmddFromDate(addDays(civil, -OFFSET_DAYS));
    }
    return mmddFromDate(civil);
  }

  /** Burgerlijke (Gregoriaanse) datum van vandaag, ter toelichting. */
  function civilTodayMmdd() {
    return mmddFromDate(new Date());
  }

  async function loadEntries() {
    const res = await fetch(`${base}data/entries.json`);
    if (!res.ok) throw new Error("entries.json niet geladen");
    return res.json();
  }

  function renderToday(entries, style) {
    const heading = document.getElementById("today-heading");
    const cardNote = document.getElementById("today-note");
    const cardEntries = document.getElementById("today-entries");
    if (!cardEntries) return;

    const today = todayMmdd(style);
    const civil = civilTodayMmdd();
    const matched = entries.filter((e) => e.feestdatum === today);

    if (heading) {
      heading.textContent = `Vandaag · ${label(today)} (${stylePhrase(style)})`;
    }

    if (cardNote) {
      if (style === "juliaans") {
        cardNote.textContent =
          `Burgerlijk in Nederland is het ${label(civil)} (Gregoriaans · nieuwe kalender).`;
      } else {
        const julian = todayMmdd("juliaans");
        cardNote.textContent =
          `In de oude/Juliaanse tijdrekening is het vandaag ${label(julian)}.`;
      }
    }

    if (matched.length === 0) {
      cardEntries.innerHTML =
        "<p>Geen feest of heilige uit deze collectie op deze kalenderdatum.</p>";
    } else {
      const items = matched
        .map((e) => {
          const kind = e.soort === "feest" ? "Feest" : "Heilige";
          const summary = e.samenvatting
            ? `<div class="muted">${e.samenvatting}</div>`
            : "";
          return `<li><a href="${base}${e.url.replace(/^\//, "")}">${e.naam}</a> <span class="meta">(${kind})</span>${summary}</li>`;
        })
        .join("");
      cardEntries.innerHTML = `<ul>${items}</ul>`;
    }
  }

  function renderYearGrid(entries, style) {
    const root = document.getElementById("year-grid");
    if (!root) return;
    const byDay = new Map();
    for (const e of entries) {
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
        const href = `${base}datum/${mmdd}/`;
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
    try {
      const entries = await loadEntries();
      renderToday(entries, style);
      renderYearGrid(entries, style);
    } catch (err) {
      const cardEntries = document.getElementById("today-entries");
      if (cardEntries) {
        cardEntries.innerHTML = `<p>Kon kalenderdata niet laden.</p>`;
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

  refresh();
})();
