(function () {
  const form = document.getElementById("reactie-form");
  if (!form) return;

  const email = form.dataset.email || "";
  const soortSelect = document.getElementById("reactie-soort");
  const status = document.getElementById("reactie-status");
  const sets = form.querySelectorAll(".reactie-set");

  function showSet() {
    const soort = soortSelect.value;
    sets.forEach(function (set) {
      const on = set.dataset.soort === soort;
      set.hidden = !on;
      set.querySelectorAll("input, textarea, select").forEach(function (el) {
        el.disabled = !on;
      });
    });
  }

  function val(id) {
    const el = document.getElementById(id);
    return el && !el.disabled ? el.value.trim() : "";
  }

  function requireFilled(id, label) {
    if (val(id)) return true;
    if (status) {
      status.hidden = false;
      status.textContent = "Vul «" + label + "» in.";
    }
    const el = document.getElementById(id);
    if (el) el.focus();
    return false;
  }

  function buildMail() {
    const soort = soortSelect.value;
    if (soort === "vraag") {
      if (!requireFilled("reactie-bericht", "Uw vraag of opmerking")) return null;
      return {
        subject: "[vraag] kalender",
        body: "Waarover: " + val("reactie-over") + "\n\n" + val("reactie-bericht"),
      };
    }
    if (soort === "correctie") {
      if (!requireFilled("reactie-waar", "Waar")) return null;
      if (!requireFilled("reactie-wat", "Wat klopt niet")) return null;
      let body = "Waar: " + val("reactie-waar") + "\n\n" + val("reactie-wat");
      const bron = val("reactie-bron-correctie");
      if (bron) body += "\n\nBron: " + bron;
      return { subject: "[correctie] " + val("reactie-waar"), body: body };
    }
    if (soort === "anders") {
      if (!requireFilled("reactie-anders", "Uw bericht")) return null;
      return {
        subject: "[anders] kalender",
        body: val("reactie-anders"),
      };
    }
    if (!requireFilled("reactie-naam", "Naam")) return null;
    if (!requireFilled("reactie-waarom", "Waarom hoort deze heilige in de kalender?")) {
      return null;
    }
    let body = "Naam: " + val("reactie-naam") + "\n";
    const feestdag = val("reactie-feestdag");
    if (feestdag) body += "Feestdag: " + feestdag + "\n";
    body += "\n" + val("reactie-waarom");
    const bronnen = val("reactie-bronnen");
    if (bronnen) body += "\n\nBronnen: " + bronnen;
    return { subject: "[heilige] " + val("reactie-naam"), body: body };
  }

  soortSelect.addEventListener("change", showSet);
  showSet();

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (status) {
      status.hidden = true;
      status.textContent = "";
    }
    if (!email) return;
    const mail = buildMail();
    if (!mail) return;
    const href =
      "mailto:" +
      email +
      "?subject=" +
      encodeURIComponent(mail.subject) +
      "&body=" +
      encodeURIComponent(mail.body);
    window.location.href = href;
    if (status) {
      status.hidden = false;
      status.textContent =
        "Als er geen e-mailprogramma opent, stuur het bericht zelf naar " + email + ".";
    }
  });
})();
