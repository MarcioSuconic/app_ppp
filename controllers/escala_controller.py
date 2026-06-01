from models.database import get_connection

class EscalaController:
    @staticmethod
    def validar_conflito(colaborador_id, dia_semana, hora_inicio, hora_fim, excluir_id=None):
        """Retorna True se houver conflito de horário para o mesmo colaborador no mesmo dia"""
        conn = get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id FROM escala_colaborador
            WHERE colaborador_id = ? 
            AND dia_semana = ?
            AND (
                (hora_inicio <= ? AND hora_fim > ?) OR
                (hora_inicio < ? AND hora_fim >= ?) OR
                (hora_inicio >= ? AND hora_fim <= ?)
            )
        '''
        params = [colaborador_id, dia_semana, hora_fim, hora_inicio, hora_fim, hora_inicio, hora_inicio, hora_fim]
        
        if excluir_id:
            query += ' AND id != ?'
            params.append(excluir_id)
        
        cursor.execute(query, params)
        conflito = cursor.fetchone() is not None
        conn.close()
        return conflito
    
    @staticmethod
    def adicionar_escala(colaborador_id, operacao_id, dia_semana, hora_inicio, hora_fim):
        if EscalaController.validar_conflito(colaborador_id, dia_semana, hora_inicio, hora_fim):
            return False, "Conflito de horário com escala existente"
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO escala_colaborador (colaborador_id, operacao_id, dia_semana, hora_inicio, hora_fim)
            VALUES (?, ?, ?, ?, ?)
        ''', (colaborador_id, operacao_id, dia_semana, hora_inicio, hora_fim))
        conn.commit()
        conn.close()
        return True, "OK"