import sqlite3
from pathlib import Path
from uuid import uuid4

from repositories.processos_repository import criar_documento


PASTA_DOCUMENTOS = Path(__file__).resolve().parent.parent / "uploads" / "documentos"
TAMANHO_MAXIMO = 20 * 1024 * 1024


class ErroDocumento(Exception):
    pass


async def salvar_documento(processo_id, arquivo, user_id):
    nome_original = (arquivo.filename or "documento").replace("\\", "/").split("/")[-1].strip()
    if not nome_original:
        nome_original = "documento"
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
            processo_id, nome_original, str(caminho), arquivo.content_type,
            len(conteudo), user_id
        )
        return {"id": documento_id, "nome": nome_original, "tipo": arquivo.content_type,
                "tamanho_bytes": len(conteudo)}
    except sqlite3.IntegrityError as exc:
        caminho.unlink(missing_ok=True)
        raise ErroDocumento("Não foi possível registrar o documento.") from exc
    except Exception:
        caminho.unlink(missing_ok=True)
        raise
