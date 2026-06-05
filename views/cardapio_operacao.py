from models.database import get_connection

class CardapioOperacao:
    @staticmethod
    def get_produtos_por_operacao(operacao_id, apenas_ativos=True):
        """Retorna produtos vinculados a uma operação"""
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT p.id, p.nome, p.descricao, p.preco_sugerido,
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
                "unidade": f"{row['quantidade_por_unidade']} {row['unidade_sigla']}" if row['unidade_sigla'] else "-",
                "categoria": row["categoria_nome"] or "-"
            })
        return resultado

    @staticmethod
    def get_servicos_por_operacao(operacao_id, apenas_ativos=True):
        """Retorna serviços vinculados a uma operação"""
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT s.id, s.nome, s.descricao, s.preco_sugerido,
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
                "duracao": row["duracao_padrao_minutos"] or 0,
                "categoria": row["categoria_nome"] or "-"
            })
        return resultado