(function () {
  const input = document.getElementById("heiligen-zoek");
  const list = document.querySelector("[data-heiligen-lijst]");
  if (!input || !list) return;

  const items = Array.from(list.querySelectorAll("li[data-zoek]"));
  const empty = document.getElementById("heiligen-zoek-leeg");

  function apply() {
    const q = input.value.trim().toLocaleLowerCase("nl");
    let shown = 0;
    items.forEach((li) => {
      const hay = (li.getAttribute("data-zoek") || "").toLocaleLowerCase("nl");
      const match = !q || hay.includes(q);
      li.hidden = !match;
      if (match) shown += 1;
    });
    if (empty) empty.hidden = shown > 0;
  }

  input.addEventListener("input", apply);
})();
