export const state = { user: null, mesas: [], mesa: null, searchResults: [], searchTerm: "" };
export const CREATE_MESA_VALUE = "__create_mesa__";

export function refreshMesaSelect(selectedId = state.mesa?.id) {
  const select = document.getElementById("mesa-select");
  if (!select) return;
  const options = state.mesas.map(mesa => new Option(mesa.nome, mesa.id));
  options.push(new Option("+ Criar mesa", CREATE_MESA_VALUE));
  select.replaceChildren(...options);
  if (selectedId) select.value = String(selectedId);
  else if (!state.mesas.length) select.selectedIndex = -1;
  else select.value = CREATE_MESA_VALUE;
}
