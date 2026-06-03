#!/bin/bash

# ============================================
# PPP - RESET COMPLETO
# Apaga TODOS os dados, inclusive operações, funções, etc.
# Mantém apenas a estrutura vazia das tabelas
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${RED}       PPP - RESET COMPLETO (ZERO DADOS)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Detecta onde está o banco
if [ -f "/opt/ppp/ppp.db" ]; then
    PPP_DIR="/opt/ppp"
    DB_PATH="/opt/ppp/ppp.db"
    echo -e "${GREEN}✅ Banco encontrado em: /opt/ppp/ppp.db${NC}"
elif [ -f "$(pwd)/ppp.db" ]; then
    PPP_DIR="$(pwd)"
    DB_PATH="$(pwd)/ppp.db"
    echo -e "${GREEN}✅ Banco encontrado em: $(pwd)/ppp.db${NC}"
else
    echo -e "${RED}❌ Banco de dados não encontrado.${NC}"
    exit 1
fi

# Backup antes do reset
echo -e "${BLUE}[1/4] Fazendo backup do banco...${NC}"
BACKUP_DIR="$PPP_DIR/backups"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/ppp_backup_$(date +%Y%m%d_%H%M%S).db"
cp "$DB_PATH" "$BACKUP_FILE"
echo -e "   ✅ Backup salvo em: $BACKUP_FILE"

# Confirmação
echo ""
echo -e "${RED}⚠️  ATENÇÃO: Isso vai apagar TODOS os dados!${NC}"
echo -e "   Serão apagados:"
echo -e "   • TODAS as operações"
echo -e "   • TODOS os ambientes"
echo -e "   • TODOS os equipamentos"
echo -e "   • TODAS as funções"
echo -e "   • TODOS os colaboradores"
echo -e "   • TODAS as tarefas"
echo -e "   • TODOS os produtos e categorias"
echo -e "   • TODOS os serviços e categorias"
echo -e "   • TODAS as relações"
echo ""
echo -e "${YELLOW}⚠️  Não serão recriados dados básicos (operações, funções, etc.)${NC}"
echo -e "${YELLOW}    O banco ficará completamente vazio, apenas com a estrutura das tabelas.${NC}"
echo ""
read -p "Digite 'SIM' (maiúsculo) para confirmar: " confirmacao

if [ "$confirmacao" != "SIM" ]; then
    echo -e "${YELLOW}❌ Reset cancelado.${NC}"
    exit 0
fi

# Apagar TODOS os dados (mantém estrutura)
echo -e "${BLUE}[2/4] Apagando TODOS os dados...${NC}"

sqlite3 "$DB_PATH" << 'EOF'
-- Desabilita chaves estrangeiras temporariamente
PRAGMA foreign_keys = OFF;

-- Apaga dados de todas as tabelas (ordem correta)
DELETE FROM produto_equipamento;
DELETE FROM servico_equipamento;
DELETE FROM operacao_produto;
DELETE FROM operacao_servico;
DELETE FROM tarefa;
DELETE FROM colaborador_funcao;
DELETE FROM colaborador;
DELETE FROM produto;
DELETE FROM servico;
DELETE FROM categoria_produto;
DELETE FROM categoria_servico;
DELETE FROM equipamento;
DELETE FROM ambiente;
DELETE FROM operacao;
DELETE FROM funcao;

-- Reseta os contadores de ID
DELETE FROM sqlite_sequence;

-- Reabilita chaves estrangeiras
PRAGMA foreign_keys = ON;

SELECT '✅ Todos os dados foram apagados!' as status;
EOF

echo -e "   ✅ Todos os dados removidos"

# Opcional: perguntar se quer apagar também a tabela de unidades
echo ""
read -p "Deseja apagar também as UNIDADES (g, kg, L, etc.)? (s/N): " apagar_unidades

if [[ $apagar_unidades =~ ^[Ss]$ ]]; then
    sqlite3 "$DB_PATH" "DELETE FROM unidade; DELETE FROM sqlite_sequence WHERE name='unidade';"
    echo -e "   ✅ Unidades apagadas"
else
    echo -e "   ℹ️  Unidades mantidas"
fi

# Otimizar banco
echo -e "${BLUE}[3/4] Otimizando banco...${NC}"
sqlite3 "$DB_PATH" "VACUUM;"
echo -e "   ✅ Banco otimizado"

# Verificar estado final
echo -e "${BLUE}[4/4] Verificando estado do banco...${NC}"
echo ""
echo -e "${YELLOW}Contagem de registros:${NC}"

sqlite3 "$DB_PATH" << 'EOF'
SELECT 'operações: ' || COUNT(*) FROM operacao;
SELECT 'ambientes: ' || COUNT(*) FROM ambiente;
SELECT 'equipamentos: ' || COUNT(*) FROM equipamento;
SELECT 'funções: ' || COUNT(*) FROM funcao;
SELECT 'colaboradores: ' || COUNT(*) FROM colaborador;
SELECT 'tarefas: ' || COUNT(*) FROM tarefa;
SELECT 'produtos: ' || COUNT(*) FROM produto;
SELECT 'serviços: ' || COUNT(*) FROM servico;
SELECT 'categorias produto: ' || COUNT(*) FROM categoria_produto;
SELECT 'categorias serviço: ' || COUNT(*) FROM categoria_servico;
SELECT 'unidades: ' || COUNT(*) FROM unidade;
EOF

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}           ✅ RESET COMPLETO CONCLUÍDO!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${RED}📌 O banco está COMPLETAMENTE VAZIO!${NC}"
echo -e "${BLUE}   Nenhuma operação, função ou dado básico foi criado.${NC}"
echo -e "${BLUE}   Você precisa cadastrar tudo manualmente.${NC}"
echo ""
echo -e "${BLUE}   Para começar:${NC}"
echo -e "   • Execute ${GREEN}ppp${NC} no terminal"
echo -e "   • Cadastre as operações primeiro"
echo -e "   • Depois ambientes, funções, colaboradores..."
echo ""
echo -e "${BLUE}💾 Backup do banco anterior: ${GREEN}$BACKUP_FILE${NC}"