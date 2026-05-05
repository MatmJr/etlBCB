# ETL Banco Central - Meios de Pagamento + Agente IA (MCP)

Este projeto realiza a Extração, Transformação e Carga (ETL) dos dados abertos do Banco Central do Brasil (BCB) referentes à série de Meios de Pagamento. Além disso, o projeto expõe esses dados através de um servidor **MCP (Model Context Protocol)** e conta com um **Agente Inteligente** capaz de responder perguntas em linguagem natural sobre as transações (PIX, TED, Cartões, etc.) utilizando a API da OpenAI.

## 🚀 Funcionalidades

- **Extração de Dados (API BCB):** Consulta automatizada à API Olinda do BCB.
- **Transformação:** Tratamento e normalização dos dados utilizando `pandas`.
- **Carga (Load):** Exportação dos dados para SQLite, MySQL ou arquivos CSV.
- **Servidor MCP (`mcp_server.py`):** Expõe as funções de dados como ferramentas (tools) para serem consumidas por LLMs (Large Language Models).
  - `obter_meios_pagamento_bcb(trimestre)`: Retorna os dados de um trimestre específico.
  - `resumo_anual_meios_pagamento(ano)`: Retorna o consolidado (soma) de um ano inteiro.
- **Agente IA (`agent.py`):** Um script interativo que utiliza a API da OpenAI juntamente com o cliente MCP para interpretar perguntas do usuário, invocar as ferramentas locais de dados e formular uma resposta contextualizada baseada em dados reais.

## 📋 Pré-requisitos

- Python 3.8 ou superior.
- Uma chave de API válida da OpenAI (**Obrigatório**).

## 🔧 Instalação e Configuração

1. Clone este repositório.
2. **(Obrigatório)** Crie e ative um ambiente virtual (`.venv`):
   ```bash
   python -m venv .venv
   
   # Para ativar no Windows (CMD):
   .venv\Scripts\activate
   # Para ativar no Linux/Mac:
   source .venv/bin/activate
   ```
3. Instale as dependências executando:
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

## 🏃 Como usar

### 1. Testando a rotina de ETL padrão
Você pode utilizar o script principal para salvar os dados do BCB diretamente em um banco de dados local:
```bash
python main.py
```

### 2. Rodando o Servidor MCP (Standalone)
Para testar o servidor MCP e inspecionar as ferramentas utilizando clientes compatíveis (como o Claude Desktop ou o MCP Inspector):
```bash
python mcp_server.py
```

### 3. Consultando o Agente IA
Para realizar perguntas diretas à IA, que vai de forma autônoma buscar os dados do Banco Central no servidor local para responder:
```bash
python agent.py
```
*(No código atual, o agente pergunta sobre o volume movimentado por PIX e TED no 1º trimestre de 2023, mas a pergunta pode ser alterada diretamente no arquivo `agent.py`).*

## 🛠️ Tecnologias Utilizadas

Python, Pandas, Requests, Model Context Protocol (MCP), FastMCP, OpenAI API, SQLAlchemy, SQLite, MySQL.