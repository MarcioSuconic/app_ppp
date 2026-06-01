from models.database import get_connection

class CrudColaborador:
    @staticmethod
    def criar(nome, funcao_id, eh_socio=False):
        if not nome or len(nome.strip()) == 0:
            return False, "Nome do colaborador não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO colaborador (nome, funcao_id, eh_socio) VALUES (?, ?, ?)",
                (nome.strip(), funcao_id if funcao_id else None, 1 if eh_socio else 0)
            )
            conn.commit()
            return True, "Colaborador criado com sucesso."
        except Exception as e:
            return False, f"Erro ao criar colaborador: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def listar_todos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.nome, c.eh_socio, f.nome as funcao_nome
            FROM colaborador c
            LEFT JOIN funcao f ON c.funcao_id = f.id
            ORDER BY c.nome
        """)
        rows = cursor.fetchall()
        conn.close()
        return [{"id": row["id"], "nome": row["nome"], "eh_socio": row["eh_socio"], "funcao": row["funcao_nome"]} for row in rows]
    
    @staticmethod
    def buscar_por_id(cid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, funcao_id, eh_socio FROM colaborador WHERE id = ?", (cid,))
        row = cursor.fetchone()
        conn.close()
        return {"id": row["id"], "nome": row["nome"], "funcao_id": row["funcao_id"], "eh_socio": row["eh_socio"]} if row else None
    
    @staticmethod
    def listar_funcoes():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM funcao ORDER BY nome")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": row["id"], "nome": row["nome"]} for row in rows]
    
    @staticmethod
    def atualizar(cid, novo_nome, funcao_id, eh_socio):
        if not novo_nome or len(novo_nome.strip()) == 0:
            return False, "Nome do colaborador não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE colaborador SET nome = ?, funcao_id = ?, eh_socio = ? WHERE id = ?",
                (novo_nome.strip(), funcao_id if funcao_id else None, 1 if eh_socio else 0, cid)
            )
            conn.commit()
            return True, "Colaborador atualizado com sucesso."
        except Exception as e:
            return False, f"Erro ao atualizar: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def excluir(cid):
        # Verifica se existem escalas vinculadas
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM escala_colaborador WHERE colaborador_id = ?", (cid,))
        count = cursor.fetchone()[0]
        if count > 0:
            conn.close()
            return False, f"Não é possível excluir: existem {count} escala(s) vinculada(s) a este colaborador."
        
        try:
            cursor.execute("DELETE FROM colaborador WHERE id = ?", (cid,))
            conn.commit()
            return True, "Colaborador excluído com sucesso."
        except Exception as e:
            return False, f"Erro ao excluir: {str(e)}"
        finally:
            conn.close()