from database import create_connection
import sqlite3


def get_usuario_setor_by_id(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT setor_id FROM usuarios WHERE id = ?", (user_id,))
        usuario = cursor.fetchone()
        return usuario
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        raise
    finally:
        conn.close()

def create_cadastro_mesa(cadastro, setor_id):
    conn = create_connection()
    cursor = conn.cursor()

    try: 
        cursor.execute("INSERT INTO mesas (nome, setor_id) VALUES (?,?)",
                       (cadastro, setor_id))
        conn.commit()
        print("Mesa criada com sucesso!")
    except sqlite3.IntegrityError:
        conn.rollback()
        print("Erro ao criar a Mesa!")
        raise 
        
    finally:
        conn.close()

        