sql-- ============================================
-- PPP - MIGRAÇÃO COMPLETA
-- Adiciona categorias, produtos, serviços, unidades
-- Adiciona campo ativo em várias tabelas
-- ============================================

-- ============================================
-- 1. TABELA DE UNIDADES (base para conversões futuras)
-- ============================================
CREATE TABLE IF NOT EXISTS unidade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    sigla TEXT NOT NULL UNIQUE,
    tipo TEXT NOT NULL,
    sistema TEXT NOT NULL,
    fator_para_base REAL DEFAULT 1.0
);

INSERT OR IGNORE INTO unidade (nome, sigla, tipo, sistema, fator_para_base) VALUES
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
('libra', 'lb', 'massa', 'imperial', 453.592);

-- ============================================
-- 2. CATEGORIAS
-- ============================================
CREATE TABLE IF NOT EXISTS categoria_produto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT,
    ativo BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS categoria_servico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT,
    ativo BOOLEAN DEFAULT 1
);

INSERT OR IGNORE INTO categoria_produto (nome, descricao) VALUES
('Bebidas', 'Refrigerantes, águas, sucos'),
('Cervejas Artesanais', 'Chopes e cervejas fabricadas no local'),
('Petiscos', 'Porções, espetos, aperitivos'),
('Refeições', 'Pratos principais, lanches'),
('Instrumentos Musicais', 'Violões, guitarras, bateria, acessórios'),
('Vestuário', 'Camisetas, bonés da marca Harmony');

INSERT OR IGNORE INTO categoria_servico (nome, descricao) VALUES
('Manutenção de Instrumentos', 'Regulagem, limpeza, troca de cordas'),
('Costura e Ajustes', 'Barra, reforma, customização'),
('Aulas e Cursos', 'Música, costura, cerveja'),
('Eventos', 'Shows, festas, workshops');

-- ============================================
-- 3. PRODUTOS
-- ============================================
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
);

-- ============================================
-- 4. SERVIÇOS
-- ============================================
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
);

-- ============================================
-- 5. RELAÇÕES OPERAÇÃO x PRODUTO / SERVIÇO
-- ============================================
CREATE TABLE IF NOT EXISTS operacao_produto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operacao_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    FOREIGN KEY (operacao_id) REFERENCES operacao(id),
    FOREIGN KEY (produto_id) REFERENCES produto(id),
    UNIQUE(operacao_id, produto_id)
);

CREATE TABLE IF NOT EXISTS operacao_servico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operacao_id INTEGER NOT NULL,
    servico_id INTEGER NOT NULL,
    FOREIGN KEY (operacao_id) REFERENCES operacao(id),
    FOREIGN KEY (servico_id) REFERENCES servico(id),
    UNIQUE(operacao_id, servico_id)
);

-- ============================================
-- 6. RELAÇÕES PRODUTO/SERVIÇO x EQUIPAMENTO
-- ============================================
CREATE TABLE IF NOT EXISTS produto_equipamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    equipamento_id INTEGER NOT NULL,
    tempo_minutos INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (produto_id) REFERENCES produto(id),
    FOREIGN KEY (equipamento_id) REFERENCES equipamento(id),
    UNIQUE(produto_id, equipamento_id)
);

CREATE TABLE IF NOT EXISTS servico_equipamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    servico_id INTEGER NOT NULL,
    equipamento_id INTEGER NOT NULL,
    tempo_minutos INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (servico_id) REFERENCES servico(id),
    FOREIGN KEY (equipamento_id) REFERENCES equipamento(id),
    UNIQUE(servico_id, equipamento_id)
);

-- ============================================
-- 7. ADICIONAR CAMPO "ativo" EM TABELAS EXISTENTES
-- ============================================
ALTER TABLE operacao ADD COLUMN ativo BOOLEAN DEFAULT 1;
ALTER TABLE ambiente ADD COLUMN ativo BOOLEAN DEFAULT 1;
ALTER TABLE equipamento ADD COLUMN ativo BOOLEAN DEFAULT 1;
ALTER TABLE funcao ADD COLUMN ativo BOOLEAN DEFAULT 1;
ALTER TABLE colaborador ADD COLUMN ativo BOOLEAN DEFAULT 1;
ALTER TABLE tarefa ADD COLUMN ativo BOOLEAN DEFAULT 1;

-- ============================================
-- 8. ADICIONAR CAMPOS DE DIMENSÃO EM EQUIPAMENTO
-- ============================================
ALTER TABLE equipamento ADD COLUMN altura_mm INTEGER;
ALTER TABLE equipamento ADD COLUMN largura_mm INTEGER;
ALTER TABLE equipamento ADD COLUMN profundidade_mm INTEGER;

-- ============================================
-- 9. ÍNDICES PARA PERFORMANCE
-- ============================================
CREATE INDEX IF NOT EXISTS idx_produto_categoria ON produto(categoria_id);
CREATE INDEX IF NOT EXISTS idx_servico_categoria ON servico(categoria_id);
CREATE INDEX IF NOT EXISTS idx_operacao_produto ON operacao_produto(operacao_id, produto_id);
CREATE INDEX IF NOT EXISTS idx_operacao_servico ON operacao_servico(operacao_id, servico_id);
CREATE INDEX IF NOT EXISTS idx_produto_equipamento ON produto_equipamento(produto_id);
CREATE INDEX IF NOT EXISTS idx_servico_equipamento ON servico_equipamento(servico_id);

-- ============================================
-- 10. VERIFICAR TUDO
-- ============================================
SELECT '✅ Migração concluída!' AS status;
SELECT 'unidades: ' || COUNT(*) FROM unidade;
SELECT 'categorias produto: ' || COUNT(*) FROM categoria_produto;
SELECT 'categorias serviço: ' || COUNT(*) FROM categoria_servico;