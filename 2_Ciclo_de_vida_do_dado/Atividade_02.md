# Exercício 2: Mapeamento do Ciclo de Vida dos Dados

**Objetivo:** Aplicar o conceito de ciclo de vida dos dados a um cenário de e-commerce.

**Cenário:** Sistema de e-commerce que coleta dados de clientes, produtos e transações.

---

## Mapeamento do Ciclo de Vida dos Dados para E-commerce

Este documento detalha cada fase do ciclo de vida dos dados em um sistema de e-commerce, identificando atividades, tecnologias, desafios e melhorias sugeridas com base no DMBOK.

---

### Fase 1: Coleta

*Nesta fase, os dados são criados ou adquiridos pela primeira vez.*

#### Atividades:
* Cadastro de novos clientes (dados pessoais: nome, e-mail, CPF, endereço).
* Registro de produtos por vendedores (descrição, preço, estoque, imagens).
* Rastreamento da navegação do usuário (páginas visitadas, cliques, tempo de permanência).
* Registro de transações de compra (itens no carrinho, método de pagamento, valor).
* Coleta de dados de avaliações e comentários de produtos.

#### Tecnologias:
* **Formulários Web (HTML5):** Para cadastro e checkout.
* **Cookies de Rastreamento:** (Ex: Google Analytics) para monitorar o comportamento do usuário.
* **APIs (Application Programming Interfaces):** Para integração com gateways de pagamento e sistemas de frete.

#### Desafios:
* **Qualidade dos Dados:** Dados incorretos ou incompletos inseridos pelos usuários.
* **Consentimento e Privacidade:** Garantir conformidade com leis como a LGPD (Lei Geral de Proteção de Dados).
* **Volume e Velocidade:** Lidar com um grande volume de dados gerados em tempo real.
* **Segurança na Captura:** Proteger os dados durante a transmissão.

#### Melhorias baseadas no DMBOK:
* **Governança de Dados:** Definir políticas claras sobre quais dados podem ser coletados e para qual finalidade.
* **Gerenciamento da Qualidade de Dados:** Implementar validações em tempo real nos formulários.
* **Gerenciamento de Metadados:** Documentar a origem, o formato e o propósito de cada dado coletado.

---

### Fase 2: Armazenamento

*Após a coleta, os dados precisam ser armazenados de forma segura e acessível.*

#### Atividades:
* Persistir dados de clientes e pedidos em um banco de dados transacional.
* Guardar logs de acesso e eventos de navegação.
* Armazenar imagens e vídeos de produtos.
* Arquivar notas fiscais e registros de transações.

#### Tecnologias:
* **Bancos de Dados Relacionais (SQL):** PostgreSQL, MySQL para dados estruturados.
* **Bancos de Dados Não Relacionais (NoSQL):** MongoDB, Cassandra para dados semiestruturados.
* **Object Storage:** Amazon S3, Google Cloud Storage para armazenar arquivos.
* **Data Lake:** Para armazenar grandes volumes de dados brutos.

#### Desafios:
* **Segurança:** Proteger os dados contra acessos não autorizados.
* **Escalabilidade:** Suportar o crescimento do volume de dados e de usuários.
* **Custo:** Otimizar os custos de armazenamento.
* **Redundância e Backup:** Evitar a perda de dados.

#### Melhorias baseadas no DMBOK:
* **Arquitetura de Dados:** Desenhar uma arquitetura que separe dados transacionais de analíticos.
* **Gerenciamento da Segurança de Dados:** Implementar criptografia e políticas de controle de acesso (RBAC).
* **Modelagem de Dados:** Aplicar técnicas de modelagem para garantir a consistência e a integridade dos dados.

---

### Fase 3: Processamento

*Os dados brutos são transformados em informações úteis.*

#### Atividades:
* **Limpeza:** Corrigir ou remover dados inconsistentes ou duplicados.
* **Enriquecimento:** Adicionar informações aos dados existentes (ex: cruzar CEP com dados demográficos).
* **Agregação:** Sumarizar dados para análise (ex: total de vendas por região).
* **Transformação (ETL/ELT):** Mover dados dos sistemas operacionais para um Data Warehouse.

#### Tecnologias:
* **Ferramentas de ETL:** Apache Airflow, Talend, AWS Glue.
* **Plataformas de Big Data:** Apache Spark.
* **Linguagens de Programação:** Python (com Pandas) e SQL.

#### Desafios:
* **Integração de Fontes:** Combinar dados de diferentes sistemas de forma consistente.
* **Latência:** Processar os dados rapidamente para tomada de decisão em tempo real.
* **Manutenção da Linhagem (Data Lineage):** Rastrear as transformações aplicadas aos dados.

#### Melhorias baseadas no DMBOK:
* **Gerenciamento de Dados Mestres (MDM):** Criar uma "fonte única da verdade" para entidades críticas como "Cliente" e "Produto".
* **Gerenciamento da Integração de Dados:** Padronizar os processos de ETL/ELT para garantir consistência.
* **Gerenciamento de Metadados:** Documentar todo o fluxo de processamento para facilitar a auditoria.

---

### Fase 4: Uso

*Os dados processados são utilizados para gerar valor para o negócio.*

#### Atividades:
* **Análise de Negócios (BI):** Criar dashboards e relatórios sobre vendas e marketing.
* **Personalização:** Recomendar produtos com base no histórico do cliente.
* **Marketing:** Segmentar clientes para campanhas direcionadas.
* **Detecção de Fraudes:** Analisar padrões para identificar atividades suspeitas.

#### Tecnologias:
* **Ferramentas de BI e Visualização:** Power BI, Tableau, Looker.
* **Plataformas de CRM:** Salesforce.
* **Machine Learning (ML):** Bibliotecas como Scikit-learn, TensorFlow.
* **Data Warehouse:** Google BigQuery, Amazon Redshift, Snowflake.

#### Desafios:
* **Acessibilidade:** Disponibilizar os dados certos para as pessoas certas.
* **Interpretação:** Garantir que os usuários de negócio saibam interpretar os relatórios.
* **Ética e Privacidade:** Utilizar os dados de forma ética e respeitando a privacidade do cliente.

#### Melhorias baseadas no DMBOK:
* **Gerenciamento de BI e Data Warehousing:** Estruturar o DW para responder às perguntas de negócio.
* **Governança de Dados:** Estabelecer políticas de uso ético dos dados.
* **Cultura Data-Driven:** Promover o treinamento e a capacitação dos colaboradores.

---

### Fase 5: Retenção e Descarte

*Define por quanto tempo os dados são mantidos e como são descartados com segurança.*

#### Atividades:
* **Arquivamento:** Mover dados históricos para um armazenamento de baixo custo.
* **Anonimização:** Remover ou mascarar informações de identificação pessoal de dados antigos.
* **Descarte Seguro:** Excluir permanentemente os dados de clientes que solicitaram seu direito ao esquecimento.
* **Cumprimento de Prazos Legais:** Reter dados fiscais pelo período exigido por lei.

#### Tecnologias:
* **Armazenamento de Arquivo:** Amazon S3 Glacier.
* **Scripts de Banco de Dados:** Para executar rotinas de exclusão e anonimização.
* **Ferramentas de Gerenciamento de Ciclo de Vida de Dados:** Oferecidas por provedores de nuvem.

#### Desafios:
* **Conformidade Legal:** Garantir que as políticas de retenção estejam alinhadas com as regulamentações.
* **Exclusão Completa:** Assegurar que os dados sejam removidos de todos os ambientes, incluindo backups.
* **Balancear Custo e Necessidade:** Reter dados pelo tempo necessário sem gerar custos desnecessários.

#### Melhorias baseadas no DMBOK:
* **Governança de Dados:** Criar e oficializar uma **Política de Retenção de Dados**.
* **Arquitetura de Dados:** Projetar sistemas que facilitem a aplicação de regras de retenção.
* **Gerenciamento do Ciclo de Vida da Informação (ILM):** Implementar processos automatizados para mover, arquivar e descartar dados.