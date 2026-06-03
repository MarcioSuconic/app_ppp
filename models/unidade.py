from models.database import get_connection

class CrudUnidade:
    @staticmethod
    def listar_todos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, sigla, tipo, sistema, fator_para_base FROM unidade ORDER BY nome")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def buscar_por_id(uid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, sigla, tipo, sistema, fator_para_base FROM unidade WHERE id = ?", (uid,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None