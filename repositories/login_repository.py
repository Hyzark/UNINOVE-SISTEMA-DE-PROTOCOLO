from database import create_connection

def get_usuario_by_email(email):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute(
    "SELECT id, nome, email, senha FROM usuarios WHERE Email = ? AND ativo = 1",
    (email,)
    )
    usuario = cursor.fetchone()
    
    conn.close()
    return usuario 

def get_usuario_by_id(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute(
    "SELECT id, nome, email, nivel_acesso FROM usuarios WHERE id = ?",
    (user_id,)
    )
    usuario = cursor.fetchone()
    
    conn.close()
    return usuario 

def get_painel_usuario(user_id):
    conn = create_connection()
    try:
        usuario = conn.execute(
            "SELECT u.id, u.nome, u.email, u.nivel_acesso, s.id, s.nome "
            "FROM usuarios u LEFT JOIN setores s ON s.id = u.setor_id "
            "WHERE u.id = ? AND u.ativo = 1", (user_id,)
        ).fetchone()
        if usuario is None:
            return None
        mesas = []
        if usuario[3] == 1 and usuario[4] is not None:
            mesas = conn.execute(
                "SELECT nome FROM mesas WHERE setor_id = ? AND ativa = 1 ORDER BY nome",
                (usuario[4],)
            ).fetchall()
        return usuario, [mesa[0] for mesa in mesas]
    finally:
        conn.close()
