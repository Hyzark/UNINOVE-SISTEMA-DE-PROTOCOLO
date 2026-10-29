import { api, jsonOptions, showToast } from "../api.js";

export function init(root, ctx) {
  const form = root.querySelector("#request-form");
  root.querySelector("#cancel-request").addEventListener("click", () => ctx.navigate("inicio"));
  form.addEventListener("submit", async event => {
    event.preventDefault();
    const data = new FormData(form);
    try {
      const result = await api("/processos", jsonOptions("POST", {
        assunto: data.get("assunto"), descricao: data.get("descricao")
      }));
      showToast(`Processo ${result.numero} criado.`);
      ctx.navigate("processo", { id: result.id });
    } catch (error) { showToast(error.message); }
  });
}
