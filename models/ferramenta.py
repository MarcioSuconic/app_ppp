from models.database import get_connection

class CrudFerramenta:
    @staticmethod
    def criar(descricao, tipo_ferramenta_id, marca_id=None, valor_compra=0.0,
              data_compra="", ambiente_id=None, observacao="", ativo=True):
        if not descricao or len(descricao.strip()) == 0:
            return False, "Descrição da ferramenta não pode estar vazia."
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO ferramenta 
                (descricao, tipo_ferramenta_id, marca_id, valor_compra, data_compra, ambiente_id, observacao, ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (descricao.strip(), tipo_ferramenta_id, marca_id, valor_compra,
                  data_compra, ambiente_id, observacao, 1 if ativo else 0))
            conn.commit()
            return True, "Ferramenta criada com sucesso."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def listar_todos(apenas_ativos=True):
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT f.*, 
                   tf.nome as tipo_nome,
                   m.nome as marca_nome,
                   a.nome as ambiente_nome,
                   op.nome as operacao_nome
            FROM ferramenta f
            LEFT JOIN tipo_ferramenta tf ON f.tipo_ferramenta_id = tf.id
            LEFT JOIN marca m ON f.marca_id = m.id
            LEFT JOIN ambiente a ON f.ambiente_id = a.id
            LEFT JOIN operacao op ON a.operacao_id = op.id
        """
        if apenas_ativos:
            sql += " WHERE f.ativo = 1"
        sql += " ORDER BY f.descricao"
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def buscar_por_id(fid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ferramenta WHERE id = ?", (fid,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def atualizar(fid, descricao, tipo_ferramenta_id, marca_id=None, valor_compra=0.0,
                  data_compra="", ambiente_id=None, observacao="", ativo=True):
        if not descricao or len(descricao.strip()) == 0:
            return False, "Descrição da ferramenta não pode estar vazia."
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE ferramenta 
                SET descricao=?, tipo_ferramenta_id=?, marca_id=?, valor_compra=?,
                    data_compra=?, ambiente_id=?, observacao=?, ativo=?
                WHERE id=?
            """, (descricao.strip(), tipo_ferramenta_id, marca_id, valor_compra,
                  data_compra, ambiente_id, observacao, 1 if ativo else 0, fid))
            conn.commit()
            return True, "Ferramenta atualizada."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def excluir(fid):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM ferramenta WHERE id = ?", (fid,))
            conn.commit()
            return True, "Ferramenta excluída."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()