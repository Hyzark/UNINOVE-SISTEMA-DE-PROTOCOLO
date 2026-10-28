from pathlib import Path
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ConfigDict

from config import TIPO_FUNCIONARIO, TIPO_GERENTE
from repositories.login_repository import get_usuario_by_id
from repositories.processos_repository import (
    listar_mesas_usuario, obter_mesa_do_usuario,
    listar_processos_da_mesa, obter_processo, obter_documento
)
from services.processos_services import cadastrar_processo, ErroAoCriarProcesso
from services.documentos_services import salvar_documento, ErroDocumento
from services.documentos_editoriais_services import (
    salvar_documento_editorial, ErroDocumentoEditorial
)
from repositories.processos_repository import (
    obter_documento_editorial,
)
from services.security.auth_services import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


def require_operador(request: Request):
    user_id = get_current_user(request)
    usuario = get_usuario_by_id(user_id)
    if usuario is None or usuario[3] not in (TIPO_FUNCIONARIO, TIPO_GERENTE):
        raise HTTPException(status_code=403, detail="Acesso permitido somente a funcionários e gerentes.")
    return user_id


class SelecaoMesa(BaseModel):
    mesa_id: int = Field(gt=0)


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
             "criado_em": p[4], "criado_por": p[5]} for p in processos]


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
                                   "atualizado_em": d[3]} for d in documentos_editoriais]
    }


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
async def anexar_documento(processo_id: int, arquivo: UploadFile = File(...),
                           user_id: int = Depends(require_operador)):
    if obter_processo(user_id, processo_id) is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado no seu setor.")
    try:
        documento = await salvar_documento(processo_id, arquivo, user_id)
    except ErroDocumento as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        await arquivo.close()
    return {"mensagem": "Documento anexado com sucesso!", "documento": documento}


@router.get("/documentos/{documento_id}/download")
def baixar_documento(documento_id: int, user_id: int = Depends(require_operador)):
    documento = obter_documento(user_id, documento_id)
    if documento is None:
        raise HTTPException(status_code=404, detail="Documento não encontrado no seu setor.")
    caminho = Path(documento[2])
    if not caminho.is_file():
        raise HTTPException(status_code=404, detail="O arquivo não está disponível no servidor.")
    return FileResponse(caminho, filename=documento[1], media_type=documento[3] or "application/octet-stream")
