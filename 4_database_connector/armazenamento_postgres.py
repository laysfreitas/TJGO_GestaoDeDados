import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor

# --- 1. CONFIGURAÇÃO DA CONEXÃO ---
# Dados de conexão baseados no nosso docker-compose.yml
DB_CONFIG = {
    "dbname": "mcp_database",
    "user": "mcp_user",
    "password": "mcp_password",
    "host": "localhost",
    "port": "5432",
    "client_encoding": "utf8"
}

def conectar():
    """Estabelece a conexão com o banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Conexão com PostgreSQL bem-sucedida!")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Erro ao conectar com o PostgreSQL: {e}")
        return None

# --- 2. CRIAÇÃO DE ESQUEMAS/ESTRUTURAS ---
def criar_tabelas(conn):
    """Cria as tabelas para livros e registros de clima, se não existirem."""
    with conn.cursor() as cur:
        # Tabela para os dados de e-commerce (livros)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS livros (
                id SERIAL PRIMARY KEY,
                titulo VARCHAR(255) NOT NULL,
                preco DECIMAL(10, 2) NOT NULL,
                data_coleta TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        # Tabela para os dados de meteorologia
        cur.execute("""
            CREATE TABLE IF NOT EXISTS registros_clima (
                id SERIAL PRIMARY KEY,
                cidade VARCHAR(100) NOT NULL,
                condicao VARCHAR(100),
                temperatura_celsius DECIMAL(5, 2),
                umidade_percentual INTEGER,
                data_coleta TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        print("Tabelas 'livros' e 'registros_clima' verificadas/criadas.")
    conn.commit()

# --- 4. CONFIGURAÇÃO DE ÍNDICES ---
def criar_indices(conn):
    """Cria índices para otimizar consultas."""
    with conn.cursor() as cur:
        # Índice na coluna 'titulo' da tabela 'livros'
        cur.execute("CREATE INDEX IF NOT EXISTS idx_livros_titulo ON livros (titulo);")
        # Índice na coluna 'cidade' da tabela 'registros_clima'
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clima_cidade ON registros_clima (cidade);")
        print("Índices verificados/criados.")
    conn.commit()

# --- 3. ROTINAS DE INSERÇÃO COM VALIDAÇÃO ---
# --- 5. OPERAÇÕES DE CRUD (CREATE) ---
def inserir_livro(conn, titulo, preco):
    """Insere um novo livro no banco de dados com validação."""
    # Validação de dados básica
    if not isinstance(titulo, str) or not titulo:
        print("Erro de validação: Título inválido.")
        return
    if not isinstance(preco, (int, float)) or preco < 0:
        print("Erro de validação: Preço inválido.")
        return
        
    sql_insert = "INSERT INTO livros (titulo, preco) VALUES (%s, %s) RETURNING id;"
    with conn.cursor() as cur:
        cur.execute(sql_insert, (titulo, preco))
        id_inserido = cur.fetchone()[0]
        conn.commit()
        print(f"Livro '{titulo}' inserido com ID: {id_inserido}.")
        return id_inserido

# --- 5. OPERAÇÕES DE CRUD (READ) ---
def buscar_livro_por_titulo(conn, titulo):
    """Busca livros por título."""
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM livros WHERE titulo ILIKE %s;", (f"%{titulo}%",))
        livros = cur.fetchall()
        return [dict(livro) for livro in livros]

# --- 5. OPERAÇÕES DE CRUD (UPDATE) ---
def atualizar_preco_livro(conn, livro_id, novo_preco):
    """Atualiza o preço de um livro."""
    with conn.cursor() as cur:
        cur.execute("UPDATE livros SET preco = %s WHERE id = %s;", (novo_preco, livro_id))
        conn.commit()
        # rowcount retorna o número de linhas afetadas
        if cur.rowcount > 0:
            print(f"Preço do livro ID {livro_id} atualizado para {novo_preco}.")
            return True
        print(f"Livro com ID {livro_id} não encontrado.")
        return False

# --- 5. OPERAÇÕES DE CRUD (DELETE) ---
def deletar_livro(conn, livro_id):
    """Deleta um livro pelo seu ID."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM livros WHERE id = %s;", (livro_id,))
        conn.commit()
        if cur.rowcount > 0:
            print(f"Livro ID {livro_id} deletado com sucesso.")
            return True
        print(f"Livro com ID {livro_id} não encontrado para deletar.")
        return False

# --- ROTINA DE TESTES ---
if __name__ == "__main__":
    conn = conectar()
    if conn:
        criar_tabelas(conn)
        criar_indices(conn)

        print("\n--- INICIANDO TESTES CRUD ---")
        
        # CREATE
        id_livro_teste = inserir_livro(conn, "A Arte da Guerra", 45.50)
        inserir_livro(conn, "O Pequeno Príncipe", 29.90)

        # READ
        print("\n--- Buscando livros com 'arte' no título: ---")
        livros_encontrados = buscar_livro_por_titulo(conn, "arte")
        for livro in livros_encontrados:
            print(livro)

        # UPDATE
        print("\n--- Atualizando preço do livro teste: ---")
        if id_livro_teste:
            atualizar_preco_livro(conn, id_livro_teste, 52.00)
            livro_atualizado = buscar_livro_por_titulo(conn, "A Arte da Guerra")
            print("Livro após atualização:", livro_atualizado[0])

        # DELETE
        print("\n--- Deletando o livro teste: ---")
        if id_livro_teste:
            deletar_livro(conn, id_livro_teste)
            livros_restantes = buscar_livro_por_titulo(conn, "") # Busca todos
            print("Livros restantes:", livros_restantes)
            
        conn.close()
        print("\nConexão com PostgreSQL fechada.")