import { api, escapeHtml, formatDate, showToast } from "./api.js";

export function bindAdminHistory(button, panel, endpoint, emptyMessage) {
  button.addEventListener("click", async () => {
    if (!panel.hidden) {
      panel.hidden = true;
      button.textContent = "Consultar histórico";
      button.setAttribute("aria-expanded", "false");
      return;
    }
    button.disabled = true;
    try {
      const events = await api(endpoint, { cache: "no-store" });
      panel.innerHTML = events.length
        ? `<h3>Histórico de cadastros</h3><div class="table-container"><table class="process-table"><thead><tr><th>Data/Hora</th><th>Administrador</th><th>Ação</th><th>Descrição</th></tr></thead><tbody>${events.map(event => `<tr><td>${escapeHtml(formatDate(event.criado_em))}</td><td>${escapeHtml(event.usuario)}</td><td>${escapeHtml(event.acao)}</td><td>${escapeHtml(event.descricao || "")}</td></tr>`).join("")}</tbody></table></div>`
        : `<div class="empty-state">${escapeHtml(emptyMessage)}</div>`;
      panel.hidden = false;
      button.textContent = "Ocultar histórico";
      button.setAttribute("aria-expanded", "true");
    } catch (error) { showToast(error.message); }
    finally { button.disabled = false; }
  });
}
