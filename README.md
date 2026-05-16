# ETL Banco Central - Meios de Pagamento + Agente IA (MCP)

Este projeto realiza a Extração, Transformação e Carga (ETL) dos dados abertos do Banco Central do Brasil (BCB) referentes à série de Meios de Pagamento. Além disso, expõe esses dados através de um servidor **MCP (Model Context Protocol)** e conta com uma **interface web** capaz de responder perguntas em linguagem natural sobre as transações (PIX, TED, Cartões, etc.) utilizando a API da OpenAI.

## Funcionalidades

- **Extração de Dados (API BCB):** Consulta automatizada à API Olinda do BCB.
- **Transformação:** Tratamento e normalização dos dados utilizando `pandas`.
- **Carga (Load):** Exportação dos dados para SQLite, MySQL ou arquivos CSV.
- **Servidor MCP (`mcp_server/server.py`):** Expõe as funções de dados como ferramentas (tools) para serem consumidas por LLMs.
  - `obter_meios_pagamento_bcb(trimestre)`: Retorna os dados de um trimestre específico.
  - `resumo_anual_meios_pagamento(ano)`: Retorna o consolidado (soma) de um ano inteiro.
- **Interface Web (`app.py`):** Aplicação Streamlit que conecta a API da OpenAI ao servidor MCP local para interpretar perguntas do usuário e responder com dados reais do BCB.

## Pré-requisitos

- Python 3.8 ou superior.
- Uma chave de API válida da OpenAI (**Obrigatório**).

## Instalação e Configuração

1. Clone este repositório.
2. **(Obrigatório)** Crie e ative um ambiente virtual (`.venv`):
   ```bash
   python -m venv .venv

   # Para ativar no Windows (CMD):
   .venv\Scripts\activate
   # Para ativar no Linux/Mac:
   source .venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. **(Obrigatório)** Copie o arquivo `.env.example` para `.env` e insira sua chave da OpenAI:
   ```bash
   # No Windows (CMD/PowerShell)
   copy .env.example .env

   # No Linux/Mac
   cp .env.example .env
   ```

## Como usar

### 1. Rodando a rotina de ETL

Salva os dados do BCB em um banco de dados local:
```bash
python main.py
```

### 2. Rodando o Servidor MCP (standalone)

Para testar as ferramentas com clientes compatíveis (Claude Desktop, MCP Inspector, etc.):
```bash
python -m mcp_server.server
```

### 3. Abrindo a Interface Web

Para interagir com os dados em linguagem natural pelo navegador:
```bash
streamlit run app.py
```

## Estrutura do Projeto

```
etlBCB-1/
├── src/                    # Lógica de ETL
│   ├── extractTransform.py # Extração e transformação via API BCB
│   └── load.py             # Persistência (SQLite, MySQL, CSV)
├── mcp_server/             # Servidor MCP com as ferramentas de dados
│   └── server.py
├── notebooks/              # Análises exploratórias
├── app.py                  # Interface web (Streamlit)
├── main.py                 # Runner do ETL
└── requirements.txt
```

## Tecnologias Utilizadas

Python, Pandas, Requests, Model Context Protocol (MCP), FastMCP, OpenAI API, SQLAlchemy, SQLite, MySQL.
