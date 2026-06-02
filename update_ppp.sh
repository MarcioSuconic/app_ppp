#!/bin/bash

# ============================================
# PPP - Atualização do Sistema
# Executar após dar git pull
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}       PPP - Atualização do Sistema${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

if [[ $EUID -ne 0 ]]; then
   echo -e "${YELLOW}⚠️  Execute com sudo: ${GREEN}sudo ./update_ppp.sh${NC}"
   exit 1
fi

# ============================================
# 1. Parar o app se estiver rodando
# ============================================
echo -e "${BLUE}[1/5] Parando instâncias do PPP...${NC}"
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "/usr/local/bin/ppp" 2>/dev/null || true
sleep 1

# ============================================
# 2. Fazer backup do banco antes de qualquer alteração
# ============================================
echo -e "${BLUE}[2/5] Fazendo backup do banco de dados...${NC}"
if [ -f "/opt/ppp/ppp.db" ]; then
    BACKUP_DIR="/opt/ppp/backups"
    mkdir -p $BACKUP_DIR
    cp "/opt/ppp/ppp.db" "$BACKUP_DIR/ppp_backup_$(date +%Y%m%d_%H%M%S).db"
    echo -e "   ✅ Backup criado"
fi

# ============================================
# 3. Atualizar arquivos do repositório
# ============================================
echo -e "${BLUE}[3/5] Atualizando arquivos...${NC}"

# Se estiver dentro do repositório git
if [ -d "/opt/ppp/.git" ]; then
    cd /opt/ppp
    git pull
else
    echo -e "   ${YELLOW}Repositório não encontrado. Copiando arquivos da fonte...${NC}"
    SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ -d "$SOURCE_DIR" ]; then
        cp -r "$SOURCE_DIR/models" "$SOURCE_DIR/views" "$SOURCE_DIR/ui" "$SOURCE_DIR/main.py" "$SOURCE_DIR/seed_ppp.sql" /opt/ppp/ 2>/dev/null || true
    fi
fi

# ============================================
# 4. Aplicar migrações no banco de dados
# ============================================
echo -e "${BLUE}[4/5] Aplicando migrações...${NC}"
cd /opt/ppp

# Migração 1: coluna colaborador_id na tabela tarefa
sqlite3 ppp.db "ALTER TABLE tarefa ADD COLUMN colaborador_id INTEGER REFERENCES colaborador(id);" 2>/dev/null && echo "   ✅ Coluna 'colaborador_id' adicionada" || echo "   ✅ Coluna 'colaborador_id' já existe"

# Migração 2: índice para colaborador_id
sqlite3 ppp.db "CREATE INDEX IF NOT EXISTS idx_tarefa_colaborador ON tarefa(colaborador_id);" 2>/dev/null && echo "   ✅ Índice criado"

# Migração 3: (futura) adicione aqui novas migrações

# ============================================
# 5. Atualizar executável global
# ============================================
echo -e "${BLUE}[5/5] Atualizando executável...${NC}"
cat > /usr/local/bin/ppp << 'EOF'
#!/bin/bash
cd /opt/ppp
python main.py "$@"
EOF
chmod +x /usr/local/bin/ppp

# ============================================
# Finalizar
# ============================================
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}           ✅ ATUALIZAÇÃO CONCLUÍDA!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📌 Para executar o PPP:${NC}"
echo -e "   • Menu de aplicações → ${GREEN}PPP - Palmas Project Planner${NC}"
echo -e "   • No terminal: ${GREEN}ppp${NC}"
echo ""
echo -e "${BLUE}🗄️  Backup salvo em: ${GREEN}/opt/ppp/backups/${NC}"
echo ""