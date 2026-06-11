-- ============================================
-- PPP - MIGRAÇÃO: Marcas, Ferramentas e Tipos
-- (Executar este arquivo com: sqlite3 ppp.db < migrate_add_ferramentas.sql)
-- ============================================

-- 1. CRIAR TABELAS NOVAS
CREATE TABLE IF NOT EXISTS marca (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tipo_ferramenta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS ferramenta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT NOT NULL,
    tipo_ferramenta_id INTEGER NOT NULL,
    marca_id INTEGER,
    valor_compra REAL DEFAULT 0.0,
    data_compra TEXT,
    ambiente_id INTEGER,
    observacao TEXT,
    ativo BOOLEAN DEFAULT 1,
    FOREIGN KEY (tipo_ferramenta_id) REFERENCES tipo_ferramenta(id),
    FOREIGN KEY (marca_id) REFERENCES marca(id),
    FOREIGN KEY (ambiente_id) REFERENCES ambiente(id)
);

-- 2. MIGRAR MARCAS DOS EQUIPAMENTOS (EVITANDO DUPLICIDADE)
INSERT OR IGNORE INTO marca (nome)
SELECT DISTINCT TRIM(marca) FROM equipamento WHERE marca IS NOT NULL AND TRIM(marca) != '';

-- 3. ADICIONAR COLUNA `marca_id` NA TABELA `equipamento`
ALTER TABLE equipamento ADD COLUMN marca_id INTEGER REFERENCES marca(id);

-- 4. ATUALIZAR OS `marca_id` COM BASE NA TABELA `marca`
UPDATE equipamento SET marca_id = (SELECT id FROM marca WHERE marca.nome = TRIM(equipamento.marca))
WHERE equipamento.marca IS NOT NULL AND TRIM(equipamento.marca) != '';

-- 5. INSERIR ALGUNS TIPOS DE FERRAMENTA PADRÃO (SE A TABELA ESTIVER VAZIA)
INSERT OR IGNORE INTO tipo_ferramenta (nome) VALUES 
('Corte (tesoura, estilete)'),
('Cozinha (colheres, espátulas)'),
('Manutenção (chaves, alicates)'),
('Costura (agulhas, dedais)');

SELECT '✅ Migração de Marcas e Ferramentas concluída!' AS status;