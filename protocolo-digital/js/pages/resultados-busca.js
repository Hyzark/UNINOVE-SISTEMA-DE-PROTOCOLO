import { state } from "../state.js";
import { escapeHtml, formatDate } from "../api.js";
import { statusClass } from "../ui.js";

export function init(root) {
  const results = state.searchResults || [];
  root.querySelector("#search-result-count").textContent = `${results.length} ${results.length === 1 ? "processo encontrado" : "processos encontrados"} no setor.`;
  root.querySelector("#search-result-body").innerHTML = results.map(process => `
    <tr>
      <td><button type="button" class="link-button" data-open-process="${Number(process.id)}">${escapeHtml(process.numero)}</button></td>
      <td>${escapeHtml(process.assunto)}</td>
      <td>${escapeHtml(process.mesa || "Sem mesa")}</td>
      <td>${escapeHtml(formatDate(process.atualizado_em))}</td>
      <td><span class="status-badge ${statusClass(process.situacao)}">${escapeHtml(process.situacao || "—")}</span></td>
    </tr>`).join("");
}
