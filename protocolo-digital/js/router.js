import { api } from "./api.js";
import { state } from "./state.js";

const pageContent = document.getElementById("page-content");
const pageTitle = document.getElementById("page-title");
const pageSubtitle = document.getElementById("page-subtitle");
const pages = {
  "inicio": { title: "Processos", subtitle: () => `Processos da mesa ${state.mesa?.nome || ""}.`, logic: true },
  "resultados-busca": { title: "Resultados da busca", subtitle: () => `Resultados para “${state.searchTerm}” em todo o setor.`, logic: true },
  "processo": { title: "Processo", subtitle: "Detalhes, documentos e histórico.", logic: true },
  "iniciar-processo": { title: "Iniciar Processo", subtitle: "Registre um processo na mesa selecionada.", logic: true },
  "criar-mesa": { title: "Criar mesa", subtitle: () => `Nova mesa para o setor ${state.user?.setor || ""}.`, logic: true },
  "criar-setor": { title: "Criar setor", subtitle: "Cadastre um novo setor no sistema.", logic: true },
  "adicionar-funcionario": { title: "Adicionar funcionário", subtitle: "Cadastre um funcionário ou gerente para um setor.", logic: true },
  "configuracoes": { title: "Configurações", subtitle: "Preferências de aparência.", logic: true },
  "perfil": { title: "Perfil", subtitle: "Dados da sua conta e do setor.", logic: true }
};
let navigationId = 0;

async function loadTemplate(name) {
  const response = await fetch(`/protocolo/templates/${name}.html`);
  if (!response.ok) throw new Error("Tela indisponível.");
  return response.text();
}

export async function abrirPagina(name, params = {}) {
  const page = pages[name];
  if (!page) return;
  const id = ++navigationId;
  pageTitle.textContent = typeof page.title === "function" ? page.title(params) : page.title;
  pageSubtitle.textContent = typeof page.subtitle === "function" ? page.subtitle(params) : page.subtitle;
  document.querySelectorAll(".menu-item").forEach(item => item.classList.toggle("active", item.dataset.page === name));
  try {
    const [html, module] = await Promise.all([
      loadTemplate(name), page.logic ? import(`/protocolo/js/pages/${name}.js`) : null
    ]);
    if (id !== navigationId) return;
    pageContent.innerHTML = html;
    if (module) await module.init(pageContent, { navigate: abrirPagina }, params);
  } catch (error) {
    if (id !== navigationId) return;
    console.error(error);
    pageContent.innerHTML = `<div class="empty-state">${error.message || "Não foi possível carregar esta tela."}</div>`;
  }
  window.scrollTo({ top: 0, behavior: "smooth" });
}
