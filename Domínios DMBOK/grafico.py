import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Carrega os dados do arquivo CSV
df = pd.read_excel('notas.xlsx', engine='openpyxl')

# Extrai os rótulos e valores
labels = df['Área de Conhecimento do DAMA DMBOK'].tolist()
values = df['Nota (1-5)'].tolist()

# O número de variáveis que estamos plotando.
num_vars = len(labels)

# Calcula o ângulo para cada eixo
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

# O gráfico é um círculo, então precisamos "completar o ciclo"
# e anexar o valor inicial ao final.
values += values[:1]
angles += angles[:1]

# Cria a figura e o eixo polar
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

# Desenha o contorno dos nossos dados.
ax.plot(angles, values, color='red', linewidth=1)
# Preenche a área.
ax.fill(angles, values, color='red', alpha=0.25)

# Corrige o eixo para ir na ordem certa e começar às 12 horas.
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)

# Desenha as linhas do eixo para cada ângulo e rótulo.
ax.set_thetagrids(np.degrees(angles[:-1]), labels)

# Percorre os rótulos e ajusta o alinhamento com base em onde
# ele está no círculo.
for label, angle in zip(ax.get_xticklabels(), angles):
  if angle in (0, np.pi):
    label.set_horizontalalignment('center')
  elif 0 < angle < np.pi:
    label.set_horizontalalignment('left')
  else:
    label.set_horizontalalignment('right')

# Define o valor máximo para o eixo y.
ax.set_ylim(0, 5)

# Adiciona um título.
plt.title('Avaliação DAMA DMBOK', size=20, color='red', y=1.1)

# Salva o gráfico
plt.savefig('radar_chart.png')