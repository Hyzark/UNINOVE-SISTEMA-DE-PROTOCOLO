export const settings = { theme: "light", font: 1 };
try {
  const saved = JSON.parse(localStorage.getItem("pd-settings"));
  if (saved && ["light", "dark"].includes(saved.theme)) settings.theme = saved.theme;
  if (saved && [0.9, 1, 1.15].includes(saved.font)) settings.font = saved.font;
} catch { /* Preferências locais inválidas são ignoradas. */ }

export function applySettings() {
  document.documentElement.dataset.theme = settings.theme;
  document.documentElement.style.setProperty("--fs", settings.font);
  try { localStorage.setItem("pd-settings", JSON.stringify(settings)); } catch { /* O navegador pode bloquear o armazenamento local. */ }
}
