import { api, jsonOptions, showToast } from "../api.js";
import { bindAdminHistory } from "../admin-history.js";

export async function init(root, ctx) {
  const form = root.querySelector("#employee-form");
  const sectorSelect = form.elements.setor_id;
  bindAdminHistory(root.querySelector("#consult-employee-history"), root.querySelector("#employee-history"), "/usuarios/historico", "Nenhum funcionário ou gerente foi cadastrado pelo sistema ainda.");
  root.querySelector("#cancel-employee").addEventListener("click", () => ctx.navigate("inicio"));
  try {
    const sectors = await api("/setores", { cache: "no-store" });
    sectorSelect.replaceChildren(new Option("Selecione o setor", ""));
    sectors.forEach(sector => sectorSelect.add(new Option(sector.nome, sector.id)));
    if (!sectors.length) {
      sectorSelect.replaceChildren(new Option("Nenhum setor ativo cadastrado", ""));
      showToast("Cadastre um setor antes de adicionar funcionários.");
    }
  } catch (error) {
    sectorSelect.replaceChildren(new Option("Não foi possível carregar os setores", ""));
    showToast(error.message);
  }
  form.elements.nome.focus();
  form.addEventListener("submit", async event => {
    event.preventDefault();
    const data = new FormData(form);
    const cadastro = {
      nome: data.get("nome").trim(),
      cargo: data.get("cargo").trim(),
      email: data.get("email").trim(),
      senha: data.get("senha"),
      setor_id: Number(data.get("setor_id")),
      nivel_acesso: Number(data.get("nivel_acesso"))
    };
    try {
      const result = await api("/cadastrarfuncionario", jsonOptions("POST", cadastro));
      showToast(result.mensagem || "Funcionário cadastrado.");
      form.reset();
      form.elements.nome.focus();
    } catch (error) { showToast(error.message); }
  });
}
