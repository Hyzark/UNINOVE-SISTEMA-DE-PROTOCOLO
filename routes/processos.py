from pathlib import Path
import logging
from typing import Literal
from zipfile import ZipFile, BadZipFile
from xml.etree import ElementTree
import csv
import mimetypes
import posixpath
from itertools import islice
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ConfigDict

from config import TIPO_ADMIN, TIPO_FUNCIONARIO, TIPO_GERENTE
from repositories.login_repository import get_usuario_by_id
from repositories.processos_repository import (
    listar_mesas_usuario, obter_mesa_do_usuario,
    listar_processos_da_mesa, buscar_processos_setor, obter_processo, obter_documento
)
from services.processos_services import cadastrar_processo, ErroAoCriarProcesso
from services.documentos_services import salvar_documento, atualizar_documento, ErroDocumento
from services.documentos_editoriais_services import (
    salvar_documento_editorial, ErroDocumentoEditorial
)
from repositories.processos_repository import (
    obter_documento_editorial,
)
from repositories.processos_repository import atualizar_situacao_processo
from services.security.auth_services import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


def _nome_com_extensao(titulo, extensao):
    titulo_path = Path(titulo)
    if not extensao or titulo_path.suffix.lower() == extensao.lower():
        return titulo
    return f"{titulo_path.stem if titulo_path.suffix else titulo}{extensao}"


def require_operador(request: Request):
    user_id = get_current_user(request)
    usuario = get_usuario_by_id(user_id)
    if usuario is None or usuario[3] not in (TIPO_FUNCIONARIO, TIPO_GERENTE, TIPO_ADMIN):
        raise HTTPException(status_code=403, detail="Acesso permitido somente a usuários do setor.")
    return user_id


class SelecaoMesa(BaseModel):
    mesa_id: int = Field(gt=0)


class AtualizacaoSituacao(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    situacao: Literal["Em análise", "Em andamento", "Aguardando solicitação"]


class Processo(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    assunto: str = Field(min_length=1, max_length=200)
    descricao: str = Field(min_length=1, max_length=5000)


class DocumentoEditorial(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    nome: str = Field(min_length=1, max_length=200)
    conteudo_html: str = Field(min_length=1, max_length=10 * 1024 * 1024)


@router.get("/minhas-mesas")
def minhas_mesas(user_id: int = Depends(require_operador)):
    return [{"id": mesa[0], "nome": mesa[1], "setor_id": mesa[2], "setor": mesa[3]}
            for mesa in listar_mesas_usuario(user_id)]


@router.post("/mesa-atual")
def selecionar_mesa(selecao: SelecaoMesa, request: Request, user_id: int = Depends(require_operador)):
    mesa = obter_mesa_do_usuario(user_id, selecao.mesa_id)
    if mesa is None:
        raise HTTPException(status_code=403, detail="A mesa não pertence ao seu setor ou está inativa.")
    request.session["mesa_id"] = mesa[0]
    return {"id": mesa[0], "nome": mesa[1], "setor_id": mesa[2], "setor": mesa[3]}


@router.post("/processos")
def criar_processo_route(processo: Processo, request: Request, user_id: int = Depends(require_operador)):
    mesa_id = request.session.get("mesa_id")
    if mesa_id is None:
        raise HTTPException(status_code=400, detail="Selecione uma mesa antes de criar um processo.")
    mesa = obter_mesa_do_usuario(user_id, mesa_id)
    if mesa is None:
        request.session.pop("mesa_id", None)
        raise HTTPException(status_code=403, detail="A mesa selecionada não está mais disponível.")
    try:
        processo_id, numero = cadastrar_processo(
            processo.assunto, processo.descricao, mesa[0], mesa[2], user_id
        )
    except ErroAoCriarProcesso as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"mensagem": "Processo criado com sucesso!", "id": processo_id, "numero": numero}


@router.get("/mesas/{mesa_id}/processos")
def processos_da_mesa(mesa_id: int, request: Request, user_id: int = Depends(require_operador)):
    mesa = obter_mesa_do_usuario(user_id, mesa_id)
    if mesa is None:
        raise HTTPException(status_code=403, detail="A mesa não pertence ao seu setor ou está inativa.")
    request.session["mesa_id"] = mesa_id
    processos = listar_processos_da_mesa(user_id, mesa_id)
    return [{"id": p[0], "numero": p[1], "assunto": p[2], "situacao": p[3],
             "criado_em": p[4], "criado_por": p[5], "atualizado_em": p[6]} for p in processos]


@router.get("/processos/busca")
def buscar_processos(termo: str = Query(..., min_length=1, max_length=200),
                     user_id: int = Depends(require_operador)):
    termo = termo.strip()
    if not termo:
        raise HTTPException(status_code=422, detail="Digite um número ou assunto para pesquisar.")
    processos = buscar_processos_setor(user_id, termo)
    return [{"id": p[0], "numero": p[1], "assunto": p[2], "situacao": p[3],
             "atualizado_em": p[4], "mesa": p[5], "criado_por": p[6]} for p in processos]


@router.get("/processos/{processo_id}")
def detalhes_processo(processo_id: int, user_id: int = Depends(require_operador)):
    dados = obter_processo(user_id, processo_id)
    if dados is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado no seu setor.")
    p, eventos, documentos, documentos_editoriais = dados
    return {
        "id": p[0], "numero": p[1], "assunto": p[2], "descricao": p[3],
        "situacao": p[4], "criado_em": p[5], "atualizado_em": p[6],
        "criado_por_id": p[7], "criado_por": p[8], "setor": p[9],
        "mesa_id": p[10], "mesa": p[11],
        "historico": [{"acao": e[0], "descricao": e[1], "criado_em": e[2], "usuario": e[3]}
                      for e in eventos],
        "documentos": [{"id": d[0], "nome": d[1], "tipo": d[2], "tamanho_bytes": d[3],
                        "criado_em": d[4], "enviado_por": d[5]} for d in documentos],
        "documentos_editoriais": [{"id": d[0], "nome": d[1], "criado_em": d[2],
                                   "atualizado_em": d[3], "pdf_documento_id": d[4]} for d in documentos_editoriais]
    }


@router.patch("/processos/{processo_id}/situacao")
def atualizar_situacao(processo_id: int, atualizacao: AtualizacaoSituacao,
                        user_id: int = Depends(require_operador)):
    if not atualizar_situacao_processo(user_id, processo_id, atualizacao.situacao):
        raise HTTPException(status_code=404, detail="Processo não encontrado no seu setor.")
    return {"mensagem": "Situação do processo atualizada.", "situacao": atualizacao.situacao}


@router.get("/documentos-editoriais/{documento_id}")
def detalhes_documento_editorial(documento_id: int, user_id: int = Depends(require_operador)):
    documento = obter_documento_editorial(user_id, documento_id)
    if documento is None:
        raise HTTPException(status_code=404, detail="Documento não encontrado no seu setor.")
    return {"id": documento[0], "processo_id": documento[1], "nome": documento[2],
            "conteudo_html": documento[3]}


@router.post("/processos/{processo_id}/documentos-editoriais", status_code=201)
def criar_documento_editorial_route(processo_id: int, documento: DocumentoEditorial,
                                    user_id: int = Depends(require_operador)):
    if obter_processo(user_id, processo_id) is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado no seu setor.")
    try:
        resultado = salvar_documento_editorial(
            processo_id, None, documento.nome, documento.conteudo_html, user_id
        )
    except ErroDocumentoEditorial as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Erro ao criar documento editorial no processo %s", processo_id)
        raise HTTPException(status_code=500, detail="Erro interno ao salvar o documento. Consulte o log do servidor.") from exc
    return {"mensagem": "Documento salvo e convertido em PDF.", "documento": resultado}


@router.put("/documentos-editoriais/{documento_id}")
def atualizar_documento_editorial_route(documento_id: int, documento: DocumentoEditorial,
                                        user_id: int = Depends(require_operador)):
    existente = obter_documento_editorial(user_id, documento_id)
    if existente is None:
        raise HTTPException(status_code=404, detail="Documento não encontrado no seu setor.")
    try:
        resultado = salvar_documento_editorial(
            existente[1], documento_id, documento.nome, documento.conteudo_html, user_id
        )
    except ErroDocumentoEditorial as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Erro ao atualizar documento editorial %s", documento_id)
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar o documento. Consulte o log do servidor.") from exc
    return {"mensagem": "Documento atualizado e PDF substituído.", "documento": resultado}


@router.post("/processos/{processo_id}/documentos", status_code=201)
async def anexar_documento(processo_id: int, titulo: str = Form(..., min_length=1, max_length=200),
                           arquivo: UploadFile = File(...),
                           user_id: int = Depends(require_operador)):
    if obter_processo(user_id, processo_id) is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado no seu setor.")
    try:
        documento = await salvar_documento(processo_id, arquivo, user_id, titulo)
    except ErroDocumento as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        await arquivo.close()
    return {"mensagem": "Documento anexado com sucesso!", "documento": documento}


@router.put("/documentos/{documento_id}")
async def atualizar_anexo(documento_id: int, titulo: str = Form(..., min_length=1, max_length=200),
                          arquivo: UploadFile | None = File(None),
                          user_id: int = Depends(require_operador)):
    documento_existente = obter_documento(user_id, documento_id)
    if documento_existente is None:
        raise HTTPException(status_code=404, detail="Documento não encontrado no seu setor.")
    try:
        documento = await atualizar_documento(documento_existente, titulo, arquivo, user_id)
    except ErroDocumento as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        if arquivo:
            await arquivo.close()
    return {"mensagem": "Documento atualizado com sucesso.", "documento": documento}


@router.get("/documentos/{documento_id}/download")
def baixar_documento(documento_id: int, user_id: int = Depends(require_operador)):
    documento = obter_documento(user_id, documento_id)
    if documento is None:
        raise HTTPException(status_code=404, detail="Documento não encontrado no seu setor.")
    caminho = Path(documento[2])
    if not caminho.is_file():
        raise HTTPException(status_code=404, detail="O arquivo não está disponível no servidor.")
    nome_download = _nome_com_extensao(documento[1], caminho.suffix)
    return FileResponse(caminho, filename=nome_download, media_type=documento[3] or "application/octet-stream")


def _valor_celula(cell, shared_strings):
    value = cell.find("{*}v")
    if value is not None and value.text is not None:
        if cell.get("t") == "s":
            try:
                return shared_strings[int(value.text)]
            except (ValueError, IndexError):
                pass
        return value.text
    inline = cell.find("{*}is")
    if inline is not None:
        return "".join(node.text or "" for node in inline.iter() if node.tag.endswith("}t"))
    return ""


def _preview_xlsx(caminho):
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    with ZipFile(caminho) as workbook:
        shared = []
        if "xl/sharedStrings.xml" in workbook.namelist():
            root = ElementTree.fromstring(workbook.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in item.findall(".//m:t", ns)) for item in root.findall("m:si", ns)]
        book = ElementTree.fromstring(workbook.read("xl/workbook.xml"))
        sheets = book.findall("m:sheets/m:sheet", ns)
        if not sheets:
            return {"kind": "spreadsheet", "sheet": "Planilha", "rows": []}
        rels = ElementTree.fromstring(workbook.read("xl/_rels/workbook.xml.rels"))
        relation_map = {r.get("Id"): r.get("Target") for r in rels}
        target = relation_map.get(sheets[0].get(f"{{{ns['r']}}}id"), "worksheets/sheet1.xml")
        sheet_path = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join("xl", target))
        sheet = ElementTree.fromstring(workbook.read(sheet_path))
        rows = [[_valor_celula(cell, shared) for cell in row.findall("m:c", ns)[:20]]
                for row in sheet.findall(".//m:sheetData/m:row", ns)[:100]]
        return {"kind": "spreadsheet", "sheet": sheets[0].get("name", "Planilha"), "rows": rows,
                "message": "Prévia limitada às primeiras 100 linhas e 20 colunas da primeira aba."}


def _preview_zip(caminho):
    with ZipFile(caminho) as archive:
        items = [{"name": info.filename, "size": info.file_size, "compressed_size": info.compress_size}
                 for info in archive.infolist()[:300]]
        return {"kind": "archive", "entries": items,
                "message": f"Mostrando até 300 itens. Total no arquivo: {len(archive.infolist())}."}


def _preview_docx(caminho):
    with ZipFile(caminho) as archive:
        root = ElementTree.fromstring(archive.read("word/document.xml"))
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = ["".join(node.text or "" for node in paragraph.findall(".//w:t", ns))
                  for paragraph in root.findall(".//w:p", ns)]
    return {"kind": "text", "text": "\n".join(paragraphs[:1000]), "message": "Prévia do texto do documento."}


def _preview_pptx(caminho):
    with ZipFile(caminho) as archive:
        slides = sorted(name for name in archive.namelist()
                        if name.startswith("ppt/slides/slide") and name.endswith(".xml"))
        ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
        text = []
        for index, slide in enumerate(slides[:50], start=1):
            root = ElementTree.fromstring(archive.read(slide))
            lines = [node.text or "" for node in root.findall(".//a:t", ns)]
            text.append(f"Slide {index}\n" + "\n".join(lines))
    return {"kind": "text", "text": "\n\n".join(text), "message": "Prévia do texto das primeiras 50 páginas."}


def _preview_ods(caminho):
    ns = {"table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
          "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"}
    with ZipFile(caminho) as archive:
        root = ElementTree.fromstring(archive.read("content.xml"))
    sheets = root.findall(".//table:table", ns)
    if not sheets:
        return {"kind": "spreadsheet", "sheet": "Planilha", "rows": []}
    rows = []
    for row in sheets[0].findall("table:table-row", ns)[:100]:
        values = []
        for cell in row.findall("table:table-cell", ns):
            repeated = min(int(cell.get(f"{{{ns['table']}}}number-columns-repeated", "1")), 20 - len(values))
            text = " ".join("".join(node.itertext()) for node in cell.findall(".//text:p", ns))
            value = cell.get(f"{{{ns['table']}}}value") or cell.get(f"{{{ns['table']}}}date-value") or text
            values.extend([value] * max(0, repeated))
            if len(values) >= 20:
                break
        rows.append(values)
    return {"kind": "spreadsheet", "sheet": sheets[0].get(f"{{{ns['table']}}}name", "Planilha"),
            "rows": rows, "message": "Prévia limitada às primeiras 100 linhas e 20 colunas da primeira aba."}


@router.get("/documentos/{documento_id}/preview")
def visualizar_documento(documento_id: int, user_id: int = Depends(require_operador)):
    documento = obter_documento(user_id, documento_id)
    if documento is None:
        raise HTTPException(status_code=404, detail="Documento não encontrado no seu setor.")
    caminho = Path(documento[2])
    if not caminho.is_file():
        raise HTTPException(status_code=404, detail="O arquivo não está disponível no servidor.")
    extensao = caminho.suffix.lower()
    if extensao == ".pdf" or extensao in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
        media_type = "application/pdf" if extensao == ".pdf" else mimetypes.guess_type(caminho.name)[0]
        nome_preview = _nome_com_extensao(documento[1], extensao)
        return FileResponse(caminho, filename=nome_preview, media_type=media_type,
                            content_disposition_type="inline", headers={"X-Content-Type-Options": "nosniff"})
    try:
        if extensao == ".zip":
            preview = _preview_zip(caminho)
        elif extensao in {".xlsx", ".xlsm"}:
            preview = _preview_xlsx(caminho)
        elif extensao == ".docx":
            preview = _preview_docx(caminho)
        elif extensao == ".pptx":
            preview = _preview_pptx(caminho)
        elif extensao == ".ods":
            preview = _preview_ods(caminho)
        elif extensao == ".csv":
            with caminho.open("r", encoding="utf-8-sig", errors="replace", newline="") as arquivo:
                rows = list(islice(csv.reader(arquivo), 100))
            preview = {"kind": "spreadsheet", "sheet": "CSV", "rows": rows,
                       "message": "Prévia limitada às primeiras 100 linhas."}
        elif extensao in {".txt", ".log", ".json", ".xml", ".md"}:
            preview = {"kind": "text", "text": caminho.read_text(encoding="utf-8-sig", errors="replace")[:100000],
                       "message": "Prévia limitada a 100 mil caracteres."}
        else:
            preview = {"kind": "unsupported", "message": "Este formato não tem prévia disponível. Use o botão Baixar para abrir o arquivo no aplicativo adequado."}
    except (BadZipFile, KeyError, ElementTree.ParseError, OSError, ValueError, IndexError, csv.Error) as exc:
        logger.info("Falha ao gerar prévia do documento %s: %s", documento_id, exc)
        preview = {"kind": "unsupported", "message": "Não foi possível montar uma prévia deste arquivo. Baixe-o para abrir no aplicativo adequado."}
    return {"titulo": documento[1], "tipo": documento[3], "tamanho_bytes": documento[4], **preview}
