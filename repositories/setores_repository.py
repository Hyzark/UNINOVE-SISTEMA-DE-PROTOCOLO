from database import create_connection
import sqlite3
from repositories.auditoria_repository import registrar_evento_cadastro

def listar_setores_ativos():
    conn = create_connection()
    try:
        return conn.execute("SELECT id, nome FROM setores WHERE ativo = 1 ORDER BY nome").fetchall()
    finally:
        conn.close()

def create_cadastro_setor(cadastro, admin_id=None):
    conn = create_connection()
    cursor = conn.cursor()

    try: 
        cursor.execute("INSERT INTO setores (nome, descricao) VALUES (?,?)",
                       (cadastro.nome, cadastro.descricao))
        setor_id = cursor.lastrowid
        if admin_id is not None:
            registrar_evento_cadastro(
                conn, admin_id, "Setor criado", f"Setor '{cadastro.nome}' criado."
            )
        conn.commit()
        return setor_id
    except sqlite3.IntegrityError:
        conn.rollback()
        print("Erro ao criar o Setor!")
        raise 
        
    finally:
        conn.close()
