#!/bin/bash

# ============================================
# PPP2 - Atualização do Sistema
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}       PPP2 - Atualização${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

if [[ $EUID -ne 0 ]]; then
   echo -e "${YELLOW}⚠️  Execute com sudo: ${GREEN}sudo ./update_ppp2.sh${NC}"
   exit 1
fi

# Detecta diretório do projeto
if [ -f "/opt/ppp2/main.py" ]; then
    PPP_DIR="/opt/ppp2"
elif [ -f "$(pwd)/main.py" ]; then
    PPP_DIR="$(pwd)"
else
    echo -e "${RED}❌ PPP2 não encontrado${NC}"
    exit 1
fi

echo -e "${BLUE}📁 Diretório: ${PPP_DIR}${NC}"

# Backup
echo -e "${BLUE}[1/5] Backup do banco...${NC}"
BACKUP_DIR="$PPP_DIR/backups"
mkdir -p "$BACKUP_DIR"
if [ -f "$PPP_DIR/ppp.db" ]; then
    cp "$PPP_DIR/ppp.db" "$BACKUP_DIR/ppp2_backup_$(date +%Y%m%d_%H%M%S).db"
    echo -e "   ✅ Backup criado"
fi

# Atualizar código
echo -e "${BLUE}[2/5] Atualizando código...${NC}"
if [ -d "$PPP_DIR/.git" ]; then
    cd "$PPP_DIR"
    git pull
else
    SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cp -r "$SOURCE_DIR/models" "$SOURCE_DIR/views" "$SOURCE_DIR/ui" "$SOURCE_DIR/main.py" "$PPP_DIR/"
fi

# Migrações automáticas
echo -e "${BLUE}[3/5] Aplicando migrações...${NC}"
cd "$PPP_DIR"

# Verifica se o banco existe
if [ -f "$PPP_DIR/ppp.db" ]; then
    # Adiciona coluna potencia na tabela equipamento (se não existir)
    sqlite3 ppp.db "ALTER TABLE equipamento ADD COLUMN potencia INTEGER DEFAULT 0;" 2>/dev/null && echo "   ✅ Coluna 'potencia' adicionada" || echo "   ✅ Coluna 'potencia' já existe"
    
    # Adiciona coluna tipo_energia na tabela equipamento (se não existir)
    sqlite3 ppp.db "ALTER TABLE equipamento ADD COLUMN tipo_energia TEXT DEFAULT 'elétrica';" 2>/dev/null && echo "   ✅ Coluna 'tipo_energia' adicionada" || echo "   ✅ Coluna 'tipo_energia' já existe"
    
    # Adiciona coluna ativo nas tabelas (se não existirem)
    sqlite3 ppp.db "ALTER TABLE operacao ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
    sqlite3 ppp.db "ALTER TABLE ambiente ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
    sqlite3 ppp.db "ALTER TABLE equipamento ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
    sqlite3 ppp.db "ALTER TABLE funcao ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
    sqlite3 ppp.db "ALTER TABLE colaborador ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
    sqlite3 ppp.db "ALTER TABLE tarefa ADD COLUMN ativo BOOLEAN DEFAULT 1;" 2>/dev/null
    
    # Adiciona colunas de dimensão (se não existirem)
    sqlite3 ppp.db "ALTER TABLE equipamento ADD COLUMN altura_mm INTEGER;" 2>/dev/null
    sqlite3 ppp.db "ALTER TABLE equipamento ADD COLUMN largura_mm INTEGER;" 2>/dev/null
    sqlite3 ppp.db "ALTER TABLE equipamento ADD COLUMN profundidade_mm INTEGER;" 2>/dev/null
    
    echo -e "   ✅ Migrações aplicadas"
else
    echo -e "   ${YELLOW}⚠️  Banco de dados não encontrado. Execute install_ppp2.sh primeiro${NC}"
fi

# Atualizar executável
echo -e "${BLUE}[4/5] Atualizando executável...${NC}"
cat > /usr/local/bin/ppp2 << EOF
#!/bin/bash
cd $PPP_DIR
python main.py "\$@"
EOF
chmod +x /usr/local/bin/ppp2

# Atualizar atalho no menu
echo -e "${BLUE}[5/5] Atualizando atalho no menu...${NC}"
cat > /usr/share/applications/ppp2.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=PPP2 - Palmas Project Planner
Comment=Ferramenta de Viabilidade
Exec=ppp2
Icon=ppp2
Terminal=false
Categories=Office;Business;Management;
StartupNotify=true
EOF

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}           ✅ ATUALIZAÇÃO CONCLUÍDA!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📌 Execute: ${GREEN}ppp2${NC}"