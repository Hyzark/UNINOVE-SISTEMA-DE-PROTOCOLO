from database import create_connection
import sqlite3

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