import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'ppp.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela operacao
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT
        )
    ''')
    
    # Tabela ambiente
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ambiente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            operacao_id INTEGER NOT NULL,
            descricao TEXT,
            FOREIGN KEY (operacao_id) REFERENCES operacao (id)
        )
    ''')
    
    # Tabela equipamento (todos os campos)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            marca TEXT,
            modelo TEXT,
            capacidade TEXT,
            preco_estimado REAL,
            data_compra TEXT,
            fornecedor TEXT,
            numero_serie TEXT,
            ultima_manutencao TEXT,
            observacao TEXT,
            ambiente_id INTEGER,
            FOREIGN KEY (ambiente_id) REFERENCES ambiente (id)
        )
    ''')
    
    # Tabela funcao
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS funcao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Tabela colaborador
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS colaborador (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            eh_socio BOOLEAN DEFAULT 0,
            funcao_principal_id INTEGER,
            observacao TEXT,
            FOREIGN KEY (funcao_principal_id) REFERENCES funcao (id)
        )
    ''')
    
    # Tabela colaborador_funcao (múltiplas funções)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS colaborador_funcao (
            colaborador_id INTEGER NOT NULL,
            funcao_id INTEGER NOT NULL,
            PRIMARY KEY (colaborador_id, funcao_id),
            FOREIGN KEY (colaborador_id) REFERENCES colaborador (id),
            FOREIGN KEY (funcao_id) REFERENCES funcao (id)
        )
    ''')
    
    # Tabela tarefa (o coração do sistema)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarefa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            duracao_minutos INTEGER NOT NULL,
            frequencia_tipo TEXT NOT NULL, -- diaria, semanal, quinzenal, mensal, unica
            funcao_id INTEGER NOT NULL,
            ambiente_id INTEGER,
            equipamento_id INTEGER,
            observacao TEXT,
            FOREIGN KEY (funcao_id) REFERENCES funcao (id),
            FOREIGN KEY (ambiente_id) REFERENCES ambiente (id),
            FOREIGN KEY (equipamento_id) REFERENCES equipamento (id)
        )
    ''')
    
    # Inserir operações padrão (se não existirem)
    cursor.execute("SELECT COUNT(*) FROM operacao")
    if cursor.fetchone()[0] == 0:
        operacoes_padrao = [
            ('Bar', 'Operação principal com cozinha, cervejaria, salão, varanda, área kids'),
            ('Harmony', 'Loja de instrumentos musicais, palco, expositores'),
            ('Lanchonete/Café', 'Café e lanchonete no piso térreo'),
            ('Ateliê', 'Costura, manequins, provadores, depósito de tecidos')
        ]
        cursor.executemany("INSERT INTO operacao (nome, descricao) VALUES (?, ?)", operacoes_padrao)
        conn.commit()
    
    conn.close()
    print("✅ Banco de dados inicializado com sucesso.")