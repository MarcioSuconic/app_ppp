from models.database import get_connection

class CrudProduto:
    @staticmethod
    def criar(nome, descricao="", unidade_id=None, quantidade_por_unidade=1.0,
              custo_producao=0.0, preco_sugerido=0.0, categoria_id=None):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome do produto não pode estar vazio."
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO produto (nome, descricao, unidade_id, quantidade_por_unidade,
                                   custo_producao, preco_sugerido, categoria_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nome.strip(), descricao, unidade_id, quantidade_por_unidade,
                  custo_producao, preco_sugerido, categoria_id))
            conn.commit()
            return True, cursor.lastrowid, "Produto criado com sucesso."
        except Exception as e:
            return False, None, f"Erro: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def listar_todos(apenas_ativos=True):
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT p.*, c.nome as categoria_nome, u.nome as unidade_nome, u.sigla as unidade_sigla
            FROM produto p
            LEFT JOIN categoria_produto c ON p.categoria_id = c.id
            LEFT JOIN unidade u ON p.unidade_id = u.id
        """
        if apenas_ativos:
            sql += " WHERE p.ativo = 1"
        sql += " ORDER BY p.nome"
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def buscar_por_id(pid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, c.nome as categoria_nome, u.nome as unidade_nome, u.sigla as unidade_sigla
            FROM produto p
            LEFT JOIN categoria_produto c ON p.categoria_id = c.id
            LEFT JOIN unidade u ON p.unidade_id = u.id
            WHERE p.id = ?
        """, (pid,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def atualizar(pid, nome, descricao, unidade_id, quantidade_por_unidade,
                  custo_producao, preco_sugerido, categoria_id, ativo):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome do produto não pode estar vazio."
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE produto SET nome=?, descricao=?, unidade_id=?, quantidade_por_unidade=?,
                custo_producao=?, preco_sugerido=?, categoria_id=?, ativo=?
                WHERE id=?
            """, (nome.strip(), descricao, unidade_id, quantidade_por_unidade,
                  custo_producao, preco_sugerido, categoria_id, 1 if ativo else 0, pid))
            conn.commit()
            return True, "Produto atualizado."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def excluir(pid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM operacao_produto WHERE produto_id = ?", (pid,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Existem operações vinculadas a este produto. Desative em vez de excluir."
        cursor.execute("SELECT COUNT(*) FROM produto_equipamento WHERE produto_id = ?", (pid,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Existem equipamentos vinculados a este produto. Desative em vez de excluir."
        try:
            cursor.execute("DELETE FROM produto WHERE id = ?", (pid,))
            conn.commit()
            return True, "Produto excluído."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def vincular_operacao(produto_id, operacao_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO operacao_produto (produto_id, operacao_id) VALUES (?, ?)",
                          (produto_id, operacao_id))
            conn.commit()
            return True, "Produto vinculado à operação."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def desvincular_operacao(produto_id, operacao_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM operacao_produto WHERE produto_id = ? AND operacao_id = ?",
                      (produto_id, operacao_id))
        conn.commit()
        conn.close()
        return True, "Desvinculado."
    
    @staticmethod
    def listar_operacoes_vinculadas(produto_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, o.nome
            FROM operacao_produto op
            JOIN operacao o ON op.operacao_id = o.id
            WHERE op.produto_id = ?
        """, (produto_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def vincular_equipamento(produto_id, equipamento_id, tempo_minutos):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO produto_equipamento (produto_id, equipamento_id, tempo_minutos) VALUES (?, ?, ?)",
                          (produto_id, equipamento_id, tempo_minutos))
            conn.commit()
            return True, "Equipamento vinculado ao produto."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def desvincular_equipamento(produto_id, equipamento_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produto_equipamento WHERE produto_id = ? AND equipamento_id = ?",
                      (produto_id, equipamento_id))
        conn.commit()
        conn.close()
        return True, "Desvinculado."
    
    @staticmethod
    def listar_equipamentos_vinculados(produto_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id, e.nome, pe.tempo_minutos
            FROM produto_equipamento pe
            JOIN equipamento e ON pe.equipamento_id = e.id
            WHERE pe.produto_id = ?
        """, (produto_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]