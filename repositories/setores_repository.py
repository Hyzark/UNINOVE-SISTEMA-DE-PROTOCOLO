from database import create_connection
import sqlite3

def listar_setores_ativos():
    conn = create_connection()
    try:
        return conn.execute("SELECT id, nome FROM setores WHERE ativo = 1 ORDER BY nome").fetchall()
    finally:
        conn.close()

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
