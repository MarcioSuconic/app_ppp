-- ============================================
-- PPP - SEED DE DADOS INICIAIS
-- Operações, Ambientes, Funções e Equipamentos
-- ============================================

-- Limpa dados existentes (opcional - só executa se quiser resetar)
-- DELETE FROM tarefa;
-- DELETE FROM colaborador_funcao;
-- DELETE FROM colaborador;
-- DELETE FROM equipamento;
-- DELETE FROM ambiente;
-- DELETE FROM funcao;
-- DELETE FROM operacao;

-- ============================================
-- 1. OPERAÇÕES (já devem existir pelo init_db)
-- ============================================
INSERT OR IGNORE INTO operacao (id, nome, descricao) VALUES 
(1, 'Bar', 'Operação principal com cozinha, cervejaria, salão, varanda, área kids'),
(2, 'Harmony', 'Loja de instrumentos musicais, palco, expositores, luthieria futura'),
(3, 'Lanchonete/Café', 'Café e lanchonete no piso térreo'),
(4, 'Ateliê', 'Costura, manequins, provadores, depósito de tecidos');

-- ============================================
-- 2. AMBIENTES
-- ============================================

-- Bar (operacao_id = 1)
INSERT OR IGNORE INTO ambiente (nome, operacao_id, descricao) VALUES
('Cozinha Principal', 1, 'Preparo de petiscos, espetos e refeições do bar'),
('Cervejaria Baixo', 1, 'Espaço térreo com chopeiras e tanques de fermentação'),
('Cervejaria Cima', 1, 'Espaço superior com chopeiras premium e produção'),
('Produção de Cerveja', 1, 'Área de fabricação de cerveja artesanal'),
('Salão Bar', 1, 'Área de atendimento aos clientes, mesas e balcão'),
('Varanda dos Espetos', 1, 'Área externa com churrasqueira para espetos'),
('Área Kids', 1, 'Espaço para crianças perto do palco'),
('Banheiros', 1, 'Banheiros masculino e feminino');

-- Harmony (operacao_id = 2)
INSERT OR IGNORE INTO ambiente (nome, operacao_id, descricao) VALUES
('Palco', 2, 'Palco para música ao vivo e apresentações de alunos'),
('Expositor 1', 2, 'Parede com instrumentos pendurados + samambaia'),
('Expositor 2', 2, 'Parede com instrumentos pendurados + samambaia'),
('Expositor 3', 2, 'Parede com instrumentos pendurados + samambaia'),
('Caixa Harmony', 2, 'Balcão de atendimento e vendas de instrumentos/acessórios');

-- Lanchonete/Café (operacao_id = 3)
INSERT OR IGNORE INTO ambiente (nome, operacao_id, descricao) VALUES
('Cozinha de Apoio', 3, 'Cozinha para lanches, café e petiscos diurnos'),
('Área Clientes (térreo)', 3, 'Espaço para clientes durante o dia'),
('Balcão', 3, 'Balcão de atendimento da lanchonete/café');

-- Ateliê (operacao_id = 4)
INSERT OR IGNORE INTO ambiente (nome, operacao_id, descricao) VALUES
('Depósito de Tecidos', 4, 'Armazenamento de tecidos, linhas e aviamentos'),
('Área de Costura', 4, 'Máquinas de costura e bancada de trabalho'),
('Balcão de Atendimento', 4, 'Atendimento a clientes e retirada de peças'),
('Provadores', 4, 'Provadores para clientes experimentarem peças'),
('Manequins (vitrine_1)', 4, 'Vitrine para exposição de peças prontas'),
('Manequins (vitrine_2)', 4, 'Vitrine para exposição de peças prontas');

-- ============================================
-- 3. FUNÇÕES BÁSICAS
-- ============================================
INSERT OR IGNORE INTO funcao (id, nome) VALUES
(1, 'Sócio Administrador'),
(2, 'Sócia Gestora'),
(3, 'Cozinheira(o)'),
(4, 'Atendente'),
(5, 'Costureira'),
(6, 'Auxiliar de Limpeza'),
(7, 'Manutenção'),
(8, 'Chopeiro'),
(9, 'Luthier (futuro)'),
(10, 'Professor(a) de Música (futuro)');

-- ============================================
-- 4. COLABORADORES (exemplo - sócios)
-- ============================================
-- Os IDs vão ser gerados automaticamente
INSERT OR IGNORE INTO colaborador (nome, eh_socio, funcao_principal_id, observacao) VALUES
('Márcio Suconic', 1, 1, 'Sócio administrador, cervejeiro, luthier'),
('Esposa Márcio', 1, 2, 'Sócia gestora, responsável pela cozinha'),
('Filha Márcio', 1, 5, 'Sócia responsável pelo Ateliê de costura');

-- ============================================
-- 5. EQUIPAMENTOS BÁSICOS (exemplos)
-- ============================================
INSERT OR IGNORE INTO equipamento (nome, marca, modelo, capacidade, preco_estimado, ambiente_id, observacao) VALUES
('Chopeira 1', 'Brastemp', 'XPro', '50L', 3500.00, (SELECT id FROM ambiente WHERE nome = 'Cervejaria Baixo' LIMIT 1), 'Chopeira para cervejas normais'),
('Chopeira 2', 'Europa', 'Premium', '30L', 4500.00, (SELECT id FROM ambiente WHERE nome = 'Cervejaria Cima' LIMIT 1), 'Chopeira para cervejas especiais'),
('Fritadeira Elétrica', 'Britânia', 'Frit-3000', '10L', 800.00, (SELECT id FROM ambiente WHERE nome = 'Cozinha Principal' LIMIT 1), 'Para espetos e petiscos'),
('Geladeira Industrial', 'Consul', 'Gelar 500', '500L', 4500.00, (SELECT id FROM ambiente WHERE nome = 'Cozinha Principal' LIMIT 1), 'Armazenamento de alimentos'),
('Máquina de Costura 1', 'Singer', 'Tradição', 'Doméstica', 1200.00, (SELECT id FROM ambiente WHERE nome = 'Área de Costura' LIMIT 1), 'Uso geral'),
('Máquina de Costura Overloque', 'Juki', 'MO-1000', 'Industrial', 3500.00, (SELECT id FROM ambiente WHERE nome = 'Área de Costura' LIMIT 1), 'Acabamento de peças'),
('Caixa Registradora', 'Elgin', 'CX-500', 'Digital', 1200.00, (SELECT id FROM ambiente WHERE nome = 'Balcão' LIMIT 1), 'Para lanchonete/café'),
('Vitrine Manequins', 'Genérica', 'Vidro Temperado', '2m', 800.00, (SELECT id FROM ambiente WHERE nome = 'Manequins (vitrine_1)' LIMIT 1), 'Exposição de peças');

-- ============================================
-- 6. TAREFAS EXEMPLO (para teste)
-- ============================================
INSERT OR IGNORE INTO tarefa (nome, duracao_minutos, frequencia_tipo, funcao_id, ambiente_id, equipamento_id, observacao) VALUES
-- Tarefas do Bar
('Limpeza das chopeiras', 30, 'diaria', 6, (SELECT id FROM ambiente WHERE nome = 'Cervejaria Baixo' LIMIT 1), (SELECT id FROM equipamento WHERE nome = 'Chopeira 1' LIMIT 1), 'Antes de abrir'),
('Troca de óleo da fritadeira', 20, 'semanal', 3, (SELECT id FROM ambiente WHERE nome = 'Cozinha Principal' LIMIT 1), (SELECT id FROM equipamento WHERE nome = 'Fritadeira Elétrica' LIMIT 1), 'Toda segunda-feira'),
('Limpeza da área kids', 30, 'diaria', 6, (SELECT id FROM ambiente WHERE nome = 'Área Kids' LIMIT 1), NULL, 'Desinfetar brinquedos e tapetes'),
('Preparo de espetos', 120, 'diaria', 3, (SELECT id FROM ambiente WHERE nome = 'Varanda dos Espetos' LIMIT 1), NULL, 'Preparar espetos para o dia'),

-- Tarefas da Harmony
('Limpeza de instrumentos expositores', 45, 'semanal', 9, (SELECT id FROM ambiente WHERE nome = 'Expositor 1' LIMIT 1), NULL, 'Tirar poeira e polir'),
('Rega das samambaias', 15, 'semanal', 6, (SELECT id FROM ambiente WHERE nome = 'Expositor 1' LIMIT 1), NULL, 'Regar todas as samambaias dos expositores'),
('Organização do palco', 30, 'diaria', 6, (SELECT id FROM ambiente WHERE nome = 'Palco' LIMIT 1), NULL, 'Deixar instrumentos prontos para alunos'),

-- Tarefas da Lanchonete/Café
('Limpeza da cozinha de apoio', 45, 'diaria', 6, (SELECT id FROM ambiente WHERE nome = 'Cozinha de Apoio' LIMIT 1), NULL, 'Após o fechamento'),
('Preparo de café', 60, 'diaria', 3, (SELECT id FROM ambiente WHERE nome = 'Balcão' LIMIT 1), NULL, 'Manhã'),

-- Tarefas do Ateliê
('Lubrificação das máquinas de costura', 15, 'mensal', 5, (SELECT id FROM ambiente WHERE nome = 'Área de Costura' LIMIT 1), (SELECT id FROM equipamento WHERE nome = 'Máquina de Costura 1' LIMIT 1), 'Dia 15 de cada mês'),
('Organização do depósito de tecidos', 60, 'semanal', 5, (SELECT id FROM ambiente WHERE nome = 'Depósito de Tecidos' LIMIT 1), NULL, 'Manter tecidos organizados por tipo');

-- ============================================
-- 7. RELATÓRIO DE INSERÇÃO
-- ============================================
SELECT '========================================' AS '';
SELECT 'PPP - DADOS INSERIDOS COM SUCESSO!' AS '';
SELECT '========================================' AS '';
SELECT 'Operações: ' || (SELECT COUNT(*) FROM operacao) AS '';
SELECT 'Ambientes: ' || (SELECT COUNT(*) FROM ambiente) AS '';
SELECT 'Funções: ' || (SELECT COUNT(*) FROM funcao) AS '';
SELECT 'Colaboradores: ' || (SELECT COUNT(*) FROM colaborador) AS '';
SELECT 'Equipamentos: ' || (SELECT COUNT(*) FROM equipamento) AS '';
SELECT 'Tarefas: ' || (SELECT COUNT(*) FROM tarefa) AS '';
SELECT '========================================' AS '';