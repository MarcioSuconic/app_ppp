from models.database import get_connection
import sqlite3

class CrudFuncao:
    @staticmethod
    def criar(nome):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome da função não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO funcao (nome) VALUES (?)", (nome.strip(),))
            conn.commit()
            return True, "Função criada com sucesso."
        except sqlite3.IntegrityError:
            return False, f"Já existe uma função com o nome '{nome}'."
        except Exception as e:
            return False, f"Erro ao criar função: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def listar_todos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM funcao ORDER BY nome")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": row["id"], "nome": row["nome"]} for row in rows]
    
    @staticmethod
    def buscar_por_id(fid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM funcao WHERE id = ?", (fid,))
        row = cursor.fetchone()
        conn.close()
        return {"id": row["id"], "nome": row["nome"]} if row else None
    
    @staticmethod
    def atualizar(fid, novo_nome):
        if not novo_nome or len(novo_nome.strip()) == 0:
            return False, "Nome da função não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE funcao SET nome = ? WHERE id = ?", (novo_nome.strip(), fid))
            conn.commit()
            return True, "Função atualizada com sucesso."
        except sqlite3.IntegrityError:
            return False, f"Já existe uma função com o nome '{novo_nome}'."
        except Exception as e:
            return False, f"Erro ao atualizar: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def excluir(fid):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verifica se existem colaboradores com esta função
        cursor.execute("SELECT COUNT(*) FROM colaborador WHERE funcao_principal_id = ?", (fid,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Não é possível excluir: existem colaboradores com esta função."
        
        # Verifica se existem tarefas com esta função
        cursor.execute("SELECT COUNT(*) FROM tarefa WHERE funcao_id = ?", (fid,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Não é possível excluir: existem tarefas vinculadas a esta função."
        
        try:
            cursor.execute("DELETE FROM funcao WHERE id = ?", (fid,))
            conn.commit()
            return True, "Função excluída com sucesso."
        except Exception as e:
            return False, f"Erro ao excluir: {str(e)}"
        finally:
            conn.close()