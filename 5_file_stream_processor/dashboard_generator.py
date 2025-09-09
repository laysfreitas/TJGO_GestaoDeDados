import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from file_processor import processar_dados_de_livros # Reutiliza nossa função do outro script

def gerar_dashboard(dataframe_limpo):
    """
    Gera e salva visualizações gráficas a partir de um DataFrame.
    """
    if dataframe_limpo is None or dataframe_limpo.empty:
        print("DataFrame vazio. Não é possível gerar o dashboard.")
        return

    print("\nIniciando a geração do dashboard...")

    # Configura o estilo dos gráficos
    sns.set_theme(style="whitegrid")

    # --- Gráfico 1: Distribuição de Preços ---
    plt.figure(figsize=(10, 6))
    sns.histplot(dataframe_limpo['preco'], kde=True, bins=5)
    plt.title('Distribuição de Preços dos Livros', fontsize=16)
    plt.xlabel('Preço (R$)', fontsize=12)
    plt.ylabel('Frequência', fontsize=12)
    plt.savefig('dashboard_distribuicao_precos.png')
    print("Gráfico 'distribuicao_precos.png' salvo.")

    # --- Gráfico 2: Top 5 Livros Mais Caros ---
    top_5_caros = dataframe_limpo.nlargest(5, 'preco')
    plt.figure(figsize=(10, 6))
    sns.barplot(x='preco', y='titulo', data=top_5_caros, palette='viridis')
    plt.title('Top 5 Livros Mais Caros', fontsize=16)
    plt.xlabel('Preço (R$)', fontsize=12)
    plt.ylabel('Título do Livro', fontsize=12)
    plt.tight_layout() # Ajusta o layout para evitar cortes nos títulos
    plt.savefig('dashboard_top_5_caros.png')
    print("Gráfico 'top_5_caros.png' salvo.")
    
    plt.close('all') # Fecha todas as figuras para liberar memória

if __name__ == "__main__":
    # 1. Processa os dados primeiro para obter um DataFrame limpo
    df_livros_processado = processar_dados_de_livros('produtos_coletados.csv')
    
    # 2. Gera o dashboard com os dados processados
    gerar_dashboard(df_livros_processado)