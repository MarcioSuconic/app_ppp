from models.database import get_connection
import sqlite3

class CrudColaborador:
    @staticmethod
    def criar(nome, eh_socio=False, funcao_principal_id=None, observacao=""):
        if not nome or len(nome.strip()) == 0:
            return False, None, "Nome do colaborador não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO colaborador (nome, eh_socio, funcao_principal_id, observacao)
                VALUES (?, ?, ?, ?)
            """, (nome.strip(), 1 if eh_socio else 0, funcao_principal_id, observacao))
            conn.commit()
            return True, cursor.lastrowid, "Colaborador criado com sucesso."
        except Exception as e:
            return False, None, f"Erro ao criar colaborador: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def listar_todos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.nome, c.eh_socio, c.observacao, 
                   f.nome as funcao_principal_nome, c.funcao_principal_id
            FROM colaborador c
            LEFT JOIN funcao f ON c.funcao_principal_id = f.id
            ORDER BY c.nome
        """)
        rows = cursor.fetchall()
        conn.close()
        
        resultado = []
        for row in rows:
            resultado.append({
                "id": row["id"],
                "nome": row["nome"],
                "eh_socio": "Sim" if row["eh_socio"] else "Não",
                "funcao_principal_nome": row["funcao_principal_nome"] or "(nenhuma)",
                "observacao": row["observacao"] or "-"
            })
        return resultado
    
    @staticmethod
    def buscar_por_id(cid):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, f.nome as funcao_principal_nome
            FROM colaborador c
            LEFT JOIN funcao f ON c.funcao_principal_id = f.id
            WHERE c.id = ?
        """, (cid,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def adicionar_funcao(colaborador_id, funcao_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO colaborador_funcao (colaborador_id, funcao_id) VALUES (?, ?)",
                          (colaborador_id, funcao_id))
            conn.commit()
            return True, "Função adicionada ao colaborador."
        except sqlite3.IntegrityError:
            return False, "Colaborador já possui esta função."
        except Exception as e:
            return False, f"Erro: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def remover_funcao(colaborador_id, funcao_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM colaborador_funcao WHERE colaborador_id = ? AND funcao_id = ?",
                      (colaborador_id, funcao_id))
        conn.commit()
        conn.close()
        return True, "Função removida."
    
    @staticmethod
    def listar_funcoes_do_colaborador(colaborador_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.id, f.nome
            FROM colaborador_funcao cf
            JOIN funcao f ON cf.funcao_id = f.id
            WHERE cf.colaborador_id = ?
            ORDER BY f.nome
        """, (colaborador_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{"id": row["id"], "nome": row["nome"]} for row in rows]
    
    @staticmethod
    def atualizar(cid, novo_nome, eh_socio, funcao_principal_id, observacao):
        if not novo_nome or len(novo_nome.strip()) == 0:
            return False, "Nome do colaborador não pode estar vazio."
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE colaborador 
                SET nome = ?, eh_socio = ?, funcao_principal_id = ?, observacao = ?
                WHERE id = ?
            """, (novo_nome.strip(), 1 if eh_socio else 0, funcao_principal_id, observacao, cid))
            conn.commit()
            return True, "Colaborador atualizado com sucesso."
        except Exception as e:
            return False, f"Erro ao atualizar: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def excluir(cid):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM colaborador_funcao WHERE colaborador_id = ?", (cid,))
        
        try:
            cursor.execute("DELETE FROM colaborador WHERE id = ?", (cid,))
            conn.commit()
            return True, "Colaborador excluído com sucesso."
        except Exception as e:
            return False, f"Erro ao excluir: {str(e)}"
        finally:
            conn.close()