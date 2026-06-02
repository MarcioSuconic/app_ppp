from models.database import get_connection
import sqlite3

class CrudAmbiente:
    @staticmethod
    def criar(nome, operacao_id, descricao=""):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome do ambiente não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO ambiente (nome, operacao_id, descricao) VALUES (?, ?, ?)", 
                          (nome.strip(), operacao_id, descricao))
            conn.commit()
            return True, "Ambiente criado com sucesso."
        except Exception as e:
            return False, f"Erro ao criar ambiente: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def listar_todos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.nome, a.descricao, o.nome as operacao_nome 
            FROM ambiente a
            JOIN operacao o ON a.operacao_id = o.id
            ORDER BY o.nome, a.nome
        """)
        rows = cursor.fetchall()
        conn.close()
        
        resultado = []
        for row in rows:
            resultado.append({
                "id": row["id"],
                "nome": row["nome"],
                "operacao": row["operacao_nome"],
                "descricao": row["descricao"] or ""
            })
        return resultado
    
    @staticmethod
    def listar_por_operacao(operacao_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, descricao FROM ambiente WHERE operacao_id = ? ORDER BY nome", (operacao_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{"id": row["id"], "nome": row["nome"], "descricao": row["descricao"]} for row in rows]
    
    @staticmethod
    def buscar_por_id(aid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.nome, a.descricao, a.operacao_id, o.nome as operacao_nome 
            FROM ambiente a
            JOIN operacao o ON a.operacao_id = o.id
            WHERE a.id = ?
        """, (aid,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row["id"],
                "nome": row["nome"],
                "descricao": row["descricao"],
                "operacao_id": row["operacao_id"],
                "operacao_nome": row["operacao_nome"]
            }
        return None
    
    @staticmethod
    def atualizar(aid, novo_nome, operacao_id, nova_descricao):
        if not novo_nome or len(novo_nome.strip()) == 0:
            return False, "Nome do ambiente não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE ambiente SET nome = ?, operacao_id = ?, descricao = ? WHERE id = ?", 
                          (novo_nome.strip(), operacao_id, nova_descricao, aid))
            conn.commit()
            return True, "Ambiente atualizado com sucesso."
        except Exception as e:
            return False, f"Erro ao atualizar: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def excluir(aid):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM equipamento WHERE ambiente_id = ?", (aid,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Não é possível excluir: existem equipamentos vinculados a este ambiente."
        
        cursor.execute("SELECT COUNT(*) FROM tarefa WHERE ambiente_id = ?", (aid,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Não é possível excluir: existem tarefas vinculadas a este ambiente."
        
        try:
            cursor.execute("DELETE FROM ambiente WHERE id = ?", (aid,))
            conn.commit()
            return True, "Ambiente excluído com sucesso."
        except Exception as e:
            return False, f"Erro ao excluir: {str(e)}"
        finally:
            conn.close()