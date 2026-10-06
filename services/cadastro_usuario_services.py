import sqlite3
from repositories.cadastro_usuario_repository import create_cadastro_func 
from services.security.password import hash_password

class EmailJaExisteException(Exception):
    pass

def cadastrar_funcionario(cadastro):
    try:
        hashed_password = hash_password(cadastro.senha)
        create_cadastro_func(cadastro, hashed_password)
    except sqlite3.IntegrityError:
        raise EmailJaExisteException("O email já está em uso.")
