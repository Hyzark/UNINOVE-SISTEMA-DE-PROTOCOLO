"""Limpa os dados de banco.db sem remover a estrutura das tabelas.

Execute este script somente quando quiser começar com o banco vazio:
    python repository2.py
"""

from pathlib import Path
import sqlite3


DB_PATH = Path(__file__).resolve().with_name("banco.db")


def limpar_banco(caminho=DB_PATH):
    conn = sqlite3.connect(caminho)
    try:
        # A exclusão é feita em ordem livre, mantendo a estrutura e as relações.
        conn.execute("PRAGMA foreign_keys = OFF")
        tabelas = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        conn.execute("BEGIN")
        for tabela in tabelas:
            identificador = tabela.replace('"', '""')
            conn.execute(f'DELETE FROM "{identificador}"')
        if conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'sqlite_sequence'"
        ).fetchone():
            conn.execute("DELETE FROM sqlite_sequence")
        conn.commit()
        return tabelas
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    removidas = limpar_banco()
    print(f"Dados removidos de {len(removidas)} tabelas em {DB_PATH}.")
    print("As tabelas e o esquema foram mantidos; nenhum administrador foi recriado.")
