import { Store } from "./store.js";

function effectiveTheme() {
  const attr = document.documentElement.getAttribute("data-theme");
  if (attr === "light" || attr === "dark") return attr;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function syncToggleButtons() {
  const isDark = effectiveTheme() === "dark";
  document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
    btn.setAttribute("aria-pressed", String(isDark));
    const label = btn.querySelector("[data-theme-toggle-label]");
    if (label) label.textContent = isDark ? "Giao diện sáng" : "Giao diện tối";
  });
}

function toggle() {
  const next = effectiveTheme() === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  Store.set("theme", next);
  syncToggleButtons();
}

document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-theme-toggle]");
  if (btn) toggle();
});

syncToggleButtons();
