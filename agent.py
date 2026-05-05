import asyncio
import json
import os
import streamlit as st
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

# Configuração inicial da página Streamlit
st.set_page_config(page_title="Agente IA - Banco Central", page_icon="🏦")

# Carrega as variáveis de ambiente
load_dotenv()

# Configurações na barra lateral
with st.sidebar:
    st.header("⚙️ Configurações")
    modelo_selecionado = st.selectbox("Modelo OpenAI:", ["gpt-4o-mini"])
    
    # Verifica e permite inserir a chave da API dinamicamente
    if not os.getenv("OPENAI_API_KEY"):
        api_key = st.text_input("OpenAI API Key:", type="password")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
    else:
        st.success("Chave de API carregada com sucesso!")

st.title("🏦 Agente de Dados - Banco Central")
st.write("Faça perguntas naturais sobre movimentações de PIX, TED, Cartões e outros meios de pagamento.")

# Inicializa o histórico de mensagens da sessão do Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": "Você é um analista de dados do Banco Central. Use as ferramentas disponíveis para buscar os dados de pagamentos e responda de forma clara. ATENÇÃO: Os dados de 'valor' estão em Milhões de Reais e os de 'quantidade' em Milhares de unidades. Observção: Caso você saiba responder diga apenas: 123", 
        }
    ]

# Renderiza o histórico do chat
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant" and msg.get("content"):
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

async def query_agent(prompt, model):
    # Adiciona e exibe a pergunta do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status_box = st.empty()
        status_box.info("🔌 Conectando ao servidor MCP local...")

        openai_client = AsyncOpenAI()
        server_params = StdioServerParameters(command="python", args=["mcp_server.py"])

        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    status_box.info("🛠️ Obtendo ferramentas do BCB...")
                    tools_response = await session.list_tools()
                    
                    openai_tools = [
                        {
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": tool.inputSchema
                            }
                        }
                        for tool in tools_response.tools
                    ]

                    status_box.info(f"🧠 Consultando o modelo ({model})...")
                    
                    response = await openai_client.chat.completions.create(
                        model=model,
                        messages=st.session_state.messages,
                        tools=openai_tools
                    )

                    message = response.choices[0].message
                    # Salva a mensagem no estado como dicionário para compatibilidade
                    st.session_state.messages.append(message.model_dump(exclude_none=True))

                    # Verifica se a IA solicitou chamar ferramentas
                    if message.tool_calls:
                        for tool_call in message.tool_calls:
                            tool_name = tool_call.function.name
                            tool_args = json.loads(tool_call.function.arguments)
                            status_box.warning(f"⚙️ Executando a ferramenta: `{tool_name}`...")
                            
                            result = await session.call_tool(tool_name, tool_args)
                            tool_result_text = result.content[0].text if result.content else "{}"
                            
                            st.session_state.messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": tool_result_text
                            })

                        status_box.info("✅ Dados recebidos! Gerando resposta final...")
                        
                        final_response = await openai_client.chat.completions.create(
                            model=model,
                            messages=st.session_state.messages
                        )
                        
                        final_text = final_response.choices[0].message.content
                        st.session_state.messages.append({"role": "assistant", "content": final_text})
                        status_box.empty()
                        st.markdown(final_text)
                    else:
                        final_text = message.content
                        status_box.empty()
                        st.markdown(final_text)
        except Exception as e:
            status_box.error(f"Erro durante a execução: {str(e)}")

# Campo de entrada de texto interativo no rodapé
if prompt := st.chat_input("Qual foi o valor movimentado por PIX e TED em 2023?"):
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ Insira a chave da API da OpenAI na barra lateral para continuar.")
    else:
        asyncio.run(query_agent(prompt, modelo_selecionado))