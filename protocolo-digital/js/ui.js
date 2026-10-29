import { escapeHtml, formatDate } from "./api.js";

export function statusClass(value = "") {
  const status = value.toLocaleLowerCase("pt-BR");
  if (status.includes("em análise") || status.includes("em analise")) return "status-analysis";
  if (status.includes("aguardando solicitação") || status.includes("aguardando solicitacao")) return "status-waiting";
  if (status.includes("em andamento")) return "status-in-progress";
  if (status.includes("conclu")) return "status-done";
  if (status.includes("sobrest")) return "status-suspended";
  if (status.includes("pend")) return "status-pending";
  return "status-progress";
}

export function renderTableRows(list) {
  if (!list.length) return '<tr><td colspan="4"><div class="empty-state">Nenhum processo encontrado.</div></td></tr>';
  return list.map(p => `<tr>
    <td><button type="button" class="link-button" data-open-process="${Number(p.id)}">${escapeHtml(p.numero)}</button></td>
    <td>${escapeHtml(p.assunto)}</td><td>${formatDate(p.atualizado_em)}</td>
    <td><span class="status-badge ${statusClass(p.situacao)}">${escapeHtml(p.situacao || "—")}</span></td>
  </tr>`).join("");
}
