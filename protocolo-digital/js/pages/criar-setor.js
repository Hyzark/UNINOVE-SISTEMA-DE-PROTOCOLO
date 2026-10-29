import { api, jsonOptions, showToast } from "../api.js";
import { bindAdminHistory } from "../admin-history.js";

export function init(root, ctx) {
  const form = root.querySelector("#sector-form");
  bindAdminHistory(root.querySelector("#consult-sector-history"), root.querySelector("#sector-history"), "/setores/historico", "Nenhum setor foi cadastrado pelo sistema ainda.");
  root.querySelector("#cancel-sector").addEventListener("click", () => ctx.navigate("inicio"));
  form.elements.nome.focus();
  form.addEventListener("submit", async event => {
    event.preventDefault();
    const nome = form.elements.nome.value.trim();
    if (!nome) return showToast("Informe o nome do setor.");
    try {
      const result = await api("/cadastrarsetor", jsonOptions("POST", {
        nome, descricao: form.elements.descricao.value.trim()
      }));
      showToast(result.mensagem || "Setor criado.");
      form.reset();
      form.elements.nome.focus();
    } catch (error) { showToast(error.message); }
  });
}
