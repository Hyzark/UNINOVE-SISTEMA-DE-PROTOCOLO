import { api, jsonOptions, escapeHtml, formatDate, showToast } from "../api.js";
import { statusClass } from "../ui.js";

export async function init(root, ctx, params = {}) {
  const processId = Number(params.id);
  if (!processId) { showToast("Processo inválido."); return ctx.navigate("inicio"); }
  let p;
  try { p = await api(`/processos/${processId}`); }
  catch (error) { showToast(error.message); return ctx.navigate("inicio"); }

  document.getElementById("page-title").textContent = `Processo ${p.numero}`;
  document.getElementById("page-subtitle").textContent = p.assunto || "Detalhes, documentos e histórico.";

  const content = root.querySelector("#process-content");
  const docs = root.querySelector("#doc-list");
  const upload = root.querySelector("#upload-form");
  const attachmentEditor = root.querySelector("#edit-attachment-form");
  const editor = root.querySelector("#editor-panel");
  let editorialId = null;
  let attachmentId = null;

  root.querySelector("#tree-number").textContent = p.numero;
  const status = root.querySelector("#tree-status");
  status.textContent = p.situacao || "—";
  status.classList.add(statusClass(p.situacao));

  function renderDocs() {
    const linkedPdfIds = new Set(p.documentos_editoriais.map(d => Number(d.pdf_documento_id)).filter(Boolean));
    const uploaded = p.documentos.filter(d => !linkedPdfIds.has(Number(d.id)));
    const rows = [
      ...uploaded.map(d => `<li class="document-row"><button type="button" class="doc-open" data-file="${d.id}"><span class="doc-icon file-icon">ARQ</span><span class="doc-info"><span class="doc-name">${escapeHtml(d.nome)}</span><span class="doc-unit">${escapeHtml(formatDate(d.criado_em))}</span></span></button><div class="document-actions"><a class="document-action" href="/documentos/${d.id}/download" download title="Baixar">↓</a><button class="document-action" type="button" data-edit-file="${d.id}" title="Editar anexo">✎</button></div></li>`),
      ...p.documentos_editoriais.map(d => `<li class="document-row"><button type="button" class="doc-open" ${d.pdf_documento_id ? `data-file="${d.pdf_documento_id}"` : "disabled"}><span class="doc-icon pdf">PDF</span><span class="doc-info"><span class="doc-name">${escapeHtml(d.nome)}.pdf</span><span class="doc-unit">Documento criado · ${escapeHtml(formatDate(d.atualizado_em))}</span></span></button><div class="document-actions">${d.pdf_documento_id ? `<a class="document-action" href="/documentos/${d.pdf_documento_id}/download" download title="Baixar PDF">↓</a>` : ""}<button class="document-action" type="button" data-edit-editorial="${d.id}" title="Editar conteúdo">✎</button></div></li>`)
    ];
    docs.innerHTML = rows.length ? rows.join("") : '<li class="tree-empty">Nenhum documento neste processo.</li>';
  }

  function showDetails() {
    upload.hidden = true; attachmentEditor.hidden = true; editor.hidden = true;
    const rows = [["Número", p.numero], ["Assunto", p.assunto], ["Descrição", p.descricao], ["Situação", p.situacao], ["Setor responsável", p.setor], ["Mesa atual", p.mesa], ["Criado por", p.criado_por], ["Criado em", formatDate(p.criado_em)], ["Última atualização", formatDate(p.atualizado_em)]];
    content.innerHTML = `<div class="viewer-head"><div><h3>Dados do processo</h3></div></div><dl class="details">${rows.map(([k, v]) => `<dt>${escapeHtml(k)}</dt><dd>${escapeHtml(v || "—")}</dd>`).join("")}</dl>`;
  }

  function showStatusEditor() {
    upload.hidden = true; attachmentEditor.hidden = true; editor.hidden = true;
    const statuses = ["Em análise", "Em andamento", "Aguardando solicitação"];
    content.innerHTML = `<div class="viewer-head"><div><h3>Status do processo</h3><p>Selecione a nova situação do processo.</p></div></div><form id="process-status-form" class="status-editor"><label class="form-field" for="process-status">Status<select class="field-control" id="process-status" name="situacao" required>${statuses.map(value => `<option value="${escapeHtml(value)}" ${p.situacao === value ? "selected" : ""}>${escapeHtml(value)}</option>`).join("")}</select></label><div class="form-actions"><button class="primary-button" type="submit">Salvar status</button></div></form>`;
  }

  function showHistory() {
    upload.hidden = true; attachmentEditor.hidden = true; editor.hidden = true;
    const events = p.historico || [];
    content.innerHTML = `<div class="viewer-head"><div><h3>Andamento do processo</h3><p>${events.length} registros</p></div></div>${events.length ? `<div class="table-container"><table class="process-table"><thead><tr><th>Data/Hora</th><th>Usuário</th><th>Ação</th><th>Descrição</th></tr></thead><tbody>${events.map(e => `<tr><td>${escapeHtml(formatDate(e.criado_em))}</td><td>${escapeHtml(e.usuario)}</td><td>${escapeHtml(e.acao)}</td><td>${escapeHtml(e.descricao || "")}</td></tr>`).join("")}</tbody></table></div>` : '<div class="empty-state">Nenhum evento registrado.</div>'}`;
  }

  async function openFile(id) {
    upload.hidden = true; attachmentEditor.hidden = true; editor.hidden = true;
    const doc = p.documentos.find(d => d.id === Number(id));
    if (!doc) return;
    const url = `/documentos/${doc.id}/preview`;
    const downloadUrl = `/documentos/${doc.id}/download`;
    const editorial = p.documentos_editoriais.find(d => Number(d.pdf_documento_id) === Number(doc.id));
    const editButton = editorial
      ? `<button class="primary-button" type="button" data-edit-editorial="${editorial.id}">Editar documento</button>`
      : `<button class="primary-button" type="button" data-edit-file="${doc.id}">Editar anexo</button>`;
    content.innerHTML = `<div class="viewer-head"><div><h3>${escapeHtml(doc.nome)}</h3><p>Enviado por ${escapeHtml(doc.enviado_por)} · ${escapeHtml(formatDate(doc.criado_em))}</p></div><div class="preview-actions"><a class="secondary-button" href="${downloadUrl}" download>Baixar</a>${editButton}</div></div><div class="preview-body" id="file-preview"><div class="empty-state">Carregando prévia...</div></div>`;
    const preview = content.querySelector("#file-preview");
    try {
      const response = await fetch(url, { credentials: "same-origin" });
      if (!response.ok) throw new Error("Não foi possível abrir a prévia deste arquivo.");
      const type = response.headers.get("content-type") || "";
      if (!type.includes("application/json")) {
        preview.innerHTML = `<iframe class="document-frame" title="Prévia de ${escapeHtml(doc.nome)}" src="${url}"></iframe>`;
        return;
      }
      const data = await response.json();
      if (data.kind === "spreadsheet") {
        const table = document.createElement("table"); table.className = "preview-table";
        for (const row of data.rows || []) { const tr = document.createElement("tr"); for (const value of row) { const cell = document.createElement("td"); cell.textContent = value ?? ""; tr.append(cell); } table.append(tr); }
        preview.replaceChildren(); const title = document.createElement("h4"); title.textContent = data.sheet || "Planilha"; preview.append(title, table);
      } else if (data.kind === "archive") {
        const table = document.createElement("table"); table.className = "preview-table";
        const head = document.createElement("tr"); ["Arquivo", "Tamanho", "Compactado"].forEach(label => { const th = document.createElement("th"); th.textContent = label; head.append(th); }); table.append(head);
        for (const item of data.entries || []) { const tr = document.createElement("tr"); [item.name, formatSize(item.size), formatSize(item.compressed_size)].forEach(value => { const td = document.createElement("td"); td.textContent = value; tr.append(td); }); table.append(tr); }
        preview.replaceChildren(table);
      } else if (data.kind === "text") {
        const pre = document.createElement("pre"); pre.className = "text-preview"; pre.textContent = data.text || ""; preview.replaceChildren(pre);
      } else {
        const message = document.createElement("div"); message.className = "empty-state"; message.textContent = data.message || "Não há prévia disponível para este formato."; preview.replaceChildren(message);
      }
      if (data.message) { const note = document.createElement("p"); note.className = "preview-note"; note.textContent = data.message; preview.append(note); }
    } catch (error) { preview.textContent = error.message; }
  }

  function formatSize(size = 0) { return size < 1024 ? `${size} B` : size < 1024 * 1024 ? `${(size / 1024).toFixed(1)} KB` : `${(size / (1024 * 1024)).toFixed(1)} MB`; }

  function editAttachment(id) {
    const doc = p.documentos.find(d => d.id === Number(id));
    if (!doc) return;
    attachmentId = doc.id;
    upload.hidden = true; editor.hidden = true; attachmentEditor.hidden = false;
    attachmentEditor.elements.titulo.value = doc.nome;
    attachmentEditor.elements.arquivo.value = "";
    content.innerHTML = "";
    attachmentEditor.elements.titulo.focus();
  }

  async function editDocument(id) {
    try {
      const d = await api(`/documentos-editoriais/${id}`);
      editorialId = d.id;
      root.querySelector("#editor-heading").textContent = "Editar documento";
      root.querySelector("#editor-name").value = d.nome;
      root.querySelector("#editor-body").innerHTML = d.conteudo_html;
      const imageCount = root.querySelectorAll("#editor-body img").length;
      root.querySelector("#image-status").textContent = imageCount ? `${imageCount} imagem(ns) já salva(s) neste documento.` : "Nenhuma imagem inserida.";
      upload.hidden = true; attachmentEditor.hidden = true; editor.hidden = false;
      content.innerHTML = "";
    } catch (error) { showToast(error.message); }
  }

  docs.addEventListener("click", event => {
    const file = event.target.closest("[data-file]");
    if (file) openFile(file.dataset.file);
    const editFile = event.target.closest("[data-edit-file]");
    if (editFile) editAttachment(editFile.dataset.editFile);
    const editEditorial = event.target.closest("[data-edit-editorial]");
    if (editEditorial) editDocument(editEditorial.dataset.editEditorial);
  });
  content.addEventListener("click", event => {
    const editFile = event.target.closest("[data-edit-file]");
    if (editFile) editAttachment(editFile.dataset.editFile);
    const editEditorial = event.target.closest("[data-edit-editorial]");
    if (editEditorial) editDocument(editEditorial.dataset.editEditorial);
  });
  content.addEventListener("submit", async event => {
    if (event.target.id !== "process-status-form") return;
    event.preventDefault();
    const situacao = new FormData(event.target).get("situacao");
    try {
      await api(`/processos/${processId}/situacao`, jsonOptions("PATCH", { situacao }));
      showToast("Status do processo atualizado.");
      ctx.navigate("processo", { id: processId });
    } catch (error) { showToast(error.message); }
  });
  root.querySelector(".process-actions").addEventListener("click", event => {
    const action = event.target.closest("[data-action]")?.dataset.action;
    if (action === "consultar") showDetails();
    if (action === "status") showStatusEditor();
    if (action === "andamento") showHistory();
    if (action === "anexar") { editor.hidden = true; attachmentEditor.hidden = true; upload.hidden = !upload.hidden; if (!upload.hidden) upload.elements.titulo.focus(); }
    if (action === "novo-documento") {
      editorialId = null;
      root.querySelector("#editor-heading").textContent = "Novo documento";
      root.querySelector("#editor-name").value = "";
      root.querySelector("#editor-body").innerHTML = "";
      root.querySelector("#image-status").textContent = "Nenhuma imagem inserida.";
      upload.hidden = true; attachmentEditor.hidden = true; editor.hidden = false;
    }
  });

  upload.addEventListener("submit", async event => {
    event.preventDefault();
    const data = new FormData(upload);
    try {
      await api(`/processos/${processId}/documentos`, { method: "POST", body: data });
      showToast("Arquivo anexado.");
      ctx.navigate("processo", { id: processId });
    } catch (error) { showToast(error.message); }
  });
  root.querySelector("[data-cancel-upload]").addEventListener("click", () => { upload.hidden = true; });
  root.querySelector("[data-cancel-edit-attachment]").addEventListener("click", () => { attachmentEditor.hidden = true; showDetails(); });
  attachmentEditor.addEventListener("submit", async event => {
    event.preventDefault();
    if (!attachmentId) return;
    try {
      await api(`/documentos/${attachmentId}`, { method: "PUT", body: new FormData(attachmentEditor) });
      showToast("Anexo atualizado.");
      ctx.navigate("processo", { id: processId });
    } catch (error) { showToast(error.message); }
  });

  root.querySelectorAll(".editor-toolbar [data-cmd]").forEach(button => {
    button.addEventListener("mousedown", event => event.preventDefault());
    button.addEventListener("click", () => {
      root.querySelector("#editor-body").focus();
      document.execCommand(button.dataset.cmd, false, button.dataset.value || null);
    });
  });
  let savedRange = null;
  const editorBody = root.querySelector("#editor-body");
  const imageButton = root.querySelector("#insert-image");
  const imageFile = root.querySelector("#image-file");
  imageButton.addEventListener("mousedown", event => {
    event.preventDefault();
    const selection = window.getSelection();
    if (selection.rangeCount && editorBody.contains(selection.anchorNode)) savedRange = selection.getRangeAt(0).cloneRange();
  });
  imageButton.addEventListener("click", () => imageFile.click());
  imageFile.addEventListener("change", async event => {
    const file = event.target.files?.[0];
    if (!file) return;
    const allowed = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp"].includes(file.type);
    if (!allowed || file.size > 20 * 1024 * 1024) {
      showToast(!allowed ? "Use uma imagem PNG, JPG/JPEG, GIF ou WebP." : "A imagem excede o limite de 20 MB.");
      imageFile.value = "";
      return;
    }
    try {
      const bitmap = await createImageBitmap(file);
      const scale = Math.min(1, 1600 / bitmap.width, 1600 / bitmap.height);
      const canvas = document.createElement("canvas");
      canvas.width = Math.max(1, Math.round(bitmap.width * scale));
      canvas.height = Math.max(1, Math.round(bitmap.height * scale));
      const context = canvas.getContext("2d");
      const type = file.type === "image/png" ? "image/png" : "image/jpeg";
      if (type === "image/jpeg") { context.fillStyle = "#fff"; context.fillRect(0, 0, canvas.width, canvas.height); }
      context.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
      bitmap.close();
      const blob = await new Promise((resolve, reject) => canvas.toBlob(value => value ? resolve(value) : reject(new Error("Não foi possível preparar a imagem.")), type, 0.82));
      if (blob.size > 4 * 1024 * 1024) throw new Error("A imagem continua grande após a otimização. Escolha uma imagem menor.");
      const dataUrl = await new Promise((resolve, reject) => { const reader = new FileReader(); reader.onload = () => resolve(reader.result); reader.onerror = () => reject(new Error("Não foi possível ler a imagem.")); reader.readAsDataURL(blob); });
      const image = document.createElement("img");
      image.src = dataUrl; image.alt = file.name; image.style.maxWidth = "100%";
      editorBody.focus();
      const selection = window.getSelection();
      if (savedRange) { selection.removeAllRanges(); selection.addRange(savedRange); }
      if (selection.rangeCount && editorBody.contains(selection.anchorNode)) {
        const range = selection.getRangeAt(0); range.deleteContents(); range.insertNode(image); range.setStartAfter(image); range.collapse(true);
        selection.removeAllRanges(); selection.addRange(range); savedRange = range.cloneRange();
      } else editorBody.append(image);
      root.querySelector("#image-status").textContent = `Imagem otimizada (${Math.round(blob.size / 1024)} KB); será incluída no PDF.`;
    } catch (error) { showToast(error.message); }
    finally { imageFile.value = ""; }
  });
  root.querySelector("#cancel-editor").addEventListener("click", () => { editor.hidden = true; showDetails(); });
  root.querySelector("#save-editor").addEventListener("click", async () => {
    const nome = root.querySelector("#editor-name").value.trim();
    const corpo = root.querySelector("#editor-body");
    if (!nome || (!corpo.innerText.trim() && !corpo.querySelector("img"))) return showToast("Informe um título e escreva o documento.");
    const body = { nome, conteudo_html: corpo.innerHTML };
    try {
      const result = editorialId
        ? await api(`/documentos-editoriais/${editorialId}`, jsonOptions("PUT", body))
        : await api(`/processos/${processId}/documentos-editoriais`, jsonOptions("POST", body));
      showToast(result.mensagem);
      ctx.navigate("processo", { id: processId });
    } catch (error) { showToast(error.message); }
  });

  renderDocs();
  showDetails();
}
