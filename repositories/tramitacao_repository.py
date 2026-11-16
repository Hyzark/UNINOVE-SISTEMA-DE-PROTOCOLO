from database import create_connection


def listar_mesas_destino(processo_id, usuario_id):
    conn = create_connection()

    try:
        processo = conn.execute(
            """
            SELECT p.id
            FROM processos p
            JOIN usuarios u ON u.id = ?
            WHERE p.id = ?
              AND u.ativo = 1
              AND p.setor_responsavel_id = u.setor_id
            """,
            (usuario_id, processo_id)
        ).fetchone()

        if processo is None:
            return None

        mesas = conn.execute(
            """
            SELECT m.id, m.nome, s.id, s.nome
            FROM mesas m
            JOIN setores s ON s.id = m.setor_id
            WHERE m.ativa = 1
              AND s.ativo = 1
              AND m.id != (
                  SELECT mesa_atual_id
                  FROM processos
                  WHERE id = ?
              )
            ORDER BY s.nome, m.nome
            """,
            (processo_id,)
        ).fetchall()

        return [
            {
                "id": mesa[0],
                "nome": mesa[1],
                "setor_id": mesa[2],
                "setor": mesa[3]
            }
            for mesa in mesas
        ]

    finally:
        conn.close()
def tramitar_processo(processo_id, usuario_id, mesa_destino_id, observacao=""):
    conn = create_connection()

    try:
        processo = conn.execute(
            """
            SELECT p.id, p.mesa_atual_id, mo.nome, so.nome
            FROM processos p
            JOIN usuarios u ON u.id = ?
            LEFT JOIN mesas mo ON mo.id = p.mesa_atual_id
            LEFT JOIN setores so ON so.id = mo.setor_id
            WHERE p.id = ?
              AND u.ativo = 1
              AND p.setor_responsavel_id = u.setor_id
            """,
            (usuario_id, processo_id)
        ).fetchone()

        if processo is None:
            raise ValueError("Processo não encontrado ou sem permissão.")

        destino = conn.execute(
            """
            SELECT m.id, m.nome, s.id, s.nome
            FROM mesas m
            JOIN setores s ON s.id = m.setor_id
            WHERE m.id = ?
              AND m.ativa = 1
              AND s.ativo = 1
            """,
            (mesa_destino_id,)
        ).fetchone()

        if destino is None:
            raise ValueError("Mesa de destino inválida.")

        if processo[1] == mesa_destino_id:
            raise ValueError("O processo já está nesta mesa.")

        origem_mesa = processo[2] or "Não informada"
        origem_setor = processo[3] or "Não informado"

        descricao = (
            f"Origem: mesa {origem_mesa}, setor {origem_setor}. "
            f"Destino: mesa {destino[1]}, setor {destino[3]}."
        )

        if observacao:
            descricao += f" Observação: {observacao}"

        conn.execute(
            """
            INSERT INTO tramitacoes (
                processo_id, mesa_origem_id, mesa_destino_id,
                usuario_id, observacao
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (processo_id, processo[1], mesa_destino_id, usuario_id, descricao)
        )

        conn.execute(
            """
            UPDATE processos
            SET mesa_atual_id = ?,
                setor_responsavel_id = ?,
                atualizado_em = datetime('now')
            WHERE id = ?
            """,
            (destino[0], destino[2], processo_id)
        )

        conn.commit()

        return {
            "processo_id": processo_id,
            "mesa_origem": origem_mesa,
            "setor_origem": origem_setor,
            "mesa_destino": destino[1],
            "setor_destino": destino[3]
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def listar_mesas_destino(processo_id, usuario_id):
    conn = create_connection()
    try:
        processo = conn.execute(
            """
            SELECT p.id
            FROM processos p
            JOIN usuarios u ON u.id = ?
            WHERE p.id = ?
              AND u.ativo = 1
              AND p.setor_responsavel_id = u.setor_id
            """,
            (usuario_id, processo_id)
        ).fetchone()

        if processo is None:
            return None

        mesas = conn.execute(
            """
            SELECT m.id, m.nome, s.id, s.nome
            FROM mesas m
            JOIN setores s ON s.id = m.setor_id
            WHERE m.ativa = 1
              AND s.ativo = 1
              AND m.id != (
                  SELECT mesa_atual_id FROM processos WHERE id = ?
              )
            ORDER BY s.nome, m.nome
            """,
            (processo_id,)
        ).fetchall()

        return [
            {
                "id": m[0],
                "nome": m[1],
                "setor_id": m[2],
                "setor": m[3]
            }
            for m in mesas
        ]
    finally:
        conn.close()


def tramitar_processo(processo_id, usuario_id, mesa_destino_id, observacao=""):
    conn = create_connection()
    try:
        processo = conn.execute(
            """
            SELECT p.id, p.mesa_atual_id, mo.nome, so.nome
            FROM processos p
            JOIN usuarios u ON u.id = ?
            LEFT JOIN mesas mo ON mo.id = p.mesa_atual_id
            LEFT JOIN setores so ON so.id = mo.setor_id
            WHERE p.id = ?
              AND u.ativo = 1
              AND p.setor_responsavel_id = u.setor_id
            """,
            (usuario_id, processo_id)
        ).fetchone()

        if processo is None:
            raise ValueError("Processo não encontrado ou sem permissão para tramitar.")

        destino = conn.execute(
            """
            SELECT m.id, m.nome, s.id, s.nome
            FROM mesas m
            JOIN setores s ON s.id = m.setor_id
            WHERE m.id = ? AND m.ativa = 1 AND s.ativo = 1
            """,
            (mesa_destino_id,)
        ).fetchone()

        if destino is None:
            raise ValueError("A mesa de destino não existe ou está inativa.")

        if processo[1] == mesa_destino_id:
            raise ValueError("O processo já está nesta mesa.")

        origem_mesa = processo[2] or "Não informada"
        origem_setor = processo[3] or "Não informado"

        descricao = (
            f"Origem: mesa {origem_mesa}, setor {origem_setor}. "
            f"Destino: mesa {destino[1]}, setor {destino[3]}."
        )

        if observacao:
            descricao += f" Observação: {observacao}"

        conn.execute(
            """
            INSERT INTO tramitacoes (
                processo_id, mesa_origem_id, mesa_destino_id,
                usuario_id, observacao
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (processo_id, processo[1], mesa_destino_id, usuario_id, descricao)
        )

        conn.execute(
            """
            UPDATE processos
            SET mesa_atual_id = ?,
                setor_responsavel_id = ?,
                atualizado_em = datetime('now')
            WHERE id = ?
            """,
            (destino[0], destino[2], processo_id)
        )

        conn.commit()

        return {
            "processo_id": processo_id,
            "mesa_origem": origem_mesa,
            "setor_origem": origem_setor,
            "mesa_destino": destino[1],
            "setor_destino": destino[3]
        }

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
