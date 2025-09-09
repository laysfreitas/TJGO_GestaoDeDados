import requests
import os
from dotenv import load_dotenv

def consumir_api_clima(cidade, api_key):
    """
    Consome a API do OpenWeatherMap para obter dados meteorológicos de uma cidade.
    """
    # URL base da API
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    # Parâmetros da requisição
    params = {
        'q': cidade,
        'appid': api_key,
        'units': 'metric',  # Para obter a temperatura em Celsius
        'lang': 'pt_br'     # Para obter a descrição em português
    }
    
    print(f"Buscando dados meteorológicos para: {cidade}")

    try:
        # Fazer a requisição GET para a API
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()

        # Converter a resposta (que é em formato JSON) para um dicionário Python
        dados = response.json()
        
        # Extrair os campos de interesse
        descricao_clima = dados['weather'][0]['description']
        temperatura = dados['main']['temp']
        umidade = dados['main']['humidity']
        
        # Exibir os dados
        print("\n--- Dados Coletados ---")
        print(f"Condição: {descricao_clima.capitalize()}")
        print(f"Temperatura: {temperatura}°C")
        print(f"Umidade: {umidade}%")
        print("-----------------------\n")
        
        return {
            'cidade': cidade,
            'condicao': descricao_clima,
            'temperatura_celsius': temperatura,
            'umidade_percentual': umidade
        }
        
    # Implementar tratamento de erros
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("Erro: API Key inválida ou não autorizada.")
        elif e.response.status_code == 404:
            print(f"Erro: Cidade '{cidade}' não encontrada.")
        else:
            print(f"Erro HTTP: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão com a API: {e}")
        return None
    except KeyError as e:
        print(f"Erro: A resposta da API não contém o campo esperado: {e}")
        return None

if __name__ == "__main__":
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # busca a API Key do ambiente usando o nome da variável definido no .env
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    CIDADE = "São Paulo,BR"
    
    # Verifica se a chave foi carregada com sucesso
    if not API_KEY:
        print("Erro: A variável de ambiente OPENWEATHER_API_KEY não foi encontrada.")
        print("Verifique se o arquivo .env existe e se a variável está definida nele.")
    else:
        # Executa a função com os dados corretos
        consumir_api_clima(cidade=CIDADE, api_key=API_KEY)