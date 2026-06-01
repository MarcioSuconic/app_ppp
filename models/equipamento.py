from models.database import get_connection
import sqlite3

class CrudEquipamento:
    @staticmethod
    def criar(nome, marca="", modelo="", capacidade="", preco_estimado=0.0,
              data_compra="", fornecedor="", numero_serie="", ultima_manutencao="", 
              observacao="", ambiente_id=None):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome do equipamento não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO equipamento 
                (nome, marca, modelo, capacidade, preco_estimado, data_compra, 
                 fornecedor, numero_serie, ultima_manutencao, observacao, ambiente_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome.strip(), marca, modelo, capacidade, preco_estimado, data_compra,
                  fornecedor, numero_serie, ultima_manutencao, observacao, ambiente_id))
            conn.commit()
            return True, "Equipamento criado com sucesso."
        except Exception as e:
            return False, f"Erro ao criar equipamento: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def listar_todos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*, a.nome as ambiente_nome, op.nome as operacao_nome
            FROM equipamento e
            LEFT JOIN ambiente a ON e.ambiente_id = a.id
            LEFT JOIN operacao op ON a.operacao_id = op.id
            ORDER BY op.nome, a.nome, e.nome
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def listar_por_ambiente(ambiente_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM equipamento WHERE ambiente_id = ? ORDER BY nome", (ambiente_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def buscar_por_id(eid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM equipamento WHERE id = ?", (eid,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def atualizar(eid, nome, marca="", modelo="", capacidade="", preco_estimado=0.0,
                  data_compra="", fornecedor="", numero_serie="", ultima_manutencao="", 
                  observacao="", ambiente_id=None):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome do equipamento não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE equipamento 
                SET nome=?, marca=?, modelo=?, capacidade=?, preco_estimado=?, 
                    data_compra=?, fornecedor=?, numero_serie=?, ultima_manutencao=?, 
                    observacao=?, ambiente_id=?
                WHERE id=?
            """, (nome.strip(), marca, modelo, capacidade, preco_estimado,
                  data_compra, fornecedor, numero_serie, ultima_manutencao,
                  observacao, ambiente_id, eid))
            conn.commit()
            return True, "Equipamento atualizado com sucesso."
        except Exception as e:
            return False, f"Erro ao atualizar: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def excluir(eid):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verifica se existem tarefas vinculadas
        cursor.execute("SELECT COUNT(*) FROM tarefa WHERE equipamento_id = ?", (eid,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Não é possível excluir: existem tarefas vinculadas a este equipamento."
        
        try:
            cursor.execute("DELETE FROM equipamento WHERE id = ?", (eid,))
            conn.commit()
            return True, "Equipamento excluído com sucesso."
        except Exception as e:
            return False, f"Erro ao excluir: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def total_preco_por_operacao():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT op.nome as operacao, SUM(e.preco_estimado) as total
            FROM equipamento e
            LEFT JOIN ambiente a ON e.ambiente_id = a.id
            LEFT JOIN operacao op ON a.operacao_id = op.id
            GROUP BY op.nome
            ORDER BY op.nome
        """)
        rows = cursor.fetchall()
        conn.close()
        return [{"operacao": row["operacao"] or "Sem operação", "total": row["total"] or 0} for row in rows]