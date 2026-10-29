import { api, jsonOptions } from "./api.js";

let processList = [];
export const setProcessList = list => { processList = list; };
export const processosDaMesa = () => processList;
export const findProcess = id => processList.find(process => String(process.id) === String(id));

export async function loadProcesses(mesaId) {
  const list = await api(`/mesas/${mesaId}/processos`, { cache: "no-store" });
  setProcessList(list);
  return list;
}

export async function selectMesa(mesaId) {
  return api("/mesa-atual", jsonOptions("POST", { mesa_id: Number(mesaId) }));
}
