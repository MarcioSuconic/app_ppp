from models.database import get_connection
import sqlite3

class CrudTarefa:
    @staticmethod
    def validar_funcao_tem_colaborador(funcao_id):
        """Verifica se existe pelo menos um colaborador com esta função (como principal ou adicional)"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM colaborador_funcao WHERE funcao_id = ?", (funcao_id,))
        count_adicionais = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM colaborador WHERE funcao_principal_id = ?", (funcao_id,))
        count_principais = cursor.fetchone()[0]
        
        conn.close()
        return (count_adicionais + count_principais) > 0
    
    @staticmethod
    def listar_colaboradores_por_funcao(funcao_id):
        """Retorna colaboradores que têm uma determinada função (como principal ou adicional)"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT c.id, c.nome 
            FROM colaborador c
            LEFT JOIN colaborador_funcao cf ON c.id = cf.colaborador_id AND cf.funcao_id = ?
            WHERE c.funcao_principal_id = ? OR cf.funcao_id = ?
            ORDER BY c.nome
        """, (funcao_id, funcao_id, funcao_id))
        rows = cursor.fetchall()
        conn.close()
        return [{"id": row["id"], "nome": row["nome"]} for row in rows]
    
    @staticmethod
    def calcular_vezes_mes(frequencia_tipo):
        if frequencia_tipo == 'diaria':
            return 30
        elif frequencia_tipo == 'semanal':
            return 30 / 7
        elif frequencia_tipo == 'quinzenal':
            return 2
        elif frequencia_tipo == 'mensal':
            return 1
        else:
            return 0
    
    @staticmethod
    def criar(nome, duracao_minutos, frequencia_tipo, funcao_id, 
              colaborador_id=None, ambiente_id=None, equipamento_id=None, observacao=""):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome da tarefa não pode estar vazio."
        if duracao_minutos <= 0:
            return False, "Duração deve ser maior que zero."
        if frequencia_tipo not in ['diaria', 'semanal', 'quinzenal', 'mensal', 'unica']:
            return False, "Frequência inválida."
        
        if not CrudTarefa.validar_funcao_tem_colaborador(funcao_id):
            return False, f"Não é possível criar tarefa. Não há nenhum colaborador cadastrado com a função selecionada."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO tarefa 
                (nome, duracao_minutos, frequencia_tipo, funcao_id, colaborador_id, ambiente_id, equipamento_id, observacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome.strip(), duracao_minutos, frequencia_tipo, funcao_id, 
                  colaborador_id, ambiente_id, equipamento_id, observacao))
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
                   c.nome as colaborador_nome,
                   a.nome as ambiente_nome,
                   op.nome as operacao_nome,
                   e.nome as equipamento_nome
            FROM tarefa t
            JOIN funcao f ON t.funcao_id = f.id
            LEFT JOIN colaborador c ON t.colaborador_id = c.id
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
        cursor.execute("""
            SELECT t.*, f.nome as funcao_nome, c.nome as colaborador_nome
            FROM tarefa t
            JOIN funcao f ON t.funcao_id = f.id
            LEFT JOIN colaborador c ON t.colaborador_id = c.id
            WHERE t.id = ?
        """, (tid,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def atualizar(tid, nome, duracao_minutos, frequencia_tipo, funcao_id,
                  colaborador_id=None, ambiente_id=None, equipamento_id=None, observacao=""):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome da tarefa não pode estar vazio."
        
        if not CrudTarefa.validar_funcao_tem_colaborador(funcao_id):
            return False, f"Não é possível atualizar tarefa. Não há nenhum colaborador com esta função."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE tarefa 
                SET nome=?, duracao_minutos=?, frequencia_tipo=?, funcao_id=?, 
                    colaborador_id=?, ambiente_id=?, equipamento_id=?, observacao=?
                WHERE id=?
            """, (nome.strip(), duracao_minutos, frequencia_tipo, funcao_id,
                  colaborador_id, ambiente_id, equipamento_id, observacao, tid))
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
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                t.nome as tarefa,
                f.nome as funcao,
                c.nome as colaborador,
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
            LEFT JOIN colaborador c ON t.colaborador_id = c.id
            LEFT JOIN ambiente a ON t.ambiente_id = a.id
            LEFT JOIN operacao op ON a.operacao_id = op.id
            LEFT JOIN equipamento e ON t.equipamento_id = e.id
            ORDER BY f.nome, t.nome
        """)
        rows = cursor.fetchall()
        conn.close()
        
        resultado = []
        for row in rows:
            resultado.append({
                "tarefa": row["tarefa"],
                "funcao": row["funcao"],
                "colaborador": row["colaborador"] if row["colaborador"] else "(não atribuído)",
                "duracao_minutos": row["duracao_minutos"],
                "frequencia_tipo": row["frequencia_tipo"],
                "vezes_mes": row["vezes_mes"],
                "horas_mes": row["horas_mes"],
                "operacao": row["operacao"],
                "ambiente": row["ambiente"],
                "equipamento": row["equipamento"],
                "observacao": row["observacao"]
            })
        return resultado
        
    @staticmethod
    def tarefas_por_colaborador():
        """Retorna lista de tarefas agrupadas por colaborador"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                c.nome as colaborador,
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
                e.nome as equipamento
            FROM tarefa t
            JOIN funcao f ON t.funcao_id = f.id
            JOIN colaborador c ON t.colaborador_id = c.id
            LEFT JOIN ambiente a ON t.ambiente_id = a.id
            LEFT JOIN operacao op ON a.operacao_id = op.id
            LEFT JOIN equipamento e ON t.equipamento_id = e.id
            ORDER BY c.nome, t.nome
        """)
        rows = cursor.fetchall()
        conn.close()
        
        resultado = []
        for row in rows:
            resultado.append({
                "colaborador": row["colaborador"],
                "tarefa": row["tarefa"],
                "funcao": row["funcao"],
                "duracao_horas": round(row["duracao_minutos"] / 60, 1),
                "frequencia": row["frequencia_tipo"],
                "vezes_mes": round(row["vezes_mes"], 2),
                "horas_mes": round(row["horas_mes"], 2),
                "operacao": row["operacao"] or "-",
                "ambiente": row["ambiente"] or "-",
                "equipamento": row["equipamento"] or "-"
            })
        return resultado

    @staticmethod
    def resumo_horas_por_colaborador():
        """Retorna total de horas/mês por colaborador"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                c.nome as colaborador,
                SUM((t.duracao_minutos / 60.0) * 
                    CASE t.frequencia_tipo
                        WHEN 'diaria' THEN 30
                        WHEN 'semanal' THEN 30.0/7
                        WHEN 'quinzenal' THEN 2
                        WHEN 'mensal' THEN 1
                        ELSE 0
                    END) as total_horas_mes
            FROM tarefa t
            JOIN colaborador c ON t.colaborador_id = c.id
            GROUP BY c.nome
            ORDER BY total_horas_mes DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [{"colaborador": row["colaborador"], "total_horas_mes": round(row["total_horas_mes"], 2)} for row in rows]