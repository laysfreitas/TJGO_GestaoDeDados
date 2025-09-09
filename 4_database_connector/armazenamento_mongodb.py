import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

# --- 1. CONFIGURAÇÃO DA CONEXÃO ---
# String de conexão baseada no nosso docker-compose.yml
MONGO_URI = "mongodb://mcp_user:mcp_password@localhost:27017/"

def conectar():
    """Estabelece a conexão com o MongoDB."""
    try:
        client = MongoClient(MONGO_URI)
        # Força uma conexão para verificar se está funcionando
        client.admin.command('ping')
        print("Conexão com MongoDB bem-sucedida!")
        # Seleciona o banco de dados
        db = client.mcp_database
        return db
    except pymongo.errors.ConnectionFailure as e:
        print(f"Erro ao conectar com o MongoDB: {e}")
        return None

# --- 2. CRIAÇÃO DE ESQUEMAS/ESTRUTURAS e 4. ÍNDICES ---
# No MongoDB, coleções são criadas na primeira inserção.
# Os índices podem ser criados a qualquer momento.
def configurar_colecoes(db):
    """Garante que as coleções existem e que os índices estão criados."""
    try:
        # Índice na coleção 'livros'
        db.livros.create_index([("titulo", pymongo.ASCENDING)], name="idx_livros_titulo")
        # Índice na coleção 'registros_clima'
        db.registros_clima.create_index([("cidade", pymongo.ASCENDING)], name="idx_clima_cidade")
        print("Coleções e índices verificados/criados no MongoDB.")
    except Exception as e:
        print(f"Erro ao criar índices no MongoDB: {e}")

# --- 3. ROTINAS DE INSERÇÃO COM VALIDAÇÃO ---
# --- 5. OPERAÇÕES DE CRUD (CREATE) ---
def inserir_livro(db, titulo, preco):
    """Insere um novo livro (documento) na coleção 'livros'."""
    # Validação de dados básica
    if not isinstance(titulo, str) or not titulo:
        print("Erro de validação: Título inválido.")
        return
    if not isinstance(preco, (int, float)) or preco < 0:
        print("Erro de validação: Preço inválido.")
        return
        
    documento_livro = {
        "titulo": titulo,
        "preco": preco,
    }
    resultado = db.livros.insert_one(documento_livro)
    print(f"Livro '{titulo}' inserido com ID: {resultado.inserted_id}.")
    return resultado.inserted_id

# --- 5. OPERAÇÕES DE CRUD (READ) ---
def buscar_livro_por_titulo(db, titulo):
    """Busca documentos de livros por título (case-insensitive)."""
    # Usando regex para uma busca 'like'
    resultados = db.livros.find({"titulo": {"$regex": titulo, "$options": "i"}})
    return list(resultados)

# --- 5. OPERAÇÕES DE CRUD (UPDATE) ---
def atualizar_preco_livro(db, livro_id, novo_preco):
    """Atualiza o preço de um livro pelo seu _id."""
    resultado = db.livros.update_one(
        {"_id": ObjectId(livro_id)},
        {"$set": {"preco": novo_preco}}
    )
    if resultado.matched_count > 0:
        print(f"Preço do livro ID {livro_id} atualizado para {novo_preco}.")
        return True
    print(f"Livro com ID {livro_id} não encontrado.")
    return False

# --- 5. OPERAÇÕES DE CRUD (DELETE) ---
def deletar_livro(db, livro_id):
    """Deleta um livro pelo seu _id."""
    resultado = db.livros.delete_one({"_id": ObjectId(livro_id)})
    if resultado.deleted_count > 0:
        print(f"Livro ID {livro_id} deletado com sucesso.")
        return True
    print(f"Livro com ID {livro_id} não encontrado para deletar.")
    return False

# --- ROTINA DE TESTES ---
if __name__ == "__main__":
    db = conectar()
    if db:
        configurar_colecoes(db)

        print("\n--- INICIANDO TESTES CRUD NO MONGODB ---")
        
        # CREATE
        id_livro_teste = inserir_livro(db, "A Revolução dos Bichos", 35.20)
        inserir_livro(db, "1984", 42.80)

        # READ
        print("\n--- Buscando livros com 'revolução' no título: ---")
        livros_encontrados = buscar_livro_por_titulo(db, "revolução")
        for livro in livros_encontrados:
            print(livro)
            
        # UPDATE
        print("\n--- Atualizando preço do livro teste: ---")
        if id_livro_teste:
            atualizar_preco_livro(db, id_livro_teste, 38.00)
            livro_atualizado = db.livros.find_one({"_id": id_livro_teste})
            print("Livro após atualização:", livro_atualizado)
            
        # DELETE
        print("\n--- Deletando o livro teste: ---")
        if id_livro_teste:
            deletar_livro(db, id_livro_teste)
            livros_restantes = list(db.livros.find())
            print("Livros restantes:", livros_restantes)