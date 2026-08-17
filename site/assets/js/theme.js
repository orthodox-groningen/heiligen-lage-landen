(function () {
  const STORAGE_KEY = "site-theme";

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    document.querySelectorAll("[data-theme-set]").forEach((btn) => {
      btn.setAttribute(
        "aria-pressed",
        btn.dataset.themeSet === theme ? "true" : "false",
      );
    });
  }

  function init() {
    let theme = "dark";
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored === "light" || stored === "dark") {
        theme = stored;
      }
    } catch (_) {
      /* localStorage unavailable */
    }
    applyTheme(theme);

    document.querySelectorAll("[data-theme-set]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const next = btn.dataset.themeSet;
        applyTheme(next);
        try {
          localStorage.setItem(STORAGE_KEY, next);
        } catch (_) {
          /* localStorage unavailable */
        }
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
