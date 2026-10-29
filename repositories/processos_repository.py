import sqlite3
import re
import unicodedata
from uuid import uuid4
from database import create_connection


def _garantir_tabela_historico(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS processo_historico ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "processo_id INTEGER NOT NULL, usuario_id INTEGER NOT NULL, "
        "acao TEXT NOT NULL, descricao TEXT, criado_em TEXT NOT NULL DEFAULT (datetime('now')), "
        "FOREIGN KEY (processo_id) REFERENCES processos(id), "
        "FOREIGN KEY (usuario_id) REFERENCES usuarios(id))"
    )
    colunas = {coluna[1] for coluna in conn.execute("PRAGMA table_info(historico)").fetchall()}
    if "processo_id" not in colunas:
        conn.execute("ALTER TABLE historico ADD COLUMN processo_id INTEGER REFERENCES processos(id)")
    conn.commit()


def listar_mesas_usuario(user_id):
    conn = create_connection()
    try:
        return conn.execute(
            "SELECT m.id, m.nome, s.id, s.nome "
            "FROM usuarios u JOIN setores s ON s.id = u.setor_id "
            "JOIN mesas m ON m.setor_id = s.id "
            "WHERE u.id = ? AND u.ativo = 1 AND s.ativo = 1 AND m.ativa = 1 "
            "ORDER BY m.nome", (user_id,)
        ).fetchall()
    finally:
        conn.close()


def obter_mesa_do_usuario(user_id, mesa_id):
    conn = create_connection()
    try:
        return conn.execute(
            "SELECT m.id, m.nome, s.id, s.nome "
            "FROM usuarios u JOIN setores s ON s.id = u.setor_id "
            "JOIN mesas m ON m.setor_id = s.id "
            "WHERE u.id = ? AND m.id = ? AND u.ativo = 1 AND s.ativo = 1 AND m.ativa = 1",
            (user_id, mesa_id)
        ).fetchone()
    finally:
        conn.close()


def criar_processo(assunto, descricao, mesa_id, setor_id, user_id):
    conn = create_connection()
    try:
        _garantir_tabela_historico(conn)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO processos (numero, assunto, descricao, setor_responsavel_id, "
            "responsavel_id, mesa_atual_id, criado_por_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (f"TEMP-{uuid4().hex}", assunto, descricao, setor_id, user_id, mesa_id, user_id)
        )
        processo_id = cursor.lastrowid
        numero = f"PROC-{processo_id:06d}"
        cursor.execute("UPDATE processos SET numero = ? WHERE id = ?", (numero, processo_id))
        mesa_nome = cursor.execute("SELECT nome FROM mesas WHERE id = ?", (mesa_id,)).fetchone()
        descricao_criacao = f"Processo {numero} criado na mesa '{mesa_nome[0]}'." if mesa_nome else f"Processo {numero} criado."
        cursor.execute(
            "INSERT INTO processo_historico (processo_id, usuario_id, acao, descricao) "
            "VALUES (?, ?, 'Criação', ?)",
            (processo_id, user_id, descricao_criacao)
        )
        conn.commit()
        return processo_id, numero
    except sqlite3.IntegrityError:
        conn.rollback()
        raise
    finally:
        conn.close()


def listar_processos_da_mesa(user_id, mesa_id):
    conn = create_connection()
    try:
        return conn.execute(
            "SELECT p.id, p.numero, p.assunto, p.situacao, p.criado_em, u.nome, p.atualizado_em "
            "FROM processos p JOIN usuarios u ON u.id = p.criado_por_id "
            "JOIN mesas m ON m.id = p.mesa_atual_id "
            "JOIN usuarios operador ON operador.id = ? "
            "WHERE m.id = ? AND m.setor_id = operador.setor_id "
            "AND m.ativa = 1 AND operador.ativo = 1 ORDER BY p.criado_em DESC, p.id DESC",
            (user_id, mesa_id)
        ).fetchall()
    finally:
        conn.close()


def buscar_processos_setor(user_id, termo):
    conn = create_connection()
    try:
        conn.create_function("normalizar_busca", 1, _normalizar_termo)
        return conn.execute(
            "SELECT p.id, p.numero, p.assunto, p.situacao, p.atualizado_em, m.nome, autor.nome "
            "FROM processos p "
            "JOIN usuarios operador ON operador.id = ? "
            "JOIN setores s ON s.id = p.setor_responsavel_id AND s.ativo = 1 "
            "LEFT JOIN mesas m ON m.id = p.mesa_atual_id "
            "JOIN usuarios autor ON autor.id = p.criado_por_id "
            "WHERE operador.ativo = 1 AND p.setor_responsavel_id = operador.setor_id "
            "AND (instr(normalizar_busca(p.numero), normalizar_busca(?)) > 0 "
            "OR instr(normalizar_busca(p.assunto), normalizar_busca(?)) > 0) "
            "ORDER BY p.atualizado_em DESC, p.id DESC",
            (user_id, termo, termo)
        ).fetchall()
    finally:
        conn.close()


def _normalizar_termo(valor):
    texto = unicodedata.normalize("NFD", str(valor or "")).casefold()
    return "".join(caractere for caractere in texto if unicodedata.category(caractere) != "Mn")


def obter_processo(user_id, processo_id):
    conn = create_connection()
    try:
        _garantir_tabela_historico(conn)
        processo = conn.execute(
            "SELECT p.id, p.numero, p.assunto, p.descricao, p.situacao, p.criado_em, "
            "p.atualizado_em, criador.id, criador.nome, s.nome, m.id, m.nome "
            "FROM processos p JOIN usuarios operador ON operador.id = ? "
            "JOIN usuarios criador ON criador.id = p.criado_por_id "
            "JOIN setores s ON s.id = p.setor_responsavel_id "
            "LEFT JOIN mesas m ON m.id = p.mesa_atual_id "
            "WHERE p.id = ? AND p.setor_responsavel_id = operador.setor_id "
            "AND operador.ativo = 1",
            (user_id, processo_id)
        ).fetchone()
        if processo is None:
            return None
        historico = conn.execute(
            "SELECT h.acao, h.descricao, h.criado_em, u.nome "
            "FROM processo_historico h JOIN usuarios u ON u.id = h.usuario_id "
            "WHERE h.processo_id = ? "
            "UNION ALL "
            "SELECT 'Tramitação', t.observacao, t.criado_em, u.nome "
            "FROM tramitacoes t JOIN usuarios u ON u.id = t.usuario_id "
            "WHERE t.processo_id = ? "
            "UNION ALL "
            "SELECT h.acao, h.descricao, h.criado_em, u.nome "
            "FROM historico h JOIN usuarios u ON u.id = h.usuario_id "
            "WHERE h.processo_id = ? "
            "ORDER BY 3 DESC",
            (processo_id, processo_id, processo_id)
        ).fetchall()
        nomes_mesas = dict(conn.execute("SELECT id, nome FROM mesas").fetchall())
        historico = [
            _normalizar_descricao_historico(evento, nomes_mesas)
            for evento in historico
        ]
        documentos = conn.execute(
            "SELECT d.id, d.nome, d.tipo, d.tamanho_bytes, d.criado_em, u.nome "
            "FROM documentos d JOIN usuarios u ON u.id = d.enviado_por_id "
            "WHERE d.processo_id = ? ORDER BY d.criado_em DESC, d.id DESC",
            (processo_id,)
        ).fetchall()
        _garantir_tabela_documentos_editoriais(conn)
        documentos_editoriais = conn.execute(
            "SELECT d.id, d.nome, d.criado_em, d.atualizado_em, COALESCE(d.pdf_documento_id, "
            "(SELECT doc.id FROM documentos doc WHERE doc.processo_id = d.processo_id "
            "AND doc.nome = d.nome || '.pdf' AND doc.tipo = 'application/pdf' "
            "ORDER BY doc.id DESC LIMIT 1)) "
            "FROM documentos_editoriais d "
            "WHERE d.processo_id = ? ORDER BY d.atualizado_em DESC, d.id DESC", (processo_id,)
        ).fetchall()
        return processo, historico, documentos, documentos_editoriais
    finally:
        conn.close()


def atualizar_situacao_processo(user_id, processo_id, situacao):
    conn = create_connection()
    try:
        _garantir_tabela_historico(conn)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT p.situacao, operador.nome FROM processos p "
            "JOIN usuarios operador ON operador.id = ? "
            "WHERE p.id = ? AND p.setor_responsavel_id = operador.setor_id "
            "AND operador.ativo = 1",
            (user_id, processo_id)
        )
        anterior = cursor.fetchone()
        if anterior is None:
            return False
        if anterior[0] == situacao:
            return True
        cursor.execute(
            "UPDATE processos SET situacao = ?, atualizado_em = datetime('now') WHERE id = ?",
            (situacao, processo_id)
        )
        cursor.execute(
            "INSERT INTO processo_historico (processo_id, usuario_id, acao, descricao) "
            "VALUES (?, ?, 'Situação atualizada', ?)",
            (processo_id, user_id,
             f"Status alterado de '{anterior[0]}' para '{situacao}' por {anterior[1]}.")
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _normalizar_descricao_historico(evento, nomes_mesas):
    acao, descricao, criado_em, usuario = evento
    texto = descricao or ""
    if acao == "Criação":
        match = re.search(r" criado na mesa (\d+)\.?$", texto)
        if match:
            nome_mesa = nomes_mesas.get(int(match.group(1)))
            texto = texto[:match.start()] + (f" criado na mesa '{nome_mesa}'." if nome_mesa else " criado.")
    elif acao in {"Documento digital criado", "Documento digital atualizado"}:
        match = re.match(r"'(.+)' salvo como PDF no anexo #\d+\.?$", texto)
        if match:
            texto = f"PDF do documento editorial '{match.group(1)}' gerado."
    return acao, texto, criado_em, usuario


def criar_documento(processo_id, nome, caminho, tipo, tamanho, user_id):
    conn = create_connection()
    try:
        _garantir_tabela_historico(conn)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO documentos (processo_id, nome, caminho_arquivo, tipo, tamanho_bytes, enviado_por_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (processo_id, nome, caminho, tipo, tamanho, user_id)
        )
        documento_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO historico (processo_id, usuario_id, acao, descricao) "
            "VALUES (?, ?, 'Documento anexado', ?)",
            (processo_id, user_id, f"Documento '{nome}' anexado.")
        )
        conn.commit()
        return documento_id
    except sqlite3.IntegrityError:
        conn.rollback()
        raise
    finally:
        conn.close()


def obter_documento(user_id, documento_id):
    conn = create_connection()
    try:
        return conn.execute(
            "SELECT d.id, d.nome, d.caminho_arquivo, d.tipo, d.tamanho_bytes, d.criado_em, u.nome, p.id "
            "FROM documentos d JOIN processos p ON p.id = d.processo_id "
            "JOIN usuarios operador ON operador.id = ? "
            "JOIN usuarios u ON u.id = d.enviado_por_id "
            "WHERE d.id = ? AND p.setor_responsavel_id = operador.setor_id AND operador.ativo = 1",
            (user_id, documento_id)
        ).fetchone()
    finally:
        conn.close()


def atualizar_documento(documento_id, processo_id, nome, caminho, tipo, tamanho, user_id):
    conn = create_connection()
    try:
        _garantir_tabela_historico(conn)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE documentos SET nome = ?, caminho_arquivo = ?, tipo = ?, tamanho_bytes = ? "
            "WHERE id = ? AND processo_id = ?",
            (nome, caminho, tipo, tamanho, documento_id, processo_id)
        )
        if cursor.rowcount != 1:
            raise LookupError("Documento não encontrado neste processo.")
        cursor.execute("UPDATE processos SET atualizado_em = datetime('now') WHERE id = ?", (processo_id,))
        cursor.execute(
            "INSERT INTO historico (processo_id, usuario_id, acao, descricao) VALUES (?, ?, ?, ?)",
            (processo_id, user_id, "Documento atualizado", f"Documento '{nome}' atualizado.")
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _garantir_tabela_documentos_editoriais(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS documentos_editoriais ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, processo_id INTEGER NOT NULL, "
        "nome TEXT NOT NULL, conteudo_html TEXT NOT NULL, criado_por_id INTEGER NOT NULL, "
        "atualizado_por_id INTEGER NOT NULL, criado_em TEXT NOT NULL DEFAULT (datetime('now')), "
        "atualizado_em TEXT NOT NULL DEFAULT (datetime('now')), "
        "FOREIGN KEY (processo_id) REFERENCES processos(id), "
        "FOREIGN KEY (criado_por_id) REFERENCES usuarios(id), "
        "FOREIGN KEY (atualizado_por_id) REFERENCES usuarios(id))"
    )
    colunas = {coluna[1] for coluna in conn.execute("PRAGMA table_info(documentos_editoriais)").fetchall()}
    if "pdf_documento_id" not in colunas:
        conn.execute("ALTER TABLE documentos_editoriais ADD COLUMN pdf_documento_id INTEGER REFERENCES documentos(id)")
    conn.commit()


def listar_documentos_editoriais(processo_id):
    conn = create_connection()
    try:
        _garantir_tabela_documentos_editoriais(conn)
        return conn.execute(
            "SELECT d.id, d.nome, d.criado_em, d.atualizado_em, COALESCE(d.pdf_documento_id, "
            "(SELECT doc.id FROM documentos doc WHERE doc.processo_id = d.processo_id "
            "AND doc.nome = d.nome || '.pdf' AND doc.tipo = 'application/pdf' "
            "ORDER BY doc.id DESC LIMIT 1)) "
            "FROM documentos_editoriais d "
            "WHERE d.processo_id = ? ORDER BY d.atualizado_em DESC, d.id DESC", (processo_id,)
        ).fetchall()
    finally:
        conn.close()


def obter_documento_editorial(user_id, documento_id):
    conn = create_connection()
    try:
        _garantir_tabela_documentos_editoriais(conn)
        return conn.execute(
            "SELECT d.id, d.processo_id, d.nome, d.conteudo_html "
            "FROM documentos_editoriais d JOIN processos p ON p.id = d.processo_id "
            "JOIN usuarios u ON u.id = ? "
            "WHERE d.id = ? AND p.setor_responsavel_id = u.setor_id AND u.ativo = 1",
            (user_id, documento_id)
        ).fetchone()
    finally:
        conn.close()


def salvar_documento_editorial(user_id, processo_id, documento_id, nome, conteudo_html,
                               caminho_pdf, tamanho_pdf):
    conn = create_connection()
    try:
        _garantir_tabela_historico(conn)
        _garantir_tabela_documentos_editoriais(conn)
        cursor = conn.cursor()
        caminho_row = None
        if documento_id is None:
            cursor.execute(
                "INSERT INTO documentos_editoriais "
                "(processo_id, nome, conteudo_html, criado_por_id, atualizado_por_id) "
                "VALUES (?, ?, ?, ?, ?)",
                (processo_id, nome, conteudo_html, user_id, user_id)
            )
            documento_id = cursor.lastrowid
            acao = "Documento digital criado"
            pdf_documento_id = None
        else:
            existente = cursor.execute(
                "SELECT pdf_documento_id, nome FROM documentos_editoriais "
                "WHERE id = ? AND processo_id = ?", (documento_id, processo_id)
            ).fetchone()
            if existente is None:
                raise LookupError("Documento digital não encontrado neste processo.")
            pdf_documento_id, nome_anterior = existente
            if pdf_documento_id is None:
                pdf_anterior = cursor.execute(
                    "SELECT id FROM documentos WHERE processo_id = ? AND nome = ? "
                    "AND tipo = 'application/pdf' ORDER BY id DESC LIMIT 1",
                    (processo_id, f"{nome_anterior}.pdf")
                ).fetchone()
                if pdf_anterior:
                    pdf_documento_id = pdf_anterior[0]
            cursor.execute(
                "UPDATE documentos_editoriais SET nome = ?, conteudo_html = ?, "
                "atualizado_por_id = ?, atualizado_em = datetime('now'), pdf_documento_id = ? "
                "WHERE id = ? AND processo_id = ?",
                (nome, conteudo_html, user_id, pdf_documento_id, documento_id, processo_id)
            )
            if cursor.rowcount != 1:
                raise LookupError("Documento digital não encontrado neste processo.")
            acao = "Documento digital atualizado"
        cursor.execute("UPDATE processos SET atualizado_em = datetime('now') WHERE id = ?", (processo_id,))
        caminho_antigo = None
        if pdf_documento_id is not None:
            caminho_row = cursor.execute(
                "SELECT caminho_arquivo FROM documentos WHERE id = ? AND processo_id = ?",
                (pdf_documento_id, processo_id)
            ).fetchone()
            if caminho_row:
                caminho_antigo = caminho_row[0]
                cursor.execute(
                    "UPDATE documentos SET nome = ?, caminho_arquivo = ?, tipo = 'application/pdf', "
                    "tamanho_bytes = ?, enviado_por_id = ?, criado_em = datetime('now') WHERE id = ?",
                    (f"{nome}.pdf", caminho_pdf, tamanho_pdf, user_id, pdf_documento_id)
                )
        if not caminho_row:
            cursor.execute(
                "INSERT INTO documentos (processo_id, nome, caminho_arquivo, tipo, tamanho_bytes, enviado_por_id) "
                "VALUES (?, ?, ?, 'application/pdf', ?, ?)",
                (processo_id, f"{nome}.pdf", caminho_pdf, tamanho_pdf, user_id)
            )
            pdf_documento_id = cursor.lastrowid
            cursor.execute(
                "UPDATE documentos_editoriais SET pdf_documento_id = ? WHERE id = ?",
                (pdf_documento_id, documento_id)
            )
        cursor.execute(
            "INSERT INTO historico (processo_id, usuario_id, acao, descricao) VALUES (?, ?, ?, ?)",
            (processo_id, user_id, acao, f"PDF do documento editorial '{nome}' gerado.")
        )
        conn.commit()
        return documento_id, pdf_documento_id, caminho_antigo
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
