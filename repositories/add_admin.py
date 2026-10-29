"""Cria o primeiro setor e administrador com os dados informados no terminal."""

import sqlite3
from getpass import getpass

from database import create_connection
from services.security.password import hash_password


def criar_setor_e_administrador(setor_nome, setor_descricao, nome, email, senha, cargo):
    conn = create_connection()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO setores (nome, descricao) VALUES (?, ?)",
            (setor_nome, setor_descricao)
        )
        setor_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO usuarios "
            "(nome, email, senha, cargo, nivel_acesso, setor_id, ativo) "
            "VALUES (?, ?, ?, ?, 2, ?, 1)",
            (nome, email, hash_password(senha), cargo, setor_id)
        )
        conn.commit()
        return setor_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _solicitar_texto(rotulo):
    while True:
        valor = input(f"{rotulo}: ").strip()
        if valor:
            return valor
        print("Este campo é obrigatório.")


def main():
    print("Cadastro inicial do sistema. Nenhum dado padrão será usado.\n")
    setor_nome = _solicitar_texto("Nome do setor do administrador")
    setor_descricao = input("Descrição do setor (opcional): ").strip()
    nome = _solicitar_texto("Nome do administrador")
    while True:
        email = _solicitar_texto("E-mail administrativo (@admin.sp.gov.br)").lower()
        if email.count("@") == 1 and email.endswith("@admin.sp.gov.br"):
            break
        print("Informe um e-mail terminado em @admin.sp.gov.br.")
    cargo = _solicitar_texto("Cargo")
    while True:
        senha = getpass("Senha: ")
        confirmacao = getpass("Confirme a senha: ")
        if senha and senha == confirmacao:
            break
        print("As senhas devem ser iguais e não podem ficar vazias.")

    try:
        criar_setor_e_administrador(setor_nome, setor_descricao, nome, email, senha, cargo)
    except sqlite3.IntegrityError as error:
        raise SystemExit("Não foi possível criar o cadastro. Verifique se o e-mail ou setor já existe.") from error
    print("Setor e administrador cadastrados. Você já pode entrar no sistema.")


if __name__ == "__main__":
    main()
