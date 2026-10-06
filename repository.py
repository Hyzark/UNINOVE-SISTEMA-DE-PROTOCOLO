import sqlite3

connection = sqlite3.connect('banco.db')
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()


# ─────────────────────────────────────────────────────────────
# CRIAÇÃO DAS TABELAS
# ─────────────────────────────────────────────────────────────

# Tabela: setores
cursor.execute("""
    CREATE TABLE IF NOT EXISTS setores (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        nome        TEXT    NOT NULL,
        descricao   TEXT,
        ativo       INTEGER NOT NULL DEFAULT 1
    )
""")

# Tabela: mesas
# Um setor pode ter uma ou mais mesas
cursor.execute("""
    CREATE TABLE IF NOT EXISTS mesas (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        nome      TEXT    NOT NULL,
        setor_id  INTEGER NOT NULL,
        ativa     INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (setor_id) REFERENCES setores(id)
    )
""")

# Tabela: usuarios
cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        nome          TEXT    NOT NULL,
        email         TEXT    NOT NULL UNIQUE,
        senha         TEXT    NOT NULL,
        cargo         TEXT,
        nivel_acesso  INTEGER NOT NULL DEFAULT 1,
        setor_id      INTEGER NOT NULL,
        ativo         INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (setor_id) REFERENCES setores(id)
    )
""")

# Tabela: processos
cursor.execute("""
    CREATE TABLE IF NOT EXISTS processos (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        numero               TEXT    NOT NULL UNIQUE,
        assunto              TEXT    NOT NULL,
        descricao            TEXT,
        situacao             TEXT    NOT NULL DEFAULT 'Em análise',
        setor_responsavel_id INTEGER NOT NULL,
        responsavel_id       INTEGER,
        mesa_atual_id        INTEGER,
        criado_por_id        INTEGER NOT NULL,
        criado_em            TEXT    NOT NULL DEFAULT (datetime('now')),
        atualizado_em        TEXT    NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (setor_responsavel_id) REFERENCES setores(id),
        FOREIGN KEY (responsavel_id)       REFERENCES usuarios(id),
        FOREIGN KEY (mesa_atual_id)        REFERENCES mesas(id),
        FOREIGN KEY (criado_por_id)        REFERENCES usuarios(id)
    )
""")

# Tabela: documentos
cursor.execute("""
    CREATE TABLE IF NOT EXISTS documentos (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        processo_id     INTEGER NOT NULL,
        nome            TEXT    NOT NULL,
        caminho_arquivo TEXT    NOT NULL,
        tipo            TEXT,
        tamanho_bytes   INTEGER,
        enviado_por_id  INTEGER NOT NULL,
        criado_em       TEXT    NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (processo_id)    REFERENCES processos(id),
        FOREIGN KEY (enviado_por_id) REFERENCES usuarios(id)
    )
""")

# Tabela: tramitacoes
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tramitacoes (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        processo_id     INTEGER NOT NULL,
        mesa_origem_id  INTEGER,
        mesa_destino_id INTEGER NOT NULL,
        usuario_id      INTEGER NOT NULL,
        observacao      TEXT,
        criado_em       TEXT    NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (processo_id)     REFERENCES processos(id),
        FOREIGN KEY (mesa_origem_id)  REFERENCES mesas(id),
        FOREIGN KEY (mesa_destino_id) REFERENCES mesas(id),
        FOREIGN KEY (usuario_id)      REFERENCES usuarios(id)
    )
""")

# Tabela: historico
cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        processo_id INTEGER NOT NULL,
        usuario_id  INTEGER NOT NULL,
        acao        TEXT    NOT NULL,
        descricao   TEXT,
        criado_em   TEXT    NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (processo_id) REFERENCES processos(id),
        FOREIGN KEY (usuario_id)  REFERENCES usuarios(id)
    )
""")

# Tabela: comentarios
# tipo: 'publico' | 'privado' | 'comentario'
cursor.execute("""
    CREATE TABLE IF NOT EXISTS comentarios (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        processo_id INTEGER NOT NULL,
        usuario_id  INTEGER NOT NULL,
        conteudo    TEXT    NOT NULL,
        tipo        TEXT    NOT NULL DEFAULT 'publico',
        criado_em   TEXT    NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (processo_id) REFERENCES processos(id),
        FOREIGN KEY (usuario_id)  REFERENCES usuarios(id)
    )
""")

# Tabela: marcadores
cursor.execute("""
    CREATE TABLE IF NOT EXISTS marcadores (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT    NOT NULL UNIQUE,
        cor  TEXT    NOT NULL DEFAULT '#888888'
    )
""")

# Tabela: processo_marcadores (N:M entre processos e marcadores)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS processo_marcadores (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        processo_id INTEGER NOT NULL,
        marcador_id INTEGER NOT NULL,
        UNIQUE (processo_id, marcador_id),
        FOREIGN KEY (processo_id) REFERENCES processos(id),
        FOREIGN KEY (marcador_id) REFERENCES marcadores(id)
    )
""")

# Tabela: assinaturas
# tipo:   'ciencia' | 'aprovacao' | 'autorizacao' | 'despacho'
# status: 'pendente' | 'assinado' | 'recusado'
cursor.execute("""
    CREATE TABLE IF NOT EXISTS assinaturas (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        processo_id     INTEGER NOT NULL,
        documento_id    INTEGER,
        solicitante_id  INTEGER NOT NULL,
        assinante_id    INTEGER NOT NULL,
        tipo            TEXT    NOT NULL DEFAULT 'ciencia',
        status          TEXT    NOT NULL DEFAULT 'pendente',
        observacao      TEXT,
        criado_em       TEXT    NOT NULL DEFAULT (datetime('now')),
        assinado_em     TEXT,
        FOREIGN KEY (processo_id)    REFERENCES processos(id),
        FOREIGN KEY (documento_id)   REFERENCES documentos(id),
        FOREIGN KEY (solicitante_id) REFERENCES usuarios(id),
        FOREIGN KEY (assinante_id)   REFERENCES usuarios(id)
    )
""")

# Tabela: sobrestamentos
cursor.execute("""
    CREATE TABLE IF NOT EXISTS sobrestamentos (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        processo_id     INTEGER NOT NULL,
        motivo          TEXT    NOT NULL,
        usuario_id      INTEGER NOT NULL,
        criado_em       TEXT    NOT NULL DEFAULT (datetime('now')),
        retirado_em     TEXT,
        retirado_por_id INTEGER,
        FOREIGN KEY (processo_id)     REFERENCES processos(id),
        FOREIGN KEY (usuario_id)      REFERENCES usuarios(id),
        FOREIGN KEY (retirado_por_id) REFERENCES usuarios(id)
    )
""")

# Tabela: disponibilidade
# Controla quais setores podem acessar cada processo
cursor.execute("""
    CREATE TABLE IF NOT EXISTS disponibilidade (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        processo_id   INTEGER NOT NULL,
        setor_id      INTEGER NOT NULL,
        criado_por_id INTEGER NOT NULL,
        criado_em     TEXT    NOT NULL DEFAULT (datetime('now')),
        UNIQUE (processo_id, setor_id),
        FOREIGN KEY (processo_id)   REFERENCES processos(id),
        FOREIGN KEY (setor_id)      REFERENCES setores(id),
        FOREIGN KEY (criado_por_id) REFERENCES usuarios(id)
    )
""")

# Tabela: processos_relacionados
# Auto-relacionamento de processos
cursor.execute("""
    CREATE TABLE IF NOT EXISTS processos_relacionados (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        processo_id      INTEGER NOT NULL,
        processo_rel_id  INTEGER NOT NULL,
        tipo_relacao     TEXT    NOT NULL DEFAULT 'relacionado',
        criado_por_id    INTEGER NOT NULL,
        criado_em        TEXT    NOT NULL DEFAULT (datetime('now')),
        UNIQUE (processo_id, processo_rel_id),
        FOREIGN KEY (processo_id)     REFERENCES processos(id),
        FOREIGN KEY (processo_rel_id) REFERENCES processos(id),
        FOREIGN KEY (criado_por_id)   REFERENCES usuarios(id)
    )
""")

# Tabela: solicitacoes_alteracao
# Fluxo hierárquico: colaborador solicita, supervisor aprova/recusa
# tipo_acao: 'alteracao' | 'exclusao'
# status:    'pendente' | 'aprovado' | 'recusado'
cursor.execute("""
    CREATE TABLE IF NOT EXISTS solicitacoes_alteracao (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        processo_id      INTEGER NOT NULL,
        solicitante_id   INTEGER NOT NULL,
        aprovador_id     INTEGER,
        tipo_acao        TEXT    NOT NULL,
        status           TEXT    NOT NULL DEFAULT 'pendente',
        justificativa    TEXT    NOT NULL,
        resposta         TEXT,
        criado_em        TEXT    NOT NULL DEFAULT (datetime('now')),
        respondido_em    TEXT,
        FOREIGN KEY (processo_id)    REFERENCES processos(id),
        FOREIGN KEY (solicitante_id) REFERENCES usuarios(id),
        FOREIGN KEY (aprovador_id)   REFERENCES usuarios(id)
    )
""")


connection.commit()


# ─────────────────────────────────────────────────────────────
# VALIDAÇÕES
# ─────────────────────────────────────────────────────────────

print("Tabelas criadas:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
for (tabela,) in cursor.fetchall():
    print(f"  - {tabela}")

connection.close()


# ─────────────────────────────────────────────────────────────
# DROPS (comentados — descomente para resetar o banco)
# ─────────────────────────────────────────────────────────────

# cursor.execute("DROP TABLE IF EXISTS solicitacoes_alteracao")
# cursor.execute("DROP TABLE IF EXISTS processos_relacionados")
# cursor.execute("DROP TABLE IF EXISTS disponibilidade")
# cursor.execute("DROP TABLE IF EXISTS sobrestamentos")
# cursor.execute("DROP TABLE IF EXISTS assinaturas")
# cursor.execute("DROP TABLE IF EXISTS processo_marcadores")
# cursor.execute("DROP TABLE IF EXISTS marcadores")
# cursor.execute("DROP TABLE IF EXISTS comentarios")
# cursor.execute("DROP TABLE IF EXISTS historico")
# cursor.execute("DROP TABLE IF EXISTS tramitacoes")
# cursor.execute("DROP TABLE IF EXISTS documentos")
# cursor.execute("DROP TABLE IF EXISTS processos")
# cursor.execute("DROP TABLE IF EXISTS usuarios")
# cursor.execute("DROP TABLE IF EXISTS mesas")
# cursor.execute("DROP TABLE IF EXISTS setores")
# connection.commit()