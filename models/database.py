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
    
    # ========== TABELAS EXISTENTES (mantidas) ==========
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT,
            ativo BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ambiente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            operacao_id INTEGER NOT NULL,
            descricao TEXT,
            ativo BOOLEAN DEFAULT 1,
            FOREIGN KEY (operacao_id) REFERENCES operacao (id)
        )
    ''')
    
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
            altura_mm INTEGER,
            largura_mm INTEGER,
            profundidade_mm INTEGER,
            ativo BOOLEAN DEFAULT 1,
            FOREIGN KEY (ambiente_id) REFERENCES ambiente (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS funcao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            ativo BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS colaborador (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            eh_socio BOOLEAN DEFAULT 0,
            funcao_principal_id INTEGER,
            observacao TEXT,
            ativo BOOLEAN DEFAULT 1,
            FOREIGN KEY (funcao_principal_id) REFERENCES funcao (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS colaborador_funcao (
            colaborador_id INTEGER NOT NULL,
            funcao_id INTEGER NOT NULL,
            PRIMARY KEY (colaborador_id, funcao_id),
            FOREIGN KEY (colaborador_id) REFERENCES colaborador (id),
            FOREIGN KEY (funcao_id) REFERENCES funcao (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarefa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            duracao_minutos INTEGER NOT NULL,
            frequencia_tipo TEXT NOT NULL,
            funcao_id INTEGER NOT NULL,
            colaborador_id INTEGER,
            ambiente_id INTEGER,
            equipamento_id INTEGER,
            observacao TEXT,
            ativo BOOLEAN DEFAULT 1,
            FOREIGN KEY (funcao_id) REFERENCES funcao (id),
            FOREIGN KEY (colaborador_id) REFERENCES colaborador (id),
            FOREIGN KEY (ambiente_id) REFERENCES ambiente (id),
            FOREIGN KEY (equipamento_id) REFERENCES equipamento (id)
        )
    ''')
    
    # ========== NOVAS TABELAS ==========
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS unidade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            sigla TEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL,
            sistema TEXT NOT NULL,
            fator_para_base REAL DEFAULT 1.0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categoria_produto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT,
            ativo BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categoria_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT,
            ativo BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            unidade_id INTEGER,
            quantidade_por_unidade REAL DEFAULT 1.0,
            custo_producao REAL DEFAULT 0.0,
            preco_sugerido REAL DEFAULT 0.0,
            categoria_id INTEGER,
            ativo BOOLEAN DEFAULT 1,
            FOREIGN KEY (unidade_id) REFERENCES unidade(id),
            FOREIGN KEY (categoria_id) REFERENCES categoria_produto(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            duracao_padrao_minutos INTEGER DEFAULT 0,
            custo_producao REAL DEFAULT 0.0,
            preco_sugerido REAL DEFAULT 0.0,
            categoria_id INTEGER,
            ativo BOOLEAN DEFAULT 1,
            FOREIGN KEY (categoria_id) REFERENCES categoria_servico(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operacao_produto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operacao_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            FOREIGN KEY (operacao_id) REFERENCES operacao(id),
            FOREIGN KEY (produto_id) REFERENCES produto(id),
            UNIQUE(operacao_id, produto_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operacao_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operacao_id INTEGER NOT NULL,
            servico_id INTEGER NOT NULL,
            FOREIGN KEY (operacao_id) REFERENCES operacao(id),
            FOREIGN KEY (servico_id) REFERENCES servico(id),
            UNIQUE(operacao_id, servico_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produto_equipamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            equipamento_id INTEGER NOT NULL,
            tempo_minutos INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (produto_id) REFERENCES produto(id),
            FOREIGN KEY (equipamento_id) REFERENCES equipamento(id),
            UNIQUE(produto_id, equipamento_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servico_equipamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servico_id INTEGER NOT NULL,
            equipamento_id INTEGER NOT NULL,
            tempo_minutos INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (servico_id) REFERENCES servico(id),
            FOREIGN KEY (equipamento_id) REFERENCES equipamento(id),
            UNIQUE(servico_id, equipamento_id)
        )
    ''')
    
    # ========== DADOS INICIAIS (se vazio) ==========
    
    # Unidades
    cursor.execute("SELECT COUNT(*) FROM unidade")
    if cursor.fetchone()[0] == 0:
        unidades = [
            ('grama', 'g', 'massa', 'internacional', 1.0),
            ('quilograma', 'kg', 'massa', 'internacional', 1000.0),
            ('miligrama', 'mg', 'massa', 'internacional', 0.001),
            ('litro', 'L', 'volume', 'internacional', 1.0),
            ('mililitro', 'mL', 'volume', 'internacional', 0.001),
            ('unidade', 'un', 'unidade', 'internacional', 1.0),
            ('centímetro', 'cm', 'comprimento', 'internacional', 1.0),
            ('metro', 'm', 'comprimento', 'internacional', 100.0),
            ('polegada', 'in', 'comprimento', 'imperial', 2.54),
            ('pé', 'ft', 'comprimento', 'imperial', 30.48),
            ('libra', 'lb', 'massa', 'imperial', 453.592)
        ]
        cursor.executemany("INSERT INTO unidade (nome, sigla, tipo, sistema, fator_para_base) VALUES (?, ?, ?, ?, ?)", unidades)
    
    # Categorias Produto
    cursor.execute("SELECT COUNT(*) FROM categoria_produto")
    if cursor.fetchone()[0] == 0:
        cat_prod = [
            ('Bebidas', 'Refrigerantes, águas, sucos'),
            ('Cervejas Artesanais', 'Chopes e cervejas fabricadas no local'),
            ('Petiscos', 'Porções, espetos, aperitivos'),
            ('Refeições', 'Pratos principais, lanches'),
            ('Instrumentos Musicais', 'Violões, guitarras, bateria, acessórios'),
            ('Vestuário', 'Camisetas, bonés da marca Harmony')
        ]
        cursor.executemany("INSERT INTO categoria_produto (nome, descricao) VALUES (?, ?)", cat_prod)
    
    # Categorias Serviço
    cursor.execute("SELECT COUNT(*) FROM categoria_servico")
    if cursor.fetchone()[0] == 0:
        cat_serv = [
            ('Manutenção de Instrumentos', 'Regulagem, limpeza, troca de cordas'),
            ('Costura e Ajustes', 'Barra, reforma, customização'),
            ('Aulas e Cursos', 'Música, costura, cerveja'),
            ('Eventos', 'Shows, festas, workshops')
        ]
        cursor.executemany("INSERT INTO categoria_servico (nome, descricao) VALUES (?, ?)", cat_serv)
    
    # Operações padrão (se vazio)
    cursor.execute("SELECT COUNT(*) FROM operacao")
    if cursor.fetchone()[0] == 0:
        op_padrao = [
            ('Bar', 'Operação principal com cozinha, cervejaria, salão, varanda, área kids'),
            ('Harmony', 'Loja de instrumentos musicais, palco, expositores'),
            ('Lanchonete/Café', 'Café e lanchonete no piso térreo'),
            ('Ateliê', 'Costura, manequins, provadores, depósito de tecidos')
        ]
        cursor.executemany("INSERT INTO operacao (nome, descricao) VALUES (?, ?)", op_padrao)
    
    # Funções básicas (se vazio)
    cursor.execute("SELECT COUNT(*) FROM funcao")
    if cursor.fetchone()[0] == 0:
        funcoes = [
            'Sócio Administrador', 'Sócia Gestora', 'Cozinheira(o)',
            'Atendente', 'Costureira', 'Auxiliar de Limpeza',
            'Manutenção', 'Chopeiro', 'Luthier', 'Professor(a) de Música'
        ]
        for f in funcoes:
            cursor.execute("INSERT INTO funcao (nome) VALUES (?)", (f,))
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados inicializado com sucesso.")