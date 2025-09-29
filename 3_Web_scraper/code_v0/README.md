# Aplicação de Coleta de Preços de Produtos

Uma aplicação completa para coleta automatizada de preços de produtos usando web scraping e integração com APIs de câmbio.

## Funcionalidades

- **Coleta Automatizada**: Scraping do site Books to Scrape com respeito ao robots.txt
- **Múltiplas Categorias**: Coleta dados das categorias Travel e Science
- **Conversão de Moeda**: Integração com API de câmbio para converter GBP para BRL/USD
- **Interface Completa**: Telas de Coletas, Dados e Câmbio
- **CRUD Completo**: Criar, ler, atualizar e excluir registros
- **Exportação**: Geração de arquivos CSV e JSON
- **Acessibilidade**: Atalhos de teclado (Alt+N, Alt+F, Alt+S)

## Tecnologias

- **Backend**: FastAPI (Python)
- **Frontend**: React/Next.js com Tailwind CSS
- **Scraping**: MCP Web Scraper
- **API Externa**: MCP API Client
- **Dados**: Armazenamento local em arquivos

## 🚀 Início Rápido

### Opção 1: Script Automático (Recomendado)

\`\`\`bash
# Execute o script de inicialização
python start_server.py
\`\`\`

O script irá:
- ✅ Verificar dependências
- 📁 Criar diretórios necessários
- 🔧 Validar configuração MCP
- 🚀 Iniciar o servidor FastAPI

### Opção 2: Manual

\`\`\`bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Iniciar servidor FastAPI
python main.py
\`\`\`

O servidor estará disponível em: **http://localhost:8000**

### ⚠️ Importante

- **Frontend**: A interface Next.js roda automaticamente no v0.app
- **Backend**: O servidor Python deve ser iniciado separadamente
- **MCP**: Deve ser habilitado no v0.app (veja instruções abaixo)

## Como Habilitar MCP no v0.app

1. **Acesse as Configurações do Projeto**:
   - Clique no ícone de engrenagem no canto superior direito
   - Selecione "Project Settings"

2. **Configure o MCP**:
   - Na seção "MCP Servers", adicione os seguintes servidores:
   
   **Web Scraper**:
   - Nome: `web-scraper`
   - Comando: `npx -y @modelcontextprotocol/server-web-scraper`
   - Variável de ambiente: `MCP_WEB_SCRAPER_MAX_REQUESTS_PER_MINUTE=30`
   
   **API Client**:
   - Nome: `api-client`
   - Comando: `npx -y @modelcontextprotocol/server-api-client`
   - Variável de ambiente: `MCP_API_CLIENT_ALLOWED_HOSTS=api.exchangerate.host`

3. **Salve e Reinicie**: Salve as configurações e reinicie o ambiente

## 🔧 Solução de Problemas

### "Servidor FastAPI Offline"

Se você vê esta mensagem na interface:

1. **Verifique se o servidor está rodando**:
   \`\`\`bash
   # Teste se o servidor responde
   curl http://localhost:8000
   \`\`\`

2. **Inicie o servidor**:
   \`\`\`bash
   python start_server.py
   # ou
   python main.py
   \`\`\`

3. **Verifique dependências**:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

### "Failed to fetch"

Este erro indica que o frontend não consegue se comunicar com o backend:

- ✅ Certifique-se que o servidor Python está rodando na porta 8000
- ✅ Verifique se não há firewall bloqueando a porta
- ✅ Teste o servidor diretamente: http://localhost:8000

### Problemas com MCP

- ✅ Verifique se os servidores MCP estão habilitados no v0.app
- ✅ Confirme as variáveis de ambiente estão configuradas
- ✅ Reinicie o ambiente após mudanças na configuração

## Estrutura do Projeto

\`\`\`
/
├── mcp.json                 # Configuração MCP
├── README.md               # Documentação
├── requirements.txt        # Dependências Python
├── start_server.py         # Script de inicialização
├── main.py                # Servidor FastAPI
├── scraper/               # Módulos de scraping
├── app/                   # Interface Next.js
├── data/                  # Dados coletados
│   ├── precos_brutos_*.csv
│   ├── cambio_*.json
│   └── raw_html/          # HTML bruto em caso de erro
└── components/            # Componentes React
\`\`\`

## 📋 Como Usar

### 1. Primeira Execução

1. **Habilite MCP** no v0.app (veja instruções acima)
2. **Inicie o servidor**: `python start_server.py`
3. **Acesse a interface** no v0.app
4. **Execute uma coleta** na aba "Coletas"

### 2. Fluxo Normal

1. **Coletas**: Inicie coletas automáticas de dados
2. **Dados**: Visualize, filtre e exporte os dados coletados
3. **Câmbio**: Monitore taxas de conversão de moeda

### 3. Atalhos de Teclado

- **Alt+N**: Nova coleta
- **Alt+F**: Filtrar dados
- **Alt+S**: Salvar/Exportar

## 📊 Campos Coletados

- `produto_nome`: Nome do produto
- `preco_bruto`: Preço em GBP (normalizado)
- `disponibilidade`: Status de disponibilidade
- `categoria`: Categoria do produto
- `avaliacao`: Avaliação de 1-5 estrelas
- `produto_url`: URL do produto
- `coleta_ts`: Timestamp da coleta
- `preco_brl`: Preço convertido para BRL
- `preco_usd`: Preço convertido para USD

## 🛡️ Conformidade

- Respeita robots.txt do site alvo
- Intervalo mínimo de 1 segundo entre requisições
- User-Agent educativo identificando o propósito
- Tratamento de erros com salvamento de HTML bruto

## 📁 Arquivos Gerados

- `data/precos_brutos_YYYY-MM-DD.csv`: Dados dos produtos
- `data/cambio_YYYY-MM-DD.json`: Taxas de câmbio
- `data/exports/`: Arquivos de exportação personalizados
- `data/raw_html/`: HTML bruto para debug

## 🔄 Fluxo de Dados

1. **Coleta** → MCP Web Scraper extrai dados do Books to Scrape
2. **Câmbio** → MCP API Client obtém taxas de exchangerate.host
3. **Processamento** → FastAPI processa e converte preços
4. **Armazenamento** → Dados salvos em CSV/JSON
5. **Interface** → React/Next.js exibe dados processados
