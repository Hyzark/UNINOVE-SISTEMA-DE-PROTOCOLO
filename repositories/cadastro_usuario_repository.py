import sqlite3
from database import create_connection
from repositories.auditoria_repository import registrar_evento_cadastro

def create_cadastro_func(cadastro, hashed_password, admin_id=None):
    conn = create_connection()
    cursor = conn.cursor()

    try: 
        cursor.execute("INSERT INTO usuarios (nome, email, senha, cargo, nivel_acesso, setor_id, ativo) VALUES (?, ?, ?, ?, ?, ?, 1)",
                       (cadastro.nome, cadastro.email, hashed_password, cadastro.cargo, cadastro.nivel_acesso, cadastro.setor_id))
        usuario_id = cursor.lastrowid
        if admin_id is not None:
            setor = cursor.execute("SELECT nome FROM setores WHERE id = ?", (cadastro.setor_id,)).fetchone()
            nivel = "Gerente" if cadastro.nivel_acesso == 3 else "Funcionário"
            setor_nome = setor[0] if setor else str(cadastro.setor_id)
            registrar_evento_cadastro(
                conn, admin_id, "Usuário cadastrado",
                f"{nivel} '{cadastro.nome}' ({cadastro.email}) cadastrado no setor '{setor_nome}'."
            )
        conn.commit()
        return usuario_id
    except sqlite3.IntegrityError:
        conn.rollback()
        raise 
        
    finally:
        conn.close()
