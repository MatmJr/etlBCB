import asyncio
import json
import os
import streamlit as st
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

st.set_page_config(page_title="Agente IA - Banco Central", page_icon="🏦")

load_dotenv()

with st.sidebar:
    st.header("⚙️ Configurações")
    modelo_selecionado = st.selectbox("Modelo OpenAI:", ["gpt-4o-mini"])

    if not os.getenv("OPENAI_API_KEY"):
        api_key = st.text_input("OpenAI API Key:", type="password")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
    else:
        st.success("Chave de API carregada com sucesso!")

st.title("🏦 Agente de Dados - Banco Central")
st.write("Faça perguntas naturais sobre movimentações de PIX, TED, Cartões e outros meios de pagamento.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "Você é um analista de dados do Banco Central. Use as ferramentas disponíveis para buscar os dados. "
            "Os dados retornados pelas ferramentas já estão formatados em texto e prontos para exibição (Ex: 'R$ 17,10 Trilhões'). "
            "Apenas repasse os valores exatos retornados pelas ferramentas de forma amigável e legível para o usuário sem modificar a sua grandeza."
        }
    ]

pending_tools = []
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "tool":
        pending_tools.append(msg)
    elif msg["role"] == "assistant" and msg.get("content"):
        with st.chat_message("assistant"):
            st.markdown(msg["content"])
            for t_msg in pending_tools:
                with st.expander(f"📄 Fonte de Dados: {t_msg.get('name', 'Ferramenta')}"):
                    try:
                        st.json(json.loads(t_msg["content"]))
                    except (json.JSONDecodeError, TypeError):
                        st.text(t_msg["content"])
            pending_tools = []

async def query_agent(prompt, model):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status_box = st.empty()
        status_box.info("🔌 Conectando ao servidor MCP local...")

        openai_client = AsyncOpenAI()
        server_params = StdioServerParameters(command="python", args=["-m", "mcp_server.server"])

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
                    st.session_state.messages.append(message.model_dump(exclude_none=True))

                    if message.tool_calls:
                        executed_tools = []
                        for tool_call in message.tool_calls:
                            tool_name = tool_call.function.name
                            tool_args = json.loads(tool_call.function.arguments)
                            status_box.warning(f"⚙️ Executando a ferramenta: `{tool_name}`...")

                            result = await session.call_tool(tool_name, tool_args)
                            tool_result_text = result.content[0].text if result.content else "{}"

                            t_msg = {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": tool_result_text
                            }
                            st.session_state.messages.append(t_msg)
                            executed_tools.append(t_msg)

                        status_box.info("✅ Dados recebidos! Gerando resposta final...")

                        final_response = await openai_client.chat.completions.create(
                            model=model,
                            messages=st.session_state.messages
                        )

                        final_text = final_response.choices[0].message.content
                        st.session_state.messages.append({"role": "assistant", "content": final_text})
                        status_box.empty()
                        st.markdown(final_text)

                        for t_msg in executed_tools:
                            with st.expander(f"📄 Fonte de Dados: {t_msg.get('name', 'Ferramenta')}"):
                                try:
                                    st.json(json.loads(t_msg["content"]))
                                except (json.JSONDecodeError, TypeError):
                                    st.text(t_msg["content"])
                    else:
                        final_text = message.content
                        status_box.empty()
                        st.markdown(final_text)
        except Exception as e:
            status_box.error(f"Erro durante a execução: {str(e)}")

if prompt := st.chat_input("Qual foi o valor movimentado por PIX e TED em 2023?"):
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ Insira a chave da API da OpenAI na barra lateral para continuar.")
    else:
        asyncio.run(query_agent(prompt, modelo_selecionado))
