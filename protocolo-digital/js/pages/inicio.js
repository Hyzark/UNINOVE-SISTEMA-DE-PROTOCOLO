import { processosDaMesa } from "../processes.js";
import { renderTableRows } from "../ui.js";

const ageDays = value => {
  if (!value) return Infinity;
  const date = new Date(`${value.replace(" ", "T")}Z`);
  return Number.isNaN(date.getTime()) ? Infinity : (Date.now() - date.getTime()) / 86400000;
};

export function init(root, _ctx, params = {}) {
  const list = processosDaMesa();
  const stats = {
    total: list.length,
    recentes: list.filter(p => ageDays(p.criado_em) <= 7).length,
    parados: list.filter(p => ageDays(p.atualizado_em) > 15).length
  };
  root.querySelectorAll("[data-stat]").forEach(el => { el.textContent = stats[el.dataset.stat] ?? 0; });
  const filter = root.querySelector("#status-filter");
  [...new Set(list.map(p => p.situacao).filter(Boolean))].sort((a, b) => a.localeCompare(b, "pt-BR")).forEach(status => {
    filter.add(new Option(status, status));
  });
  const search = root.querySelector("#process-search");
  const update = () => {
    const term = search.value.trim().toLocaleLowerCase("pt-BR");
    const status = filter.value;
    const result = list.filter(p => (!term || p.numero.toLocaleLowerCase("pt-BR").includes(term) || p.assunto.toLocaleLowerCase("pt-BR").includes(term)) && (!status || p.situacao === status));
    root.querySelector("#process-table-body").innerHTML = renderTableRows(result);
    root.querySelector("#process-count").textContent = `${result.length} ${result.length === 1 ? "processo" : "processos"}`;
  };
  search.addEventListener("input", update);
  filter.addEventListener("change", update);
  if (params.search) search.value = params.search;
  update();
}
