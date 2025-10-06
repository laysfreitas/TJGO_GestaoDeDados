# Sistema de Pareceres

Sistema completo de gestão de pareceres jurídicos com fluxo de trabalho multi-estágios, desenvolvido em Python Flask com PostgreSQL.

## Funcionalidades

### Dashboard
- **Visualização em tabela responsiva** com colunas: Nº do Processo, Data de Recebimento, Prazo, Parecerista Elaborador, Status, Ações
- **Ordenação** por qualquer coluna (clique no cabeçalho)
- **Busca** por número do processo
- **Filtro** por status do parecer
- **Ações rápidas** por linha: Ver/Editar, Avançar, Voltar (conforme o estágio)

### Fluxo de Trabalho
O sistema implementa um fluxo com 4 estágios sequenciais:

1. **Iniciado**
   - Campos: n_processo, interessado, magistrado, comarca, serventia, dt_despacho, dt_encaminhamento, hr_encaminhamento, dt_recebimento, hr_recebimento

2. **Em elaboração**
   - Campos obrigatórios do estágio anterior +
   - id_prazo (FK), id_status (FK), qt_objetos, nota_tecnica

3. **Em revisão**
   - Campos obrigatórios dos estágios anteriores +
   - id_revisor (FK), dt_revisao, hr_revisao

4. **Pronto para envio**
   - Campos obrigatórios dos estágios anteriores +
   - id_responsavel_envio (FK), dt_envio, hr_envio, forma_envio, forma_envio_email, id_anexo_parecer (FK, nullable)

### Interface de Edição
- **Abas por estágio**: apenas a aba do estágio atual está habilitada
- **Validação automática**: impede avanço se campos obrigatórios não forem preenchidos
- **Mensagens claras**: exibe lista de campos faltantes ao tentar avançar

## Tecnologias Utilizadas

- **Backend**: Python 3.11, Flask, SQLAlchemy
- **Banco de dados**: PostgreSQL (via psycopg2-binary)
- **Frontend**: HTML5, TailwindCSS (via CDN)
- **ORM**: Flask-SQLAlchemy 3.x

## Estrutura do Banco de Dados

### Tabelas Principais

**pareceres** - Tabela central com todos os dados do parecer e controle de estágios

**prazos** - Tabela auxiliar com prazos predefinidos (5, 10, 15, 30, 60 dias)

**status** - Tabela auxiliar com status do processo (Aguardando análise, Em análise, Pendente, Concluído, Arquivado)

**usuarios** - Tabela auxiliar com revisores e responsáveis (nome, email, senha_hash)

**documentos** - Tabela auxiliar para anexos (nome_arquivo, url)

### Relacionamentos
- `Parecer.prazo` → `Prazo` (muitos-para-um)
- `Parecer.status` → `Status` (muitos-para-um)
- `Parecer.revisor` → `Usuario` (muitos-para-um)
- `Parecer.responsavel_envio` → `Usuario` (muitos-para-um)
- `Parecer.anexo_parecer` → `Documento` (muitos-para-um, nullable, ondelete='SET NULL')

## Configuração no Replit

### 1. Variáveis de Ambiente (Secrets)

O sistema requer as seguintes variáveis de ambiente configuradas nas Secrets do Replit:

- `DATABASE_URL` - String de conexão PostgreSQL (já configurada automaticamente pelo Replit)
- `SESSION_SECRET` - Chave secreta para sessões Flask (opcional, usa chave de desenvolvimento se não fornecida)

Exemplo de `DATABASE_URL`:
```
postgresql://usuario:senha@host:porta/database
```

### 2. Instalação de Dependências

As dependências já estão instaladas automaticamente:
- flask
- flask-sqlalchemy
- psycopg2-binary

### 3. Inicialização do Banco de Dados

O banco de dados é criado automaticamente na primeira execução. As tabelas auxiliares são populadas com dados iniciais (seeds):

**Prazos criados**:
- 5 dias
- 10 dias
- 15 dias
- 30 dias
- 60 dias

**Status criados**:
- Aguardando análise
- Em análise
- Pendente
- Concluído
- Arquivado

**Usuários criados** (todos com senha: `senha123`):
- João Silva (joao.silva@example.com)
- Maria Santos (maria.santos@example.com)
- Pedro Oliveira (pedro.oliveira@example.com)
- Ana Costa (ana.costa@example.com)

## Como Rodar

### No Replit

1. Clique no botão **Run** no topo da tela
2. Aguarde o servidor inicializar
3. Acesse a aplicação através da URL fornecida pelo Replit
4. O servidor estará disponível na porta 5000

### Localmente

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd <nome-do-diretorio>

# Configure as variáveis de ambiente
export DATABASE_URL="postgresql://usuario:senha@localhost:5432/pareceres"
export SESSION_SECRET="sua-chave-secreta"

# Instale as dependências
pip install flask flask-sqlalchemy psycopg2-binary

# Execute o servidor
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

## Sistema de Autenticação

O sistema possui controle de acesso completo:

### Controle de Acesso

**Visitantes (sem autenticação)**:
- ✅ Visualizar a lista de pareceres
- ❌ Criar novos pareceres
- ❌ Editar pareceres existentes
- ❌ Avançar ou voltar estágios
- ❌ Excluir pareceres

**Usuários autenticados**:
- ✅ Todas as funcionalidades acima
- ✅ Criar, editar e gerenciar pareceres
- ✅ Controlar transições de estágios

### Login no Sistema

1. Acesse a página inicial
2. Clique em **Entrar** no canto superior direito
3. Use um dos usuários iniciais:
   - Email: `joao.silva@example.com`
   - Senha: `senha123`

Você pode usar qualquer um dos 4 usuários criados automaticamente (todos com a mesma senha `senha123`).

### Criar Novo Usuário

1. Na página inicial, clique em **Cadastrar**
2. Preencha:
   - Nome completo
   - Email (deve ser único)
   - Senha (mínimo 6 caracteres)
   - Confirmação de senha
3. Clique em **Cadastrar**
4. Faça login com suas credenciais

### Logout

Para sair do sistema, clique em **Sair** no canto superior direito quando estiver autenticado.

## Uso do Sistema

### Criar Novo Parecer
1. **Faça login no sistema** (obrigatório)
2. Clique no botão **+ Novo Parecer** no cabeçalho
3. Preencha os campos do estágio "Iniciado"
4. Clique em **Salvar**

### Editar Parecer
1. **Faça login no sistema** (obrigatório)
2. Na dashboard, clique em **Editar** na linha do parecer
3. Preencha os campos da aba atual
4. Clique em **Salvar** para manter no mesmo estágio

### Avançar de Estágio
1. **Faça login no sistema** (obrigatório)
2. Visualize ou edite o parecer
3. Certifique-se que todos os campos obrigatórios do estágio atual estão preenchidos
4. Clique em **Avançar para "[próximo estágio]"**
5. Se houver campos faltantes, uma mensagem de erro será exibida

### Voltar de Estágio
1. **Faça login no sistema** (obrigatório)
2. Visualize ou edite o parecer
3. Clique em **Voltar para "[estágio anterior]"**
4. O parecer retorna ao estágio anterior

### Buscar e Filtrar
1. Use o campo **Buscar por Nº do Processo** para localizar pareceres específicos
2. Use o filtro **Filtrar por Status** para ver apenas pareceres em um estágio específico
3. Clique em **Filtrar** para aplicar

### Ordenar
1. Clique no cabeçalho de qualquer coluna para ordenar
2. Clique novamente para inverter a ordem (ascendente/descendente)

## Estrutura do Projeto

```
.
├── app.py              # Aplicação Flask principal com rotas e lógica
├── models.py           # Modelos SQLAlchemy e lógica de validação
├── templates/          # Templates HTML
│   ├── base.html       # Template base com navegação e autenticação
│   ├── index.html      # Dashboard com tabela e filtros
│   ├── editar.html     # Formulário de edição com abas
│   ├── visualizar.html # Página de visualização detalhada
│   ├── login.html      # Página de login
│   └── register.html   # Página de cadastro
├── static/             # Arquivos estáticos (vazio, usa TailwindCSS CDN)
└── README.md           # Este arquivo

```

## Validações Implementadas

### Por Estágio

**Elaboração** (todos os campos do Iniciado são obrigatórios):
- Nº do Processo, Interessado, Magistrado, Comarca, Serventia
- Data e Hora de Despacho, Encaminhamento e Recebimento

**Revisão** (todos os campos da Elaboração são obrigatórios):
- Prazo, Status, Quantidade de Objetos, Nota Técnica

**Pronto para Envio** (todos os campos da Revisão são obrigatórios):
- Revisor, Data e Hora de Revisão

## Segurança

### Senhas

- **Hashing seguro**: Todas as senhas são hashadas usando `werkzeug.security` (scrypt)
- **Nunca armazene senhas em texto plano**
- **Senha padrão**: Os usuários iniciais usam `senha123` - altere em produção!

### Sessões

- As sessões são gerenciadas com cookies seguros do Flask
- Configure `SESSION_SECRET` com uma chave forte em produção
- As sessões expiram ao fechar o navegador

### Observações de Segurança para Produção

- ✅ **Autenticação implementada** - Sistema possui login/logout e controle de acesso
- ⚠️ Altere a `SESSION_SECRET` para uma chave aleatória forte
- ⚠️ Altere as senhas dos usuários padrão
- ⚠️ Configure SSL/HTTPS para conexões seguras
- ⚠️ Use um servidor WSGI em produção (Gunicorn, uWSGI) ao invés do servidor de desenvolvimento Flask
- ⚠️ Implemente limitação de taxa (rate limiting) para tentativas de login
- ⚠️ Adicione recuperação de senha por email

## Suporte

Para questões ou problemas, consulte a documentação do Flask e SQLAlchemy:
- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- TailwindCSS: https://tailwindcss.com/
