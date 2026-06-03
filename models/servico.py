from models.database import get_connection

class CrudServico:
    @staticmethod
    def criar(nome, descricao="", duracao_padrao_minutos=0,
              custo_producao=0.0, preco_sugerido=0.0, categoria_id=None):
        if not nome or len(nome.strip()) == 0:
            return False, None, "Nome do serviço não pode estar vazio."
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO servico (nome, descricao, duracao_padrao_minutos,
                                   custo_producao, preco_sugerido, categoria_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nome.strip(), descricao, duracao_padrao_minutos,
                  custo_producao, preco_sugerido, categoria_id))
            conn.commit()
            return True, cursor.lastrowid, "Serviço criado com sucesso."
        except Exception as e:
            return False, None, f"Erro: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def listar_todos(apenas_ativos=True):
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT s.*, c.nome as categoria_nome
            FROM servico s
            LEFT JOIN categoria_servico c ON s.categoria_id = c.id
        """
        if apenas_ativos:
            sql += " WHERE s.ativo = 1"
        sql += " ORDER BY s.nome"
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def listar_por_operacao(operacao_id, apenas_ativos=True):
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT s.*, c.nome as categoria_nome
            FROM servico s
            JOIN operacao_servico os ON s.id = os.servico_id
            LEFT JOIN categoria_servico c ON s.categoria_id = c.id
            WHERE os.operacao_id = ?
        """
        if apenas_ativos:
            sql += " AND s.ativo = 1"
        sql += " ORDER BY c.nome, s.nome"
        cursor.execute(sql, (operacao_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def buscar_por_id(sid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.*, c.nome as categoria_nome
            FROM servico s
            LEFT JOIN categoria_servico c ON s.categoria_id = c.id
            WHERE s.id = ?
        """, (sid,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def atualizar(sid, nome, descricao, duracao_padrao_minutos,
                  custo_producao, preco_sugerido, categoria_id, ativo):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome do serviço não pode estar vazio."
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE servico SET nome=?, descricao=?, duracao_padrao_minutos=?,
                custo_producao=?, preco_sugerido=?, categoria_id=?, ativo=?
                WHERE id=?
            """, (nome.strip(), descricao, duracao_padrao_minutos,
                  custo_producao, preco_sugerido, categoria_id, 1 if ativo else 0, sid))
            conn.commit()
            return True, "Serviço atualizado."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def excluir(sid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM operacao_servico WHERE servico_id = ?", (sid,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Existem operações vinculadas a este serviço. Desative em vez de excluir."
        cursor.execute("SELECT COUNT(*) FROM servico_equipamento WHERE servico_id = ?", (sid,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Existem equipamentos vinculados a este serviço. Desative em vez de excluir."
        try:
            cursor.execute("DELETE FROM servico WHERE id = ?", (sid,))
            conn.commit()
            return True, "Serviço excluído."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def vincular_operacao(servico_id, operacao_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO operacao_servico (servico_id, operacao_id) VALUES (?, ?)",
                          (servico_id, operacao_id))
            conn.commit()
            return True, "Serviço vinculado à operação."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def desvincular_operacao(servico_id, operacao_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM operacao_servico WHERE servico_id = ? AND operacao_id = ?",
                      (servico_id, operacao_id))
        conn.commit()
        conn.close()
        return True, "Desvinculado."
    
    @staticmethod
    def listar_operacoes_vinculadas(servico_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, o.nome
            FROM operacao_servico os
            JOIN operacao o ON os.operacao_id = o.id
            WHERE os.servico_id = ?
        """, (servico_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def vincular_equipamento(servico_id, equipamento_id, tempo_minutos):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO servico_equipamento (servico_id, equipamento_id, tempo_minutos) VALUES (?, ?, ?)",
                          (servico_id, equipamento_id, tempo_minutos))
            conn.commit()
            return True, "Equipamento vinculado ao serviço."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def desvincular_equipamento(servico_id, equipamento_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM servico_equipamento WHERE servico_id = ? AND equipamento_id = ?",
                      (servico_id, equipamento_id))
        conn.commit()
        conn.close()
        return True, "Desvinculado."
    
    @staticmethod
    def listar_equipamentos_vinculados(servico_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id, e.nome, se.tempo_minutos
            FROM servico_equipamento se
            JOIN equipamento e ON se.equipamento_id = e.id
            WHERE se.servico_id = ?
        """, (servico_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]