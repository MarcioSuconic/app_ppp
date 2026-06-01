from models.database import get_connection
import sqlite3

class CrudTarefa:
    @staticmethod
    def calcular_vezes_mes(frequencia_tipo):
        """Retorna quantas vezes por mês a tarefa ocorre (base 30 dias)"""
        if frequencia_tipo == 'diaria':
            return 30
        elif frequencia_tipo == 'semanal':
            return 30 / 7  # 4.2857
        elif frequencia_tipo == 'quinzenal':
            return 2
        elif frequencia_tipo == 'mensal':
            return 1
        else:  # unica
            return 0
    
    @staticmethod
    def criar(nome, duracao_minutos, frequencia_tipo, funcao_id, 
              ambiente_id=None, equipamento_id=None, observacao=""):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome da tarefa não pode estar vazio."
        if duracao_minutos <= 0:
            return False, "Duração deve ser maior que zero."
        if frequencia_tipo not in ['diaria', 'semanal', 'quinzenal', 'mensal', 'unica']:
            return False, "Frequência inválida."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO tarefa 
                (nome, duracao_minutos, frequencia_tipo, funcao_id, ambiente_id, equipamento_id, observacao)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nome.strip(), duracao_minutos, frequencia_tipo, funcao_id, 
                  ambiente_id, equipamento_id, observacao))
            conn.commit()
            return True, "Tarefa criada com sucesso."
        except Exception as e:
            return False, f"Erro ao criar tarefa: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def listar_todos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.*, 
                   f.nome as funcao_nome,
                   a.nome as ambiente_nome,
                   op.nome as operacao_nome,
                   e.nome as equipamento_nome
            FROM tarefa t
            JOIN funcao f ON t.funcao_id = f.id
            LEFT JOIN ambiente a ON t.ambiente_id = a.id
            LEFT JOIN operacao op ON a.operacao_id = op.id
            LEFT JOIN equipamento e ON t.equipamento_id = e.id
            ORDER BY f.nome, t.nome
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def buscar_por_id(tid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tarefa WHERE id = ?", (tid,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def atualizar(tid, nome, duracao_minutos, frequencia_tipo, funcao_id,
                  ambiente_id=None, equipamento_id=None, observacao=""):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome da tarefa não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE tarefa 
                SET nome=?, duracao_minutos=?, frequencia_tipo=?, funcao_id=?, 
                    ambiente_id=?, equipamento_id=?, observacao=?
                WHERE id=?
            """, (nome.strip(), duracao_minutos, frequencia_tipo, funcao_id,
                  ambiente_id, equipamento_id, observacao, tid))
            conn.commit()
            return True, "Tarefa atualizada com sucesso."
        except Exception as e:
            return False, f"Erro ao atualizar: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def excluir(tid):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM tarefa WHERE id = ?", (tid,))
            conn.commit()
            return True, "Tarefa excluída com sucesso."
        except Exception as e:
            return False, f"Erro ao excluir: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def horas_mensais_por_funcao():
        """Retorna total de horas/mês por função baseado nas tarefas cadastradas"""
        conn = get_connection()
        cursor = conn.cursor()
        
        tarefas = CrudTarefa.listar_todos()
        resultado = {}
        
        for tarefa in tarefas:
            funcao = tarefa['funcao_nome']
            duracao_horas = tarefa['duracao_minutos'] / 60
            vezes_mes = CrudTarefa.calcular_vezes_mes(tarefa['frequencia_tipo'])
            horas_mes = duracao_horas * vezes_mes
            
            if funcao not in resultado:
                resultado[funcao] = 0
            resultado[funcao] += horas_mes
        
        conn.close()
        return resultado
    
    @staticmethod
    def lista_completa_relatorio():
        """Retorna lista de tarefas para o relatório Excel"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                t.nome as tarefa,
                f.nome as funcao,
                t.duracao_minutos,
                t.frequencia_tipo,
                CASE t.frequencia_tipo
                    WHEN 'diaria' THEN 30
                    WHEN 'semanal' THEN 30.0/7
                    WHEN 'quinzenal' THEN 2
                    WHEN 'mensal' THEN 1
                    ELSE 0
                END as vezes_mes,
                (t.duracao_minutos / 60.0) * 
                CASE t.frequencia_tipo
                    WHEN 'diaria' THEN 30
                    WHEN 'semanal' THEN 30.0/7
                    WHEN 'quinzenal' THEN 2
                    WHEN 'mensal' THEN 1
                    ELSE 0
                END as horas_mes,
                op.nome as operacao,
                a.nome as ambiente,
                e.nome as equipamento,
                t.observacao
            FROM tarefa t
            JOIN funcao f ON t.funcao_id = f.id
            LEFT JOIN ambiente a ON t.ambiente_id = a.id
            LEFT JOIN operacao op ON a.operacao_id = op.id
            LEFT JOIN equipamento e ON t.equipamento_id = e.id
            ORDER BY f.nome, t.nome
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]