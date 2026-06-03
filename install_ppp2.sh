#!/bin/bash

# ============================================
# PPP2 - Palmas Project Planner
# Instalação limpa (comando: ppp2)
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}       PPP2 - Instalação${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

if [[ $EUID -ne 0 ]]; then
   echo -e "${YELLOW}⚠️  Execute com sudo: ${GREEN}sudo ./install_ppp2.sh${NC}"
   exit 1
fi

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo -e "${BLUE}📁 Diretório fonte: ${SOURCE_DIR}${NC}"

# 1. Dependências
echo -e "${BLUE}[1/5] Instalando dependências...${NC}"
pacman -S --noconfirm --needed pyside6 python-openpyxl

# 2. Diretórios
echo -e "${BLUE}[2/5] Criando diretórios...${NC}"
mkdir -p /opt/ppp2
mkdir -p /opt/ppp2/relatorios
mkdir -p /opt/ppp2/backups
mkdir -p /usr/share/icons/hicolor/256x256/apps
mkdir -p /usr/share/applications

# 3. Copiar arquivos
echo -e "${BLUE}[3/5] Copiando arquivos...${NC}"
cp -r "$SOURCE_DIR/models" "$SOURCE_DIR/views" "$SOURCE_DIR/ui" /opt/ppp2/
cp "$SOURCE_DIR/main.py" /opt/ppp2/
[ -f "$SOURCE_DIR/icon.png" ] && cp "$SOURCE_DIR/icon.png" /usr/share/icons/hicolor/256x256/apps/ppp2.png

# 4. Criar executável ppp2
echo -e "${BLUE}[4/5] Criando executável...${NC}"
cat > /usr/local/bin/ppp2 << 'EOF'
#!/bin/bash
cd /opt/ppp2
python main.py "$@"
EOF
chmod +x /usr/local/bin/ppp2

# 5. Atalho no menu
cat > /usr/share/applications/ppp2.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=PPP2 - Palmas Project Planner
Comment=Ferramenta de Viabilidade
Exec=ppp2
Icon=ppp2
Terminal=false
Categories=Office;Business;Management;
EOF

# 6. Configurar banco de dados
echo -e "${BLUE}[5/5] Configurando banco...${NC}"
cd /opt/ppp2

python -c "from models.database import init_db; init_db()" 2>/dev/null

# Migrações (adicionar colunas ativo)
sqlite3 ppp.db "ALTER TABLE operacao ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
sqlite3 ppp.db "ALTER TABLE ambiente ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
sqlite3 ppp.db "ALTER TABLE equipamento ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
sqlite3 ppp.db "ALTER TABLE funcao ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
sqlite3 ppp.db "ALTER TABLE colaborador ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
sqlite3 ppp.db "ALTER TABLE tarefa ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
sqlite3 ppp.db "ALTER TABLE equipamento ADD COLUMN altura_mm INTEGER;" 2>/dev/null
sqlite3 ppp.db "ALTER TABLE equipamento ADD COLUMN largura_mm INTEGER;" 2>/dev/null
sqlite3 ppp.db "ALTER TABLE equipamento ADD COLUMN profundidade_mm INTEGER;" 2>/dev/null

chown -R $(logname):$(logname) /opt/ppp2 2>/dev/null || chown -R 1000:1000 /opt/ppp2
chmod -R 755 /opt/ppp2

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}           ✅ INSTALAÇÃO CONCLUÍDA!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📌 Execute: ${GREEN}ppp2${NC}"
echo ""