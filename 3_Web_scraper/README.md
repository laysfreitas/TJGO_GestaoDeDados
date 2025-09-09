# Exercício 1: Coleta de Dados

Este projeto contém dois scripts para coleta automatizada de dados:
1.  `scraper_ecommerce.py`: Coleta títulos e preços de livros do site 'books.toscrape.com'.
2.  `client_api_meteorologia.py`: Consome a API da OpenWeatherMap para obter dados de clima.

## Como Executar

1.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configurar a API Key:**
    No arquivo `client_api_meteorologia.py`, substitua o valor da variável `API_KEY` pela sua chave obtida no site OpenWeatherMap.

3.  **Executar os Scripts:**
    ```bash
    python scraper_ecommerce.py
    python client_api_meteorologia.py
    ```

## Campos Extraídos

### 1. Web Scraper de E-commerce (`produtos_coletados.csv`)

| Campo    | Tipo de Dado | Descrição                            |
| :------- | :----------- | :------------------------------------- |
| `titulo` | String       | O título completo do livro.            |
| `preco`  | Float        | O preço do livro em Libras Esterlinas. |

### 2. Cliente de API de Meteorologia

| Campo                | Tipo de Dado | Unidade | Descrição                                  |
| :------------------- | :----------- | :------ | :------------------------------------------- |
| `cidade`             | String       | N/A     | Nome da cidade pesquisada.                   |
| `condicao`           | String       | N/A     | Descrição do clima (ex: "céu limpo").      |
| `temperatura_celsius`| Float        | °C      | Temperatura atual em graus Celsius.          |
| `umidade_percentual` | Integer      | %       | Percentual de umidade relativa do ar.        |
