from database import create_connection


ACOES_CADASTRO = {
    "setores": "Setor criado",
    "usuarios": "Usuário cadastrado",
}


def _garantir_historico_cadastros(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS historico ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "usuario_id INTEGER NOT NULL, acao TEXT NOT NULL, descricao TEXT, "
        "criado_em TEXT NOT NULL DEFAULT (datetime('now')), "
        "FOREIGN KEY (usuario_id) REFERENCES usuarios(id))"
    )
    colunas = {coluna[1] for coluna in conn.execute("PRAGMA table_info(historico)").fetchall()}
    if "processo_id" not in colunas:
        conn.execute("ALTER TABLE historico ADD COLUMN processo_id INTEGER REFERENCES processos(id)")


def registrar_evento_cadastro(conn, admin_id, acao, descricao):
    _garantir_historico_cadastros(conn)
    conn.execute(
        "INSERT INTO historico (processo_id, usuario_id, acao, descricao) VALUES (NULL, ?, ?, ?)",
        (admin_id, acao, descricao)
    )


def listar_historico_cadastros(tipo):
    acao = ACOES_CADASTRO[tipo]
    conn = create_connection()
    try:
        _garantir_historico_cadastros(conn)
        conn.commit()
        return conn.execute(
            "SELECT h.id, h.acao, h.descricao, h.criado_em, u.nome "
            "FROM historico h JOIN usuarios u ON u.id = h.usuario_id "
            "WHERE h.processo_id IS NULL AND h.acao = ? "
            "ORDER BY h.criado_em DESC, h.id DESC",
            (acao,)
        ).fetchall()
    finally:
        conn.close()
