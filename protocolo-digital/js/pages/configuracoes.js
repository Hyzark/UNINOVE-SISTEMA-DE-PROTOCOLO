import { settings, applySettings } from "../settings.js";

export function init(root) {
  const mark = () => {
    root.querySelectorAll("[data-theme-option]").forEach(b => {
      const on = b.dataset.themeOption === settings.theme;
      b.classList.toggle("active", on);
      b.setAttribute("aria-pressed", on);
    });
    root.querySelectorAll("[data-font-option]").forEach(b => {
      const on = Number(b.dataset.fontOption) === settings.font;
      b.classList.toggle("active", on);
      b.setAttribute("aria-pressed", on);
    });
  };

  root.querySelectorAll("[data-theme-option]").forEach(b => b.addEventListener("click", () => {
    settings.theme = b.dataset.themeOption; applySettings(); mark();
  }));
  root.querySelectorAll("[data-font-option]").forEach(b => b.addEventListener("click", () => {
    settings.font = Number(b.dataset.fontOption); applySettings(); mark();
  }));
  mark();
}
