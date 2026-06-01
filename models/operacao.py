from models.database import get_connection

class CrudOperacao:
    @staticmethod
    def criar(nome, descricao=""):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome da operação não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO operacao (nome, descricao) VALUES (?, ?)", (nome.strip(), descricao))
            conn.commit()
            return True, "Operação criada com sucesso."
        except sqlite3.IntegrityError:
            return False, f"Já existe uma operação com o nome '{nome}'."
        except Exception as e:
            return False, f"Erro ao criar operação: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def listar_todos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, descricao FROM operacao ORDER BY nome")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": row["id"], "nome": row["nome"], "descricao": row["descricao"]} for row in rows]
    
    @staticmethod
    def buscar_por_id(oid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, descricao FROM operacao WHERE id = ?", (oid,))
        row = cursor.fetchone()
        conn.close()
        return {"id": row["id"], "nome": row["nome"], "descricao": row["descricao"]} if row else None
    
    @staticmethod
    def atualizar(oid, novo_nome, nova_descricao):
        if not novo_nome or len(novo_nome.strip()) == 0:
            return False, "Nome da operação não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE operacao SET nome = ?, descricao = ? WHERE id = ?", (novo_nome.strip(), nova_descricao, oid))
            conn.commit()
            return True, "Operação atualizada com sucesso."
        except sqlite3.IntegrityError:
            return False, f"Já existe uma operação com o nome '{novo_nome}'."
        except Exception as e:
            return False, f"Erro ao atualizar: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def excluir(oid):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verifica se existem ambientes vinculados
        cursor.execute("SELECT COUNT(*) FROM ambiente WHERE operacao_id = ?", (oid,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Não é possível excluir: existem ambientes vinculados a esta operação."
        
        try:
            cursor.execute("DELETE FROM operacao WHERE id = ?", (oid,))
            conn.commit()
            return True, "Operação excluída com sucesso."
        except Exception as e:
            return False, f"Erro ao excluir: {str(e)}"
        finally:
            conn.close()