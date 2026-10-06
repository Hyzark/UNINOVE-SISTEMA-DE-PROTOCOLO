from database import create_connection

def get_usuario_by_email(email):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute(
    "SELECT * FROM usuarios WHERE Email = ?",
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