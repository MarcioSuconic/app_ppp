from models.database import get_connection
from controllers.escala_controller import EscalaController

class CrudEscala:
    @staticmethod
    def criar(colaborador_id, operacao_id, dia_semana, hora_inicio, hora_fim):
        # Validação de conflito
        if EscalaController.validar_conflito(colaborador_id, dia_semana, hora_inicio, hora_fim):
            return False, "Conflito de horário: colaborador já possui escala neste dia e horário."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO escala_colaborador (colaborador_id, operacao_id, dia_semana, hora_inicio, hora_fim)
                VALUES (?, ?, ?, ?, ?)
            """, (colaborador_id, operacao_id, dia_semana, hora_inicio, hora_fim))
            conn.commit()
            return True, "Escala criada com sucesso."
        except Exception as e:
            return False, f"Erro ao criar escala: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def listar_todos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id, 
                   c.nome as colaborador_nome, 
                   o.nome as operacao_nome,
                   e.dia_semana,
                   e.hora_inicio,
                   e.hora_fim
            FROM escala_colaborador e
            JOIN colaborador c ON e.colaborador_id = c.id
            JOIN operacao o ON e.operacao_id = o.id
            ORDER BY c.nome, e.dia_semana, e.hora_inicio
        """)
        rows = cursor.fetchall()
        conn.close()
        
        dias = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
        resultado = []
        for row in rows:
            resultado.append({
                "id": row["id"],
                "colaborador": row["colaborador_nome"],
                "operacao": row["operacao_nome"],
                "dia_semana": row["dia_semana"],
                "dia_nome": dias[row["dia_semana"]],
                "hora_inicio": row["hora_inicio"],
                "hora_fim": row["hora_fim"]
            })
        return resultado
    
    @staticmethod
    def buscar_por_id(eid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, colaborador_id, operacao_id, dia_semana, hora_inicio, hora_fim
            FROM escala_colaborador WHERE id = ?
        """, (eid,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def listar_colaboradores():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM colaborador ORDER BY nome")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": row["id"], "nome": row["nome"]} for row in rows]
    
    @staticmethod
    def listar_operacoes():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM operacao ORDER BY nome")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": row["id"], "nome": row["nome"]} for row in rows]
    
    @staticmethod
    def atualizar(eid, colaborador_id, operacao_id, dia_semana, hora_inicio, hora_fim):
        # Validação de conflito (excluindo a própria escala)
        if EscalaController.validar_conflito(colaborador_id, dia_semana, hora_inicio, hora_fim, excluir_id=eid):
            return False, "Conflito de horário: colaborador já possui escala neste dia e horário."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE escala_colaborador 
                SET colaborador_id = ?, operacao_id = ?, dia_semana = ?, hora_inicio = ?, hora_fim = ?
                WHERE id = ?
            """, (colaborador_id, operacao_id, dia_semana, hora_inicio, hora_fim, eid))
            conn.commit()
            return True, "Escala atualizada com sucesso."
        except Exception as e:
            return False, f"Erro ao atualizar: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def excluir(eid):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM escala_colaborador WHERE id = ?", (eid,))
            conn.commit()
            return True, "Escala excluída com sucesso."
        except Exception as e:
            return False, f"Erro ao excluir: {str(e)}"
        finally:
            conn.close()