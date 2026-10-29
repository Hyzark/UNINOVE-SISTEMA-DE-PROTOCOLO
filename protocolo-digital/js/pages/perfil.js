import { state } from "../state.js";

export function init(root) {
  const user = state.user;
  if (!user) return;
  root.querySelector("#profile-name").textContent = user.nome || "—";
  root.querySelector("#profile-email").textContent = user.email || "—";
  root.querySelector("#profile-sector").textContent = user.setor || "—";
  root.querySelector("#profile-role").textContent = ({ admin: "Administrador", gerente: "Gerente", funcionario: "Funcionário" })[user.perfil] || "Usuário";
  root.querySelector("#profile-avatar").textContent = (user.nome || "?").trim().slice(0, 1).toLocaleUpperCase("pt-BR");
  root.querySelector('[data-bind="mesa"]').textContent = state.mesa?.nome || "Nenhuma mesa selecionada";
}
