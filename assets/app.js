// Progressive enhancement: the page is complete without JS.
// This adds the theme toggle and the publication filter.
(() => {
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch { /* ignore */ } },
  };

  // ---- theme ----
  const themeBtn = document.querySelector(".theme-btn");
  if (themeBtn) {
    themeBtn.hidden = false;
    const media = matchMedia("(prefers-color-scheme: dark)");
    const current = () => document.documentElement.dataset.theme || (media.matches ? "dark" : "light");
    themeBtn.addEventListener("click", () => {
      const next = current() === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = next;
      store.set("theme", next);
    });
  }

  // ---- publication filter ----
  const form = document.querySelector(".pub-filter");
  if (!form) return;
  form.hidden = false;

  const q = document.getElementById("pub-q");
  const major = document.getElementById("pub-major");
  const count = document.getElementById("pub-count");
  const empty = document.getElementById("pub-empty");
  const chips = [...form.querySelectorAll(".chip")];
  const groups = [...document.querySelectorAll("#pub-list .year-group")];
  const items = [...document.querySelectorAll("#pub-list .pub")].map((el) => ({
    el,
    cat: el.dataset.cat,
    major: el.dataset.major === "true",
    text: el.textContent.toLowerCase(),
  }));
  let cat = "all";

  const apply = () => {
    const term = q.value.trim().toLowerCase();
    let shown = 0;
    for (const it of items) {
      const ok = (cat === "all" || it.cat === cat) && (!major.checked || it.major) && (!term || it.text.includes(term));
      it.el.hidden = !ok;
      if (ok) shown++;
    }
    for (const g of groups) g.hidden = !g.querySelector(".pub:not([hidden])");
    empty.hidden = shown > 0;
    count.textContent = `${shown} / ${items.length}`;
  };

  chips.forEach((chip) =>
    chip.addEventListener("click", () => {
      cat = chip.dataset.cat;
      chips.forEach((c) => c.setAttribute("aria-pressed", String(c === chip)));
      apply();
    })
  );
  q.addEventListener("input", apply);
  major.addEventListener("change", apply);
  apply();
})();
