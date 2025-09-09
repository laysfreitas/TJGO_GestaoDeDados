import time
import random

# Limite de temperatura para o nosso alerta de anomalia
LIMITE_ALERTA_TEMPERATURA = 35.0 

# Histórico de temperaturas para calcular a média móvel
historico_temperaturas = []
TAMANHO_JANELA_MEDIA = 5 # Usaremos as últimas 5 medições

def gerar_dado_clima_em_tempo_real():
    """
    Simula a chegada de um novo dado de clima de um sensor.
    Gera uma temperatura normalmente entre 20 e 30°C, com picos ocasionais.
    """
    temperatura_base = 25
    # Adiciona uma variação e uma chance de gerar uma anomalia
    variacao = random.uniform(-5, 5) + (5 if random.random() > 0.95 else 0)
    
    dado = {
        'cidade': 'Goiânia',
        'temperatura_celsius': round(temperatura_base + variacao, 2),
        'timestamp': time.time()
    }
    return dado

def configurar_alerta(dado_processado):
    """Verifica se o dado processado dispara alguma regra de alerta."""
    temperatura_atual = dado_processado['temperatura_celsius']
    media_recente = dado_processado.get('media_movel_temperatura')

    # Alerta 1: Temperatura absoluta muito alta
    if temperatura_atual > LIMITE_ALERTA_TEMPERATURA:
        print(f"🔴 ALERTA! Temperatura crítica detectada em {dado_processado['cidade']}: {temperatura_atual}°C")

    # Alerta 2: Aumento súbito em relação à média recente
    if media_recente and temperatura_atual > media_recente * 1.25: # 25% acima da média
         print(f"🟡 ALERTA! Aumento súbito de temperatura detectado: {temperatura_atual}°C (Média: {media_recente:.2f}°C)")

def processar_stream_de_clima():
    """
    Processa um fluxo contínuo de dados de clima.
    """
    print("Iniciando processador de stream de clima... (Pressione Ctrl+C para parar)")
    
    while True:
        try:
            # 1. Recebe o novo dado
            novo_dado = gerar_dado_clima_em_tempo_real()
            print(f"Novo dado recebido: {novo_dado['temperatura_celsius']}°C")

            # 2. Transformação em tempo real
            # Adiciona a temperatura ao histórico
            historico_temperaturas.append(novo_dado['temperatura_celsius'])
            
            # Mantém o histórico com o tamanho da janela definido
            if len(historico_temperaturas) > TAMANHO_JANELA_MEDIA:
                historico_temperaturas.pop(0)

            # Calcula a média móvel se tivermos dados suficientes
            if len(historico_temperaturas) == TAMANHO_JANELA_MEDIA:
                media_movel = sum(historico_temperaturas) / len(historico_temperaturas)
                novo_dado['media_movel_temperatura'] = media_movel
            
            # 3. Configura o alerta
            configurar_alerta(novo_dado)
            
            # Espera 2 segundos para simular a próxima chegada de dados
            time.sleep(2)

        except KeyboardInterrupt:
            print("\nProcessador de stream finalizado.")
            break
        except Exception as e:
            print(f"Ocorreu um erro no stream: {e}")
            time.sleep(5) # Espera antes de tentar novamente

if __name__ == "__main__":
    processar_stream_de_clima()