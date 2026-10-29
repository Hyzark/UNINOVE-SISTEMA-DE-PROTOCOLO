import { api } from "./api.js";
import { settings, applySettings } from "./settings.js";
import { showToast } from "./api.js";
import { abrirPagina } from "./router.js";
import { loadProcesses, selectMesa } from "./processes.js";
import { state, CREATE_MESA_VALUE, refreshMesaSelect } from "./state.js";

document.querySelectorAll(".menu-item").forEach(item => item.addEventListener("click", event => {
  event.preventDefault();
  if (item.dataset.page === "inicio" && state.mesa) {
    loadProcesses(state.mesa.id)
      .then(() => abrirPagina("inicio"))
      .catch(error => showToast(error.message));
    return;
  }
  abrirPagina(item.dataset.page);
}));
document.addEventListener("click", event => {
  const process = event.target.closest("[data-open-process]");
  if (process) abrirPagina("processo", { id: process.dataset.openProcess });
});
document.getElementById("settings-button").addEventListener("click", () => abrirPagina("configuracoes"));
document.getElementById("profile-button").addEventListener("click", () => abrirPagina("perfil"));

const mesaSelect = document.getElementById("mesa-select");
mesaSelect.addEventListener("change", async () => {
  if (mesaSelect.value === CREATE_MESA_VALUE) {
    if (state.mesa) mesaSelect.value = String(state.mesa.id);
    else mesaSelect.selectedIndex = -1;
    abrirPagina("criar-mesa");
    return;
  }
  try {
    state.mesa = await selectMesa(mesaSelect.value);
    localStorage.setItem("pd-mesa-id", String(state.mesa.id));
    await loadProcesses(state.mesa.id);
    await abrirPagina("inicio");
  } catch (error) { showToast(error.message); }
});

document.getElementById("search-form").addEventListener("submit", async event => {
  event.preventDefault();
  const term = document.getElementById("global-search").value.trim().toLowerCase();
  if (!term) return;
  try {
    const matches = await api(`/processos/busca?termo=${encodeURIComponent(term)}`);
    if (!matches.length) showToast("Nenhum processo encontrado neste setor.");
    else if (matches.length === 1) abrirPagina("processo", { id: matches[0].id });
    else {
      state.searchTerm = document.getElementById("global-search").value.trim();
      state.searchResults = matches;
      abrirPagina("resultados-busca");
    }
  } catch (error) { showToast(error.message); }
});

document.getElementById("logout-button").addEventListener("click", async () => {
  try { await api("/logout", { method: "POST" }); } finally { window.location.assign("/"); }
});

async function start() {
  applySettings();
  try {
    state.user = await api("/sessao");
    document.querySelectorAll("[data-admin-only]").forEach(item => { item.hidden = state.user.perfil !== "admin"; });
    document.getElementById("user-name").textContent = state.user.nome;
    document.getElementById("user-sector").textContent = state.user.setor || "Setor não informado";
    document.getElementById("user-avatar").textContent = (state.user.nome || "?").trim().slice(0, 1).toLocaleUpperCase("pt-BR");
    document.getElementById("today-date").textContent = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", year: "numeric" }).format(new Date());
    state.mesas = await api("/minhas-mesas");
    refreshMesaSelect();
    if (!state.mesas.length) {
      if (state.user.perfil === "admin") {
        await abrirPagina("inicio");
        return;
      }
      document.getElementById("page-content").innerHTML = '<div class="empty-state">Nenhuma mesa ativa está cadastrada para o seu setor.</div>';
      return;
    }
    const requestedId = localStorage.getItem("pd-mesa-id");
    const chosen = state.mesas.find(m => String(m.id) === requestedId) || state.mesas[0];
    state.mesa = await selectMesa(chosen.id);
    refreshMesaSelect(chosen.id);
    await loadProcesses(chosen.id);
    await abrirPagina("inicio");
  } catch (error) {
    if (error.message) showToast(error.message);
  }
}

start();
