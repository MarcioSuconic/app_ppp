from models.database import get_connection

class CrudMarca:
    @staticmethod
    def criar(nome):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome da marca não pode estar vazio."
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO marca (nome) VALUES (?)", (nome.strip(),))
            conn.commit()
            return True, "Marca criada com sucesso."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def listar_todos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM marca ORDER BY nome")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": row["id"], "nome": row["nome"]} for row in rows]

    @staticmethod
    def buscar_por_id(mid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM marca WHERE id = ?", (mid,))
        row = cursor.fetchone()
        conn.close()
        return {"id": row["id"], "nome": row["nome"]} if row else None

    @staticmethod
    def atualizar(mid, novo_nome):
        if not novo_nome or len(novo_nome.strip()) == 0:
            return False, "Nome da marca não pode estar vazio."
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE marca SET nome = ? WHERE id = ?", (novo_nome.strip(), mid))
            conn.commit()
            return True, "Marca atualizada."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def excluir(mid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM equipamento WHERE marca_id = ?", (mid,))
        count_eq = cursor.fetchone()[0]
        if count_eq > 0:
            conn.close()
            return False, f"Marca usada por {count_eq} equipamento(s)."
        cursor.execute("SELECT COUNT(*) FROM ferramenta WHERE marca_id = ?", (mid,))
        count_ft = cursor.fetchone()[0]
        if count_ft > 0:
            conn.close()
            return False, f"Marca usada por {count_ft} ferramenta(s)."
        try:
            cursor.execute("DELETE FROM marca WHERE id = ?", (mid,))
            conn.commit()
            return True, "Marca excluída."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()