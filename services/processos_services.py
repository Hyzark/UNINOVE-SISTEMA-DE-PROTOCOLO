import sqlite3
from repositories.processos_repository import criar_processo


class ErroAoCriarProcesso(Exception):
    pass


def cadastrar_processo(assunto, descricao, mesa_id, setor_id, user_id):
    try:
        return criar_processo(assunto, descricao, mesa_id, setor_id, user_id)
    except sqlite3.IntegrityError as exc:
        raise ErroAoCriarProcesso("Não foi possível cadastrar o processo.") from exc
