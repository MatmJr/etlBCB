import asyncio
import json
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

# Carrega a chave da API localizada no arquivo .env
load_dotenv()

# Define o modelo 'mini' a ser utilizado pelo Agente
MODELO = "gpt-4o-mini"

async def main():
    # Verifica se a chave foi devidamente carregada
    if not os.getenv("OPENAI_API_KEY"):
        print("Erro: A variável OPENAI_API_KEY não está configurada no arquivo .env")
        return

    # Inicializa o cliente assíncrono da OpenAI
    openai_client = AsyncOpenAI()

    # Configura os parâmetros para o Agente iniciar o seu servidor FastMCP
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
    )

    print("Iniciando conexão com o servidor MCP...")
    
    # Inicia a comunicação stdio com o servidor MCP local
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Conectado ao servidor MCP com sucesso!\n")

            # Puxa automaticamente todas as ferramentas cadastradas no seu mcp_server.py
            tools_response = await session.list_tools()
            
            # Converte as ferramentas do formato MCP para o formato do OpenAI Function Calling
            openai_tools = []
            for tool in tools_response.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })

            # Pergunta base que será enviada para o agente
            pergunta = "Qual foi o valor total movimentado por PIX e por TED durante todo o ano de 2025?"
            print(f"Usuário: {pergunta}\n")
            print("Consultando o modelo OpenAI...")

            messages = [
                {
                    "role": "system", 
                    "content": "Você é um analista de dados do Banco Central. Use as ferramentas disponíveis para buscar os dados de pagamentos (seja de um trimestre específico ou o consolidado anual) e responda de forma clara comparando os números."
                },
                {"role": "user", "content": pergunta}
            ]

            # 1º Passo: Manda o prompt para a OpenAI avaliar se precisa chamar alguma ferramenta
            response = await openai_client.chat.completions.create(
                model=MODELO,
                messages=messages,
                tools=openai_tools
            )

            message = response.choices[0].message
            messages.append(message)

            # 2º Passo: Se a IA decidir que precisa chamar a ferramenta, executa ela
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    print(f"[Sistema] A IA solicitou a ferramenta '{tool_name}' usando os parâmetros: {tool_args}...")
                    
                    # Aciona a sua função Python através da ponte do MCP
                    result = await session.call_tool(tool_name, tool_args)
                    tool_result_text = result.content[0].text if result.content else "{}"
                    
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": tool_result_text})

                print("[Sistema] Dados extraídos da API com sucesso! Gerando resposta final...\n")
                final_response = await openai_client.chat.completions.create(model=MODELO, messages=messages)
                print("Resposta da IA:\n" + final_response.choices[0].message.content)

if __name__ == "__main__":
    asyncio.run(main())