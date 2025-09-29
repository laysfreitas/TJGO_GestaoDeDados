#!/bin/bash

echo "🔍 VERIFICADOR DE SERVIDOR - COLETA DE PREÇOS"
echo "============================================="

# Verificar se o servidor está rodando
echo "📡 Testando conexão com servidor FastAPI..."

if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Servidor FastAPI está rodando em http://localhost:8000"
    
    # Testar endpoints principais
    echo ""
    echo "🧪 Testando endpoints principais:"
    
    # Status
    if curl -s http://localhost:8000/api/status > /dev/null 2>&1; then
        echo "  ✅ /api/status - OK"
    else
        echo "  ❌ /api/status - ERRO"
    fi
    
    # Produtos
    if curl -s http://localhost:8000/api/produtos > /dev/null 2>&1; then
        echo "  ✅ /api/produtos - OK"
    else
        echo "  ❌ /api/produtos - ERRO"
    fi
    
    # Câmbio
    if curl -s http://localhost:8000/api/cambio > /dev/null 2>&1; then
        echo "  ✅ /api/cambio - OK"
    else
        echo "  ⚠️  /api/cambio - Sem dados (normal se não houve coleta)"
    fi
    
    echo ""
    echo "🎉 Servidor funcionando corretamente!"
    
else
    echo "❌ Servidor FastAPI não está respondendo"
    echo ""
    echo "💡 Para iniciar o servidor:"
    echo "   python start_server.py"
    echo "   ou"
    echo "   python main.py"
    echo ""
    echo "🔧 Verifique se:"
    echo "   • Python está instalado"
    echo "   • Dependências estão instaladas (pip install -r requirements.txt)"
    echo "   • Porta 8000 não está sendo usada por outro processo"
fi

echo ""
echo "📋 Logs do servidor (se estiver rodando):"
echo "   Verifique o terminal onde executou 'python main.py'"
