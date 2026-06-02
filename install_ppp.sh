#!/bin/bash

# ============================================
# PPP - Palmas Project Planner
# Script de instalação para Arch Linux
# ============================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}       PPP - Palmas Project Planner - Instalação${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

if [[ $EUID -ne 0 ]]; then
   echo -e "${YELLOW}⚠️  Este script precisa ser executado como root (sudo).${NC}"
   echo -e "   Execute: ${GREEN}sudo ./install_ppp.sh${NC}"
   exit 1
fi

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo -e "${BLUE}📁 Diretório fonte: ${SOURCE_DIR}${NC}"

# ============================================
# 1. Instalar dependências do sistema (CORRIGIDO)
# ============================================
echo -e "${BLUE}[1/6] Instalando dependências do sistema...${NC}"
# No Arch: pyside6 (não python-pyside6)
sudo pacman -S --noconfirm --needed pyside6 python-openpyxl

# ============================================
# 2. Criar diretórios
# ============================================
echo -e "${BLUE}[2/6] Criando diretórios...${NC}"
sudo mkdir -p /opt/ppp
sudo mkdir -p /opt/ppp/relatorios
sudo mkdir -p /opt/ppp/backups
sudo mkdir -p /usr/share/icons/hicolor/256x256/apps
sudo mkdir -p /usr/share/applications

# ============================================
# 3. Copiar arquivos do projeto
# ============================================
echo -e "${BLUE}[3/6] Copiando arquivos do projeto...${NC}"

DIRS_TO_COPY="models views ui"
FILES_TO_COPY="main.py seed_ppp.sql"

for dir in $DIRS_TO_COPY; do
    if [ -d "$SOURCE_DIR/$dir" ]; then
        sudo cp -r "$SOURCE_DIR/$dir" /opt/ppp/
        echo -e "   ✅ Copiado: $dir/"
    else
        echo -e "   ${YELLOW}⚠️  Pasta não encontrada: $dir/${NC}"
    fi
done

for file in $FILES_TO_COPY; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        sudo cp "$SOURCE_DIR/$file" /opt/ppp/
        echo -e "   ✅ Copiado: $file"
    else
        echo -e "   ${YELLOW}⚠️  Arquivo não encontrado: $file${NC}"
    fi
done

# Copiar ícone se existir
if [ -f "$SOURCE_DIR/icon.png" ]; then
    sudo cp "$SOURCE_DIR/icon.png" /usr/share/icons/hicolor/256x256/apps/ppp.png
    echo -e "   ✅ Copiado: ícone"
fi

# ============================================
# 4. Criar executável global
# ============================================
echo -e "${BLUE}[4/6] Criando executável global...${NC}"
sudo tee /usr/local/bin/ppp > /dev/null << 'EOF'
#!/bin/bash
cd /opt/ppp
python main.py "$@"
EOF

sudo chmod +x /usr/local/bin/ppp

# ============================================
# 5. Criar atalho no menu
# ============================================
echo -e "${BLUE}[5/6] Criando atalho no menu...${NC}"
sudo tee /usr/share/applications/ppp.desktop > /dev/null << 'EOF'
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

# ============================================
# 6. Configurar banco de dados
# ============================================
echo -e "${BLUE}[6/6] Configurando banco de dados...${NC}"

cd /opt/ppp

if [ ! -f "/opt/ppp/ppp.db" ]; then
    echo -e "   ${YELLOW}Criando banco de dados...${NC}"
    python -c "from models.database import init_db; init_db()" 2>/dev/null || true
fi

if [ -f "/opt/ppp/seed_ppp.sql" ] && [ ! -f "/opt/ppp/ppp.db" ]; then
    echo -e "   ${YELLOW}Aplicando seed...${NC}"
    sqlite3 /opt/ppp/ppp.db < /opt/ppp/seed_ppp.sql 2>/dev/null || true
fi

# Backup inicial
cp /opt/ppp/ppp.db "/opt/ppp/backups/ppp_backup_$(date +%Y%m%d_%H%M%S).db" 2>/dev/null || true

# Ajustar permissões
chown -R $(logname):$(logname) /opt/ppp 2>/dev/null || chown -R 1000:1000 /opt/ppp
chmod -R 755 /opt/ppp

# ============================================
# Finalizar
# ============================================
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}           ✅ INSTALAÇÃO CONCLUÍDA!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📌 Para executar o PPP:${NC}"
echo -e "   • Menu de aplicações → ${GREEN}PPP - Palmas Project Planner${NC}"
echo -e "   • No terminal: ${GREEN}ppp${NC}"
echo ""
echo -e "${BLUE}📂 Arquivos instalados em: ${GREEN}/opt/ppp/${NC}"
echo -e "${BLUE}🗄️  Backups: ${GREEN}/opt/ppp/backups/${NC}"
echo ""

read -p "Deseja executar o PPP agora? (s/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${GREEN}▶️  Iniciando PPP...${NC}"
    sudo -u $(logname) /usr/local/bin/ppp &
fi