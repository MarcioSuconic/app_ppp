#!/bin/bash

echo "════════════════════════════════════════════════════════════"
echo "          PPP - RESET COMPLETO DO SISTEMA"
echo "════════════════════════════════════════════════════════════"
echo ""

# Remove o banco de dados
if [ -f "ppp.db" ]; then
    echo "🗑️  Removendo banco de dados ppp.db..."
    rm ppp.db
else
    echo "ℹ️  Banco de dados não encontrado."
fi

# Remove a pasta de relatórios
if [ -d "relatorios" ]; then
    echo "🗑️  Removendo pasta de relatórios..."
    rm -rf relatorios
else
    echo "ℹ️  Pasta de relatórios não encontrada."
fi

# Remove arquivos de cache do Python
echo "🗑️  Removendo cache do Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

echo ""
echo "════════════════════════════════════════════════════════════"
echo "          ✅ RESET CONCLUÍDO! Banco de dados limpo."
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Para recomeçar, execute: python main.py"