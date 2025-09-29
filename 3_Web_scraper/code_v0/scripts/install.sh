#!/bin/bash

echo "🎯 INSTALADOR - COLETA DE PREÇOS DE PRODUTOS"
echo "============================================"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Criar ambiente virtual (opcional)
read -p "🤔 Criar ambiente virtual? (y/n): " create_venv
if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Ambiente virtual ativado"
fi

# Instalar dependências
echo "📥 Instalando dependências Python..."
pip install -r requirements.txt

# Criar diretórios
echo "📁 Criando diretórios..."
mkdir -p data/raw_html data/exports

# Verificar instalação
echo "🧪 Testando instalação..."
python3 -c "import fastapi, uvicorn, pandas, requests; print('✅ Todas as dependências instaladas')"

echo ""
echo "🎉 INSTALAÇÃO CONCLUÍDA!"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Habilite MCP no v0.app (veja README.md)"
echo "2. Execute: python start_server.py"
echo "3. Acesse a interface no v0.app"
echo ""
