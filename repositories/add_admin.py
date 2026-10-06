import sqlite3
from database import create_connection
from pydantic import BaseModel
from services.security.password import hash_password


class Setoradmin(BaseModel):
    nome: str
    descricao: str

def create_cadastro_setor(cadastro):
    conn = create_connection()
    cursor = conn.cursor()

    try: 
        cursor.execute("INSERT INTO setores (nome, descricao) VALUES (?,?)",
                       (cadastro.nome, cadastro.descricao))
        conn.commit()
        print("Setor criado com sucesso!")
    except sqlite3.IntegrityError:
        conn.rollback()
        print("Erro ao criar o Setor!")
        raise 
        
    finally:
        conn.close()

cadastro_setor = Setoradmin(
    nome="Diretoria de infraestrutura e Sistemas",
    descricao="Garantir a estabilidade, a segurança e a continuidade das operações digitais da empresa, gerenciando os recursos tecnológicos e o ciclo de vida dos acessos corporativos"
)

class Admin(BaseModel):
    nome: str
    email: str
    senha: str
    cargo: str

def create_cadastro_admin(cadastro, hashed_password):
    conn = create_connection()

    cursor = conn.cursor()

    try: 
        cursor.execute("INSERT INTO usuarios (nome, email, senha, cargo, nivel_acesso, setor_id) VALUES (?, ?, ?, ?, 2, 1)",
                       (cadastro.nome, cadastro.email, hashed_password, cadastro.cargo))
        conn.commit()
        print("Administrador criado com sucesso!")
    except sqlite3.IntegrityError:
        conn.rollback()
        print("Erro ao criar administrador!")
        raise 
        
    finally:
        conn.close()

cadastro = Admin(
    nome="Marcus Vinicius",
    email="marcusadm@admin.com",
    senha="12345",
    cargo="Diretor"
)

hashed_password = hash_password(cadastro.senha)

create_cadastro_admin(cadastro, hashed_password)