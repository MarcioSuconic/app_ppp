from models.database import get_connection

class CrudTipoFerramenta:
    @staticmethod
    def criar(nome):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome do tipo não pode estar vazio."
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO tipo_ferramenta (nome) VALUES (?)", (nome.strip(),))
            conn.commit()
            return True, "Tipo de ferramenta criado."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def listar_todos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM tipo_ferramenta ORDER BY nome")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": row["id"], "nome": row["nome"]} for row in rows]

    @staticmethod
    def buscar_por_id(tid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM tipo_ferramenta WHERE id = ?", (tid,))
        row = cursor.fetchone()
        conn.close()
        return {"id": row["id"], "nome": row["nome"]} if row else None

    @staticmethod
    def atualizar(tid, novo_nome):
        if not novo_nome or len(novo_nome.strip()) == 0:
            return False, "Nome do tipo não pode estar vazio."
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE tipo_ferramenta SET nome = ? WHERE id = ?", (novo_nome.strip(), tid))
            conn.commit()
            return True, "Tipo atualizado."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def excluir(tid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ferramenta WHERE tipo_ferramenta_id = ?", (tid,))
        count = cursor.fetchone()[0]
        if count > 0:
            conn.close()
            return False, f"Tipo usado por {count} ferramenta(s)."
        try:
            cursor.execute("DELETE FROM tipo_ferramenta WHERE id = ?", (tid,))
            conn.commit()
            return True, "Tipo excluído."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()