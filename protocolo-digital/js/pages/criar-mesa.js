import { api, jsonOptions, showToast } from "../api.js";
import { loadProcesses, selectMesa } from "../processes.js";
import { state, refreshMesaSelect } from "../state.js";

export function init(root, ctx) {
  const form = root.querySelector("#mesa-form");
  root.querySelector("#cancel-mesa").addEventListener("click", () => ctx.navigate("inicio"));
  form.elements.nome.focus();
  form.addEventListener("submit", async event => {
    event.preventDefault();
    const nome = form.elements.nome.value.trim();
    if (!nome) return showToast("Informe o nome da mesa.");
    try {
      const result = await api("/cadastrarMesa", jsonOptions("POST", { nome }));
      state.mesas = await api("/minhas-mesas");
      state.mesa = await selectMesa(result.id);
      localStorage.setItem("pd-mesa-id", String(state.mesa.id));
      refreshMesaSelect(state.mesa.id);
      await loadProcesses(state.mesa.id);
      showToast(`Mesa “${state.mesa.nome}” criada.`);
      await ctx.navigate("inicio");
    } catch (error) { showToast(error.message); }
  });
}
