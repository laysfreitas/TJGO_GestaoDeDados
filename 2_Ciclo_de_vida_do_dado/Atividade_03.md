# Exercício 3: Modelagem Dimensional Prática

**Objetivo:** Criar um modelo estrela para o cenário de e-commerce.

**Cenário:** Análise de vendas de um sistema de e-commerce.

**Requisitos:** Permitir análises por **período**, **região** e **categoria**.

---

## Passo 1: Identificar Fatos e Dimensões

O processo de negócio a ser analisado é a **Venda**. Portanto, nossa tabela fato central irá registrar os eventos de venda. As dimensões são os "eixos" de análise que nos darão o contexto de "quem", "o quê", "onde" e "quando" cada venda ocorreu.

* **Tabela Fato (Fact Table):**
    * **Fato Vendas:** Representa os itens de uma transação de venda. As métricas (fatos) são os valores numéricos que queremos agregar, como quantidade e valor.

* **Tabelas de Dimensão (Dimension Tables):**
    * **Dimensão Tempo:** Para atender ao requisito de análise por **período**. Descreve a data da venda em diferentes granularidades (dia, mês, ano, etc.).
    * **Dimensão Produto:** Para atender ao requisito de análise por **categoria**. Descreve os produtos vendidos, incluindo seus atributos como nome, marca e categoria.
    * **Dimensão Cliente:** Para atender ao requisito de análise por **região**. Descreve os clientes que realizaram a compra, incluindo sua localização geográfica.

---

## Passo 2: Desenhar o Diagrama Estrela e Especificar Atributos

O diagrama estrela (Star Schema) terá a tabela `FATO_VENDAS` no centro, conectada diretamente às tabelas de dimensão.

#### Diagrama Conceitual:

              +-----------------+
              |   DIM_TEMPO     |
              +-----------------+
              | sk_tempo (PK)   |
              | data_completa   |
              | dia, mes, ano   |
              | trimestre       |
              | ...             |
              +--------+--------+
                       |
                       | (fk_tempo)
                       |
+------------------+   +-------------------+   +----------------+
|   DIM_PRODUTO    |<--+    FATO_VENDAS    +-->|  DIM_CLIENTE   |
+------------------+   +-------------------+   +----------------+
| sk_produto (PK)  |   | fk_produto (FK)   |   | sk_cliente (PK)|
| nome_produto     |   | fk_cliente (FK)   |   | nome_cliente   |
| categoria        |   | fk_tempo (FK)     |   | cidade         |
| subcategoria     |   |                   |   | estado         |
| marca            |   |-------------------|   | regiao         |
| ...              |   |Métricas:          |   | ...            |
+------------------+   | quantidade_vendida|   +----------------+
                       | valor_total       |
                       | valor_desconto    |
                       +-------------------+


#### Especificação de Atributos e Métricas:

* **Tabela Fato: `FATO_VENDAS`**
    * **Chaves Estrangeiras:** `fk_produto`, `fk_cliente`, `fk_tempo`
    * **Métricas:** `quantidade_vendida`, `preco_unitario`, `valor_total_bruto`, `valor_desconto`, `valor_total_liquido`

* **Tabela de Dimensão: `DIM_TEMPO`**
    * **Chave Primária:** `sk_tempo`
    * **Atributos:** `data_completa`, `dia`, `mes`, `nome_mes`, `ano`, `trimestre`, `dia_da_semana`, `flag_fim_de_semana`

* **Tabela de Dimensão: `DIM_PRODUTO`**
    * **Chave Primária:** `sk_produto`
    * **Atributos:** `nk_id_produto` (Chave natural), `nome_produto`, `descricao`, `categoria`, `subcategoria`, `marca`

* **Tabela de Dimensão: `DIM_CLIENTE`**
    * **Chave Primária:** `sk_cliente`
    * **Atributos:** `nk_id_cliente` (Chave natural), `nome_cliente`, `email`, `cidade`, `estado`, `regiao`, `faixa_etaria`

---

## Passo 3: Escrever DDL (Data Definition Language)

Abaixo estão os scripts SQL `CREATE TABLE` para as tabelas principais do modelo.

```sql
-- DDL para a Tabela de Dimensão de Tempo
CREATE TABLE DIM_TEMPO (
    sk_tempo INT PRIMARY KEY,
    data_completa DATE NOT NULL,
    dia INT NOT NULL,
    mes INT NOT NULL,
    nome_mes VARCHAR(20) NOT NULL,
    ano INT NOT NULL,
    trimestre INT NOT NULL,
    dia_da_semana VARCHAR(20) NOT NULL,
    flag_fim_de_semana CHAR(3) NOT NULL -- 'Sim' ou 'Não'
);

-- DDL para a Tabela de Dimensão de Produto
CREATE TABLE DIM_PRODUTO (
    sk_produto SERIAL PRIMARY KEY,
    nk_id_produto VARCHAR(50) NOT NULL,
    nome_produto VARCHAR(255) NOT NULL,
    descricao TEXT,
    categoria VARCHAR(100) NOT NULL,
    subcategoria VARCHAR(100),
    marca VARCHAR(100)
);

-- DDL para a Tabela de Dimensão de Cliente
CREATE TABLE DIM_CLIENTE (
    sk_cliente SERIAL PRIMARY KEY,
    nk_id_cliente VARCHAR(50) NOT NULL,
    nome_cliente VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    cidade VARCHAR(100),
    estado VARCHAR(50),
    regiao VARCHAR(50) NOT NULL,
    faixa_etaria VARCHAR(20)
);

-- DDL para a Tabela Fato de Vendas
CREATE TABLE FATO_VENDAS (
    id_venda SERIAL PRIMARY KEY,
    fk_produto INT NOT NULL,
    fk_cliente INT NOT NULL,
    fk_tempo INT NOT NULL,
    quantidade_vendida INT NOT NULL,
    preco_unitario DECIMAL(10, 2) NOT NULL,
    valor_total_bruto DECIMAL(10, 2) NOT NULL,
    valor_desconto DECIMAL(10, 2),
    valor_total_liquido DECIMAL(10, 2) NOT NULL,

    -- Definição das chaves estrangeiras (constraints)
    CONSTRAINT fk_vendas_produto FOREIGN KEY (fk_produto) REFERENCES DIM_PRODUTO(sk_produto),
    CONSTRAINT fk_vendas_cliente FOREIGN KEY (fk_cliente) REFERENCES DIM_CLIENTE(sk_cliente),
    CONSTRAINT fk_vendas_tempo FOREIGN KEY (fk_tempo) REFERENCES DIM_TEMPO(sk_tempo)
);

