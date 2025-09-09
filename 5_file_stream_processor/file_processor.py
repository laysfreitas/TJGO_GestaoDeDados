import pandas as pd
import os

def processar_dados_de_livros(caminho_arquivo):
    """
    Lê um arquivo CSV, aplica transformações e gera um relatório agregado.
    """
    print(f"Iniciando processamento do arquivo: {caminho_arquivo}")

    try:
        # Carrega os dados do arquivo CSV para um DataFrame do Pandas
        df = pd.read_csv(caminho_arquivo)
        print("\n--- Dados Originais ---")
        print(df)

        # --- 1. Transformação: Limpeza de Dados ---
        # Remove linhas onde o 'titulo' ou 'preco' são nulos/vazios
        df_limpo = df.dropna(subset=['titulo', 'preco'])
        
        # Garante que a coluna 'preco' seja do tipo numérico (float)
        df_limpo['preco'] = pd.to_numeric(df_limpo['preco'])
        
        print("\n--- Dados Após Limpeza ---")
        print(df_limpo)

        # --- 2. Transformação: Normalização ---
        # Cria uma nova coluna com o título em letras minúsculas para padronização
        df_limpo['titulo_normalizado'] = df_limpo['titulo'].str.lower()

        # --- 3. Transformação: Agregação ---
        # Calcula estatísticas descritivas básicas sobre os preços
        media_preco = df_limpo['preco'].mean()
        mediana_preco = df_limpo['preco'].median()
        livro_mais_caro = df_limpo.loc[df_limpo['preco'].idxmax()]
        livro_mais_barato = df_limpo.loc[df_limpo['preco'].idxmin()]

        print("\n--- Análise Agregada ---")
        print(f"Preço Médio dos Livros: R$ {media_preco:.2f}")
        print(f"Preço Mediano dos Livros: R$ {mediana_preco:.2f}")
        print(f"Livro Mais Caro: {livro_mais_caro['titulo']} (R$ {livro_mais_caro['preco']:.2f})")
        print(f"Livro Mais Barato: {livro_mais_barato['titulo']} (R$ {livro_mais_barato['preco']:.2f})")
        
        # --- 4. Geração de Relatório ---
        # Cria um DataFrame com os resultados agregados
        relatorio = pd.DataFrame({
            "Metrica": ["Preco Medio", "Preco Mediano", "Total de Livros Validos"],
            "Valor": [media_preco, mediana_preco, len(df_limpo)]
        })
        
        # Salva o relatório em um novo arquivo CSV
        caminho_relatorio = 'relatorio_agregado_livros.csv'
        relatorio.to_csv(caminho_relatorio, index=False)
        print(f"\nRelatório agregado salvo em: '{caminho_relatorio}'")

        return df_limpo

    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return None

if __name__ == "__main__":
    processar_dados_de_livros('produtos_coletados.csv')