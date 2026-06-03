#!/bin/bash

# ============================================
# PPP2 - RESET TOTAL
# Apaga banco e recria estrutura limpa
# ============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${RED}       PPP2 - RESET TOTAL (ZERO DADOS)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Detecta diretório
if [ -f "/opt/ppp2/main.py" ]; then
    PPP_DIR="/opt/ppp2"
elif [ -f "$(pwd)/main.py" ]; then
    PPP_DIR="$(pwd)"
else
    echo -e "${RED}❌ PPP2 não encontrado${NC}"
    exit 1
fi

DB_PATH="$PPP_DIR/ppp.db"
echo -e "${BLUE}📁 Banco: ${DB_PATH}${NC}"

# Backup
echo -e "${BLUE}[1/3] Backup...${NC}"
BACKUP_DIR="$PPP_DIR/backups"
mkdir -p "$BACKUP_DIR"
cp "$DB_PATH" "$BACKUP_DIR/ppp2_backup_$(date +%Y%m%d_%H%M%S).db"
echo -e "   ✅ Backup criado"

# Confirmação
echo ""
read -p "Digite 'SIM' para apagar TODOS os dados: " confirmacao
if [ "$confirmacao" != "SIM" ]; then
    echo -e "${YELLOW}❌ Cancelado${NC}"
    exit 0
fi

# Reset
echo -e "${BLUE}[2/3] Apagando dados...${NC}"
sqlite3 "$DB_PATH" << 'EOF'
PRAGMA foreign_keys = OFF;
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
DELETE FROM sqlite_sequence;
PRAGMA foreign_keys = ON;
EOF
echo -e "   ✅ Dados removidos"

# Recriar estrutura básica
echo -e "${BLUE}[3/3] Recriando estrutura...${NC}"
python -c "from models.database import init_db; init_db()" 2>/dev/null

# Migrações
sqlite3 "$DB_PATH" "ALTER TABLE operacao ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
sqlite3 "$DB_PATH" "ALTER TABLE ambiente ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
sqlite3 "$DB_PATH" "ALTER TABLE equipamento ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
sqlite3 "$DB_PATH" "ALTER TABLE funcao ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
sqlite3 "$DB_PATH" "ALTER TABLE colaborador ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
sqlite3 "$DB_PATH" "ALTER TABLE tarefa ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
sqlite3 "$DB_PATH" "ALTER TABLE equipamento ADD COLUMN altura_mm INTEGER;" 2>/dev/null
sqlite3 "$DB_PATH" "ALTER TABLE equipamento ADD COLUMN largura_mm INTEGER;" 2>/dev/null
sqlite3 "$DB_PATH" "ALTER TABLE equipamento ADD COLUMN profundidade_mm INTEGER;" 2>/dev/null

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}           ✅ RESET CONCLUÍDO!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📌 Execute: ${GREEN}ppp2${NC}"