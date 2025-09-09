import requests
from bs4 import BeautifulSoup
import csv

def coletar_precos_livros():
    """
    Função para coletar dados de títulos e preços do site 'books.toscrape.com'.
    """
    URL = 'http://books.toscrape.com/'
    
    print(f"Iniciando a coleta de dados de: {URL}")

    try:
        # Fazer a requisição HTTP para a página
        response = requests.get(URL, timeout=10)
        response.raise_for_status() 

        # Analisar o conteúdo HTML da página
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrar os produtos (neste caso, os livros)
        # Inspecionando a página, vemos que cada livro está dentro de uma tag <article class="product_pod">
        livros = soup.find_all('article', class_='product_pod')

        dados_coletados = []
        
        # Iterar sobre cada livro e extrair as informações
        for livro in livros:
            # O título está dentro de um <h3><a>...</a></h3>
            titulo = livro.h3.a['title']
            
            # O preço está dentro de <div class="product_price"><p class="price_color">...</p></div>
            preco_texto = livro.find('p', class_='price_color').get_text()
            # Limpando o texto do preço para converter para número
            preco = float(preco_texto.replace('£', ''))
            
            dados_coletados.append({'titulo': titulo, 'preco': preco})
            print(f"Coletado: {titulo} - Preço: £{preco}")

        # 5. Salvar os dados em um arquivo CSV para documentação
        with open('produtos_coletados.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['titulo', 'preco'])
            writer.writeheader()
            writer.writerows(dados_coletados)
            
        print("\nDados salvos com sucesso em 'produtos_coletados.csv'")
        
        return dados_coletados

    # 3. Implementar tratamento de erros
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão: {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return None


if __name__ == "__main__":
    coletar_precos_livros()