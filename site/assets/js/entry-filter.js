(function () {
  const input = document.getElementById("heiligen-zoek");
  const list = document.querySelector("[data-heiligen-lijst]");
  if (!input || !list) return;

  const items = Array.from(list.querySelectorAll("li[data-zoek]"));
  const empty = document.getElementById("heiligen-zoek-leeg");

  function apply() {
    const q = input.value.trim().toLocaleLowerCase("nl");
    let shown = 0;
    const visiblePlaatsen = new Set();
    items.forEach((li) => {
      const hay = (li.getAttribute("data-zoek") || "").toLocaleLowerCase("nl");
      const match = !q || hay.includes(q);
      li.hidden = !match;
      if (match) {
        shown += 1;
        (li.getAttribute("data-plaatsen") || "")
          .split(/\s+/)
          .filter(Boolean)
          .forEach((id) => visiblePlaatsen.add(id));
      }
    });
    if (empty) empty.hidden = shown > 0;
    document.dispatchEvent(
      new CustomEvent("heiligen-filter", {
        detail: { query: q, plaatsIds: Array.from(visiblePlaatsen) },
      })
    );
  }

  const params = new URLSearchParams(window.location.search);
  const plaats = (params.get("plaats") || "").trim();
  if (plaats && !input.value) input.value = plaats;

  input.addEventListener("input", apply);
  apply();
})();
