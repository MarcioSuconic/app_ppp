#!/bin/bash

# ============================================
# PPP - Atualização do Sistema
# Detecta automaticamente onde está instalado
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

# Detecta onde está o projeto
if [ -f "/opt/ppp/main.py" ]; then
    PPP_DIR="/opt/ppp"
    echo -e "${GREEN}✅ Sistema detectado em: /opt/ppp (instalação completa)${NC}"
elif [ -f "$(pwd)/main.py" ]; then
    PPP_DIR="$(pwd)"
    echo -e "${YELLOW}⚠️  Rodando no diretório atual: $PPP_DIR (modo desenvolvedor)${NC}"
else
    echo -e "${RED}❌ Não foi possível localizar o PPP.${NC}"
    exit 1
fi

if [[ $EUID -ne 0 ]]; then
   echo -e "${YELLOW}⚠️  Execute com sudo: ${GREEN}sudo ./update_ppp.sh${NC}"
   exit 1
fi

# 1. Parar o app
echo -e "${BLUE}[1/6] Parando instâncias do PPP...${NC}"
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "/usr/local/bin/ppp" 2>/dev/null || true
sleep 1

# 2. Backup do banco
echo -e "${BLUE}[2/6] Fazendo backup do banco de dados...${NC}"
if [ -f "$PPP_DIR/ppp.db" ]; then
    BACKUP_DIR="$PPP_DIR/backups"
    mkdir -p $BACKUP_DIR
    cp "$PPP_DIR/ppp.db" "$BACKUP_DIR/ppp_backup_$(date +%Y%m%d_%H%M%S).db"
    echo -e "   ✅ Backup criado"
fi

# 3. Atualizar arquivos
echo -e "${BLUE}[3/6] Atualizando arquivos...${NC}"
if [ "$PPP_DIR" == "/opt/ppp" ] && [ -d "/opt/ppp/.git" ]; then
    cd /opt/ppp
    git pull
else
    SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ -d "$SOURCE_DIR" ]; then
        cp -r "$SOURCE_DIR/models" "$SOURCE_DIR/views" "$SOURCE_DIR/ui" "$SOURCE_DIR/main.py" "$SOURCE_DIR/seed_ppp.sql" "$PPP_DIR/" 2>/dev/null || true
        echo -e "   ✅ Arquivos copiados"
    fi
fi

# 4. Rodar migração SQL (se existir)
echo -e "${BLUE}[4/6] Aplicando migrações...${NC}"
cd "$PPP_DIR"
if [ -f "migrate_ppp.sql" ]; then
    sqlite3 ppp.db < migrate_ppp.sql 2>/dev/null || echo "   ⚠️  Migração já aplicada ou erro menor"
else
    echo "   ⚠️  Arquivo migrate_ppp.sql não encontrado"
fi

# 5. Atualizar executável global
echo -e "${BLUE}[5/6] Atualizando executável...${NC}"
cat > /usr/local/bin/ppp << EOF
#!/bin/bash
cd $PPP_DIR
python main.py "\$@"
EOF
chmod +x /usr/local/bin/ppp

# 6. Atualizar atalho no menu
echo -e "${BLUE}[6/6] Atualizando atalho no menu...${NC}"
cat > /usr/share/applications/ppp.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=PPP - Palmas Project Planner
Comment=Ferramenta de Viabilidade do Negócio
Exec=ppp
Icon=ppp
Terminal=false
Categories=Office;Business;Management;
StartupNotify=true
EOF

if [ -f "$PPP_DIR/icon.png" ]; then
    sudo cp "$PPP_DIR/icon.png" /usr/share/icons/hicolor/256x256/apps/ppp.png 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}           ✅ ATUALIZAÇÃO CONCLUÍDA!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📌 Para executar o PPP:${NC}"
echo -e "   • Menu de aplicações → ${GREEN}PPP - Palmas Project Planner${NC}"
echo -e "   • No terminal: ${GREEN}ppp${NC}"