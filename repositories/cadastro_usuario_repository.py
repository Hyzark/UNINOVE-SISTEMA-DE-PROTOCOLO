import sqlite3
from database import create_connection

def create_cadastro_func(cadastro, hashed_password):
    conn = create_connection()
    cursor = conn.cursor()

    try: 
        cursor.execute("INSERT INTO usuarios (nome, email, senha, cargo, nivel_acesso, setor_id, ativo) VALUES (?, ?, ?, ?, 1, ?, 1)",
                       (cadastro.nome, cadastro.email, hashed_password, cadastro.cargo, cadastro.setor_id))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        raise 
        
    finally:
        conn.close()