import sqlite3
from pathlib import Path
from uuid import uuid4

from repositories.processos_repository import criar_documento, atualizar_documento as persistir_atualizacao_documento


PASTA_DOCUMENTOS = Path(__file__).resolve().parent.parent / "uploads" / "documentos"
TAMANHO_MAXIMO = 20 * 1024 * 1024


class ErroDocumento(Exception):
    pass


def _nome_arquivo(arquivo):
    nome = (arquivo.filename or "documento").replace("\\", "/").split("/")[-1].strip()
    return nome or "documento"


def _validar_titulo(titulo):
    titulo = (titulo or "").strip()
    if not titulo or len(titulo) > 200:
        raise ErroDocumento("Informe um título de até 200 caracteres.")
    return titulo


async def salvar_documento(processo_id, arquivo, user_id, titulo):
    _validar_titulo(titulo)
    nome_original = _nome_arquivo(arquivo)
    conteudo = await arquivo.read(TAMANHO_MAXIMO + 1)
    if len(conteudo) > TAMANHO_MAXIMO:
        raise ErroDocumento("O arquivo excede o limite de 20 MB.")

    extensao = Path(nome_original).suffix[:20]
    nome_armazenado = f"{uuid4().hex}{extensao}"
    PASTA_DOCUMENTOS.mkdir(parents=True, exist_ok=True)
    caminho = PASTA_DOCUMENTOS / nome_armazenado
    caminho.write_bytes(conteudo)
    try:
        documento_id = criar_documento(
            processo_id, titulo.strip(), str(caminho), arquivo.content_type,
            len(conteudo), user_id
        )
        return {"id": documento_id, "nome": titulo.strip(), "tipo": arquivo.content_type,
                "tamanho_bytes": len(conteudo)}
    except sqlite3.IntegrityError as exc:
        caminho.unlink(missing_ok=True)
        raise ErroDocumento("Não foi possível registrar o documento.") from exc
    except Exception:
        caminho.unlink(missing_ok=True)
        raise


async def atualizar_documento(documento_existente, titulo, arquivo, user_id):
    titulo = _validar_titulo(titulo)
    documento_id, _nome_atual, caminho_atual, tipo_atual, _tamanho_atual, _criado_em, _autor, processo_id = documento_existente
    caminho_novo = caminho_atual
    conteudo = None
    tipo_novo = tipo_atual
    if arquivo and arquivo.filename:
        nome_original = _nome_arquivo(arquivo)
        conteudo = await arquivo.read(TAMANHO_MAXIMO + 1)
        if len(conteudo) > TAMANHO_MAXIMO:
            raise ErroDocumento("O arquivo excede o limite de 20 MB.")
        extensao = Path(nome_original).suffix[:20]
        PASTA_DOCUMENTOS.mkdir(parents=True, exist_ok=True)
        caminho_novo = PASTA_DOCUMENTOS / f"{uuid4().hex}{extensao}"
        caminho_novo.write_bytes(conteudo)
        tipo_novo = arquivo.content_type or "application/octet-stream"
    persistido = False
    try:
        persistir_atualizacao_documento(
            documento_id, processo_id, titulo, str(caminho_novo),
            tipo_novo, len(conteudo) if conteudo is not None else documento_existente[4], user_id
        )
        persistido = True
        if conteudo is not None and caminho_atual != str(caminho_novo):
            antigo = Path(caminho_atual)
            if antigo.parent.resolve() == PASTA_DOCUMENTOS.resolve():
                try:
                    antigo.unlink(missing_ok=True)
                except OSError:
                    pass
        return {"id": documento_id, "nome": titulo, "tipo": tipo_novo,
                "tamanho_bytes": len(conteudo) if conteudo is not None else documento_existente[4]}
    except Exception:
        if conteudo is not None and not persistido:
            Path(caminho_novo).unlink(missing_ok=True)
        raise
