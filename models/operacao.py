from models.database import get_connection
import sqlite3

class CrudOperacao:
    @staticmethod
    def criar(nome, descricao="", ativo=True):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome da operação não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO operacao (nome, descricao, ativo) VALUES (?, ?, ?)", 
                          (nome.strip(), descricao, 1 if ativo else 0))
            conn.commit()
            return True, "Operação criada com sucesso."
        except sqlite3.IntegrityError:
            return False, f"Já existe uma operação com o nome '{nome}'."
        except Exception as e:
            return False, f"Erro ao criar operação: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def listar_todos(apenas_ativos=True):
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT id, nome, descricao, ativo FROM operacao"
        if apenas_ativos:
            sql += " WHERE ativo = 1"
        sql += " ORDER BY nome"
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return [{"id": row["id"], "nome": row["nome"], "descricao": row["descricao"], "ativo": row["ativo"]} for row in rows]
    
    @staticmethod
    def buscar_por_id(oid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, descricao, ativo FROM operacao WHERE id = ?", (oid,))
        row = cursor.fetchone()
        conn.close()
        return {"id": row["id"], "nome": row["nome"], "descricao": row["descricao"], "ativo": row["ativo"]} if row else None
    
    @staticmethod
    def atualizar(oid, novo_nome, nova_descricao, ativo):
        if not novo_nome or len(novo_nome.strip()) == 0:
            return False, "Nome da operação não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE operacao SET nome = ?, descricao = ?, ativo = ? WHERE id = ?", 
                          (novo_nome.strip(), nova_descricao, 1 if ativo else 0, oid))
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
            return False, "Não é possível excluir: existem ambientes vinculados a esta operação. Desative em vez de excluir."
        
        # Verifica se existem produtos vinculados
        cursor.execute("SELECT COUNT(*) FROM operacao_produto WHERE operacao_id = ?", (oid,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Não é possível excluir: existem produtos vinculados a esta operação. Desative em vez de excluir."
        
        # Verifica se existem serviços vinculados
        cursor.execute("SELECT COUNT(*) FROM operacao_servico WHERE operacao_id = ?", (oid,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Não é possível excluir: existem serviços vinculados a esta operação. Desative em vez de excluir."
        
        try:
            cursor.execute("DELETE FROM operacao WHERE id = ?", (oid,))
            conn.commit()
            return True, "Operação excluída com sucesso."
        except Exception as e:
            return False, f"Erro ao excluir: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def listar_produtos(operacao_id, apenas_ativos=True):
        """Retorna os produtos vinculados a uma operação"""
        from models.produto import CrudProduto
        return CrudProduto.listar_por_operacao(operacao_id, apenas_ativos)
    
    @staticmethod
    def listar_servicos(operacao_id, apenas_ativos=True):
        """Retorna os serviços vinculados a uma operação"""
        from models.servico import CrudServico
        return CrudServico.listar_por_operacao(operacao_id, apenas_ativos)