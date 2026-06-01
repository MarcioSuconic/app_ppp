from models.database import get_connection
from PySide6.QtWidgets import QMessageBox

class CrudOperacao:
    @staticmethod
    def criar(nome):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome da operação não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO operacao (nome) VALUES (?)", (nome.strip(),))
            conn.commit()
            return True, "Operação criada com sucesso."
        except Exception as e:
            return False, f"Erro ao criar operação: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def listar_todos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM operacao ORDER BY nome")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": row["id"], "nome": row["nome"]} for row in rows]
    
    @staticmethod
    def buscar_por_id(oid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM operacao WHERE id = ?", (oid,))
        row = cursor.fetchone()
        conn.close()
        return {"id": row["id"], "nome": row["nome"]} if row else None
    
    @staticmethod
    def atualizar(oid, novo_nome):
        if not novo_nome or len(novo_nome.strip()) == 0:
            return False, "Nome da operação não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE operacao SET nome = ? WHERE id = ?", (novo_nome.strip(), oid))
            conn.commit()
            return True, "Operação atualizada com sucesso."
        except Exception as e:
            return False, f"Erro ao atualizar: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def excluir(oid):
        # Verifica se existem ambientes vinculados
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ambiente WHERE operacao_id = ?", (oid,))
        count = cursor.fetchone()[0]
        if count > 0:
            conn.close()
            return False, f"Não é possível excluir: existem {count} ambiente(s) vinculado(s) a esta operação."
        
        try:
            cursor.execute("DELETE FROM operacao WHERE id = ?", (oid,))
            conn.commit()
            return True, "Operação excluída com sucesso."
        except Exception as e:
            return False, f"Erro ao excluir: {str(e)}"
        finally:
            conn.close()