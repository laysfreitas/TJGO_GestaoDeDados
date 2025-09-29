#!/usr/bin/env python3
"""
Script de inicialização do servidor FastAPI para Coleta de Preços
Facilita o processo de inicialização e verificação do ambiente
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    try:
        import fastapi
        import uvicorn
        import pandas
        import requests
        print("✅ Dependências principais encontradas")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("💡 Execute: pip install -r requirements.txt")
        return False

def create_directories():
    """Cria diretórios necessários"""
    print("📁 Criando diretórios necessários...")
    
    directories = [
        "data",
        "data/raw_html", 
        "data/exports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}")

def check_mcp_config():
    """Verifica se o arquivo MCP existe"""
    print("🔧 Verificando configuração MCP...")
    
    if Path("mcp.json").exists():
        print("   ✅ Arquivo mcp.json encontrado")
        return True
    else:
        print("   ⚠️  Arquivo mcp.json não encontrado")
        print("   💡 Certifique-se de habilitar MCP no v0.app")
        return False

def start_server():
    """Inicia o servidor FastAPI"""
    print("🚀 Iniciando servidor FastAPI...")
    print("   📍 URL: http://localhost:8000")
    print("   🛑 Para parar: Ctrl+C")
    print("-" * 50)
    
    try:
        # Importar e executar o servidor
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False
    
    return True

def test_server():
    """Testa se o servidor está respondendo"""
    print("🧪 Testando servidor...")
    
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000", timeout=2)
            if response.status_code == 200:
                print("   ✅ Servidor respondendo corretamente")
                return True
        except requests.exceptions.RequestException:
            if attempt < max_attempts - 1:
                print(f"   ⏳ Tentativa {attempt + 1}/{max_attempts}...")
                time.sleep(1)
            else:
                print("   ❌ Servidor não está respondendo")
                return False
    
    return False

def main():
    """Função principal"""
    print("=" * 50)
    print("🎯 COLETA DE PREÇOS - INICIALIZADOR DO SERVIDOR")
    print("=" * 50)
    
    # Verificar dependências
    if not check_dependencies():
        sys.exit(1)
    
    # Criar diretórios
    create_directories()
    
    # Verificar MCP
    check_mcp_config()
    
    print("\n" + "=" * 50)
    print("✅ AMBIENTE VERIFICADO - INICIANDO SERVIDOR")
    print("=" * 50)
    
    # Iniciar servidor
    start_server()

if __name__ == "__main__":
    main()
