from models.database import get_connection

class CrudCategoriaProduto:
    @staticmethod
    def criar(nome, descricao=""):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome da categoria não pode estar vazio."
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO categoria_produto (nome, descricao) VALUES (?, ?)", (nome.strip(), descricao))
            conn.commit()
            return True, "Categoria criada com sucesso."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def listar_todos(apenas_ativos=True):
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT id, nome, descricao, ativo FROM categoria_produto"
        if apenas_ativos:
            sql += " WHERE ativo = 1"
        sql += " ORDER BY nome"
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def buscar_por_id(cid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, descricao, ativo FROM categoria_produto WHERE id = ?", (cid,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def atualizar(cid, nome, descricao, ativo):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome da categoria não pode estar vazio."
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE categoria_produto SET nome = ?, descricao = ?, ativo = ? WHERE id = ?",
                          (nome.strip(), descricao, 1 if ativo else 0, cid))
            conn.commit()
            return True, "Categoria atualizada."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def excluir(cid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM produto WHERE categoria_id = ?", (cid,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Existem produtos vinculados a esta categoria. Desative em vez de excluir."
        try:
            cursor.execute("DELETE FROM categoria_produto WHERE id = ?", (cid,))
            conn.commit()
            return True, "Categoria excluída."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()