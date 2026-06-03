#!/bin/bash

# ============================================
# PPP - RESET TOTAL
# Remove o banco e recria a estrutura do zero
# ============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${RED}       PPP - RESET TOTAL (RECRIA BANCO DO ZERO)${NC}"
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
echo -e "${RED}⚠️  ATENÇÃO: Isso vai APAGAR E RECRIAR o banco de dados!${NC}"
echo -e "   • Banco atual será deletado"
echo -e "   • Novo banco será criado com estrutura vazia"
echo -e "   • Nenhum dado será mantido"
echo ""
read -p "Digite 'SIM' (maiúsculo) para confirmar: " confirmacao

if [ "$confirmacao" != "SIM" ]; then
    echo -e "${YELLOW}❌ Reset cancelado.${NC}"
    exit 0
fi

# Deletar o banco antigo
echo -e "${BLUE}[2/4] Deletando banco antigo...${NC}"
rm -f "$DB_PATH"
echo -e "   ✅ Banco deletado"

# Recriar banco com estrutura
echo -e "${BLUE}[3/4] Recriando banco com estrutura vazia...${NC}"
cd "$PPP_DIR"
python -c "from models.database import init_db; init_db()" 2>/dev/null || echo "   ⚠️  init_db falhou, tentando import manual..."

# Verificar se o banco foi criado
if [ -f "$DB_PATH" ]; then
    echo -e "   ✅ Banco recriado com sucesso"
else
    echo -e "${RED}❌ Falha ao recriar banco${NC}"
    exit 1
fi

# Otimizar
echo -e "${BLUE}[4/4] Otimizando banco...${NC}"
sqlite3 "$DB_PATH" "VACUUM;" 2>/dev/null || true
echo -e "   ✅ Banco otimizado"

# Verificar estado final
echo ""
echo -e "${YELLOW}Estrutura do banco (tabelas vazias):${NC}"
sqlite3 "$DB_PATH" ".tables"

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}           ✅ RESET TOTAL CONCLUÍDO!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📌 O banco está completamente vazio, mas com estrutura pronta.${NC}"
echo -e "${BLUE}   Para começar a cadastrar:${NC}"
echo -e "   • Execute ${GREEN}python main.py${NC} na pasta do projeto"
echo ""
echo -e "${BLUE}💾 Backup do banco anterior: ${GREEN}$BACKUP_FILE${NC}"