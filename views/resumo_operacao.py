from models.database import get_connection

class ResumoOperacao:
    @staticmethod
    def get_tarefas_por_operacao(operacao_id):
        """Retorna todas as tarefas da operação com colaborador"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.id, t.nome as tarefa, 
                t.duracao_minutos,
                t.frequencia_tipo,
                f.nome as funcao,
                c.nome as colaborador,
                a.nome as ambiente,
                eq.nome as equipamento,
                t.observacao
            FROM tarefa t
            JOIN funcao f ON t.funcao_id = f.id
            LEFT JOIN colaborador c ON t.colaborador_id = c.id
            JOIN ambiente a ON t.ambiente_id = a.id
            LEFT JOIN equipamento eq ON t.equipamento_id = eq.id
            WHERE a.operacao_id = ?
            ORDER BY f.nome, t.nome
        """, (operacao_id,))
        rows = cursor.fetchall()
        conn.close()
        
        resultado = []
        for row in rows:
            duracao_horas = row["duracao_minutos"] / 60
            if row["frequencia_tipo"] == 'diaria':
                vezes_mes = 30
            elif row["frequencia_tipo"] == 'semanal':
                vezes_mes = 30 / 7
            elif row["frequencia_tipo"] == 'quinzenal':
                vezes_mes = 2
            elif row["frequencia_tipo"] == 'mensal':
                vezes_mes = 1
            else:
                vezes_mes = 0
            
            horas_mes = duracao_horas * vezes_mes
            
            resultado.append({
                "id": row["id"],
                "tarefa": row["tarefa"],
                "duracao_horas": round(duracao_horas, 1),
                "frequencia": row["frequencia_tipo"],
                "vezes_mes": round(vezes_mes, 2),
                "horas_mes": round(horas_mes, 2),
                "funcao": row["funcao"],
                "colaborador": row["colaborador"] if row["colaborador"] else "(não atribuído)",
                "ambiente": row["ambiente"],
                "equipamento": row["equipamento"] or "-",
                "observacao": row["observacao"] or "-"
            })
        
        return resultado
    @staticmethod
    def get_equipamentos_por_operacao(operacao_id):
        """Retorna equipamentos da operação"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*, a.nome as ambiente_nome
            FROM equipamento e
            JOIN ambiente a ON e.ambiente_id = a.id
            WHERE a.operacao_id = ?
            ORDER BY a.nome, e.nome
        """, (operacao_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_horas_por_funcao_na_operacao(operacao_id):
        """Retorna horas/mês por função na operação"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.nome as funcao,
                   SUM((t.duracao_minutos / 60.0) * 
                       CASE t.frequencia_tipo
                           WHEN 'diaria' THEN 30
                           WHEN 'semanal' THEN 30.0/7
                           WHEN 'quinzenal' THEN 2
                           WHEN 'mensal' THEN 1
                           ELSE 0
                       END) as horas_mes
            FROM tarefa t
            JOIN funcao f ON t.funcao_id = f.id
            JOIN ambiente a ON t.ambiente_id = a.id
            WHERE a.operacao_id = ?
            GROUP BY f.nome
            ORDER BY horas_mes DESC
        """, (operacao_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{"funcao": row["funcao"], "horas_mes": round(row["horas_mes"], 2)} for row in rows]
    
    @staticmethod
    def get_produtos_por_operacao(operacao_id, apenas_ativos=True):
        """Retorna produtos vinculados a uma operação, com categoria"""
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT p.id, p.nome, p.descricao, p.preco_sugerido, p.custo_producao,
                p.quantidade_por_unidade, u.sigla as unidade_sigla,
                c.nome as categoria_nome
            FROM produto p
            JOIN operacao_produto op ON p.id = op.produto_id
            LEFT JOIN unidade u ON p.unidade_id = u.id
            LEFT JOIN categoria_produto c ON p.categoria_id = c.id
            WHERE op.operacao_id = ?
        """
        if apenas_ativos:
            sql += " AND p.ativo = 1"
        sql += " ORDER BY c.nome, p.nome"
        cursor.execute(sql, (operacao_id,))
        rows = cursor.fetchall()
        conn.close()
        
        resultado = []
        for row in rows:
            resultado.append({
                "id": row["id"],
                "nome": row["nome"],
                "descricao": row["descricao"] or "-",
                "preco": row["preco_sugerido"] or 0,
                "custo": row["custo_producao"] or 0,
                "unidade": f"{row['quantidade_por_unidade']} {row['unidade_sigla']}" if row['unidade_sigla'] else "-",
                "categoria": row["categoria_nome"] or "-"
            })
        return resultado

    @staticmethod
    def get_servicos_por_operacao(operacao_id, apenas_ativos=True):
        """Retorna serviços vinculados a uma operação, com categoria"""
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT s.id, s.nome, s.descricao, s.preco_sugerido, s.custo_producao,
                s.duracao_padrao_minutos,
                c.nome as categoria_nome
            FROM servico s
            JOIN operacao_servico os ON s.id = os.servico_id
            LEFT JOIN categoria_servico c ON s.categoria_id = c.id
            WHERE os.operacao_id = ?
        """
        if apenas_ativos:
            sql += " AND s.ativo = 1"
        sql += " ORDER BY c.nome, s.nome"
        cursor.execute(sql, (operacao_id,))
        rows = cursor.fetchall()
        conn.close()
        
        resultado = []
        for row in rows:
            resultado.append({
                "id": row["id"],
                "nome": row["nome"],
                "descricao": row["descricao"] or "-",
                "preco": row["preco_sugerido"] or 0,
                "custo": row["custo_producao"] or 0,
                "duracao": row["duracao_padrao_minutos"] or 0,
                "categoria": row["categoria_nome"] or "-"
            })
        return resultado