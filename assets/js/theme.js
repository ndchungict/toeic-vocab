(function () {
  var KEY = "toeic:v2";

  function readStore() {
    try {
      return JSON.parse(localStorage.getItem(KEY)) || {};
    } catch (e) {
      return {};
    }
  }

  function writeTheme(theme) {
    var store = readStore();
    store.theme = theme;
    localStorage.setItem(KEY, JSON.stringify(store));
  }

  function effectiveTheme() {
    var attr = document.documentElement.getAttribute("data-theme");
    if (attr === "light" || attr === "dark") return attr;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function syncToggleButtons() {
    var isDark = effectiveTheme() === "dark";
    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", String(isDark));
      var label = btn.querySelector("[data-theme-toggle-label]");
      if (label) label.textContent = isDark ? "Giao diện sáng" : "Giao diện tối";
    });
  }

  function toggle() {
    var next = effectiveTheme() === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    writeTheme(next);
    syncToggleButtons();
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-theme-toggle]");
    if (btn) toggle();
  });

  syncToggleButtons();
})();
