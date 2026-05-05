from mcp.server.fastmcp import FastMCP
from src.extractTransform import requestApiBcb
import json
import pandas as pd

# Inicializa o servidor FastMCP
mcp = FastMCP("BCB_MeiosPagamento")

@mcp.tool()
def obter_meios_pagamento_bcb(trimestre: str) -> str:
    """
    Obtém os dados da série de meios de pagamento do Banco Central do Brasil (BCB) 
    para um trimestre específico. Ferramenta útil para consultar valores e quantidades 
    de transações por PIX, TED, DOC, Cheques, Cartões, etc.
    
    A resposta retorna um JSON contendo os seguintes campos numéricos para valores e quantidades:
    - datatrimestre (string)
    - valorPix, quantidadePix
    - valorTED, quantidadeTED
    - valorTEC, quantidadeTEC
    - valorCheque, quantidadeCheque
    - valorBoleto, quantidadeBoleto
    - valorDOC, quantidadeDOC
    - valorCartaoCredito, quantidadeCartaoCredito
    - valorCartaoDebito, quantidadeCartaoDebito
    - valorCartaoPrePago, quantidadeCartaoPrePago
    - valorTransIntrabancaria, quantidadeTransIntrabancaria
    - valorConvenios, quantidadeConvenios
    - valorDebitoDireto, quantidadeDebitoDireto
    - valorSaques, quantidadeSaques

    Args:
        trimestre: String no formato AAAAT (Exemplo: "20191" para o 1º trimestre de 2019).
    """
    try:
        df = requestApiBcb(trimestre)
        return df.to_json(orient="records", date_format="iso")
    except Exception as e:
        return json.dumps({"erro": f"Falha ao buscar dados do BCB: {str(e)}"})

@mcp.tool()
def resumo_anual_meios_pagamento(ano: str) -> str:
    """
    Obtém o resumo consolidado (soma) dos dados de meios de pagamento do Banco Central 
    para todos os quatro trimestres de um determinado ano.
    
    A resposta retorna um JSON contendo a soma anual dos seguintes campos numéricos:
    - valorPix, quantidadePix
    - valorTED, quantidadeTED
    - valorTEC, quantidadeTEC
    - valorCheque, quantidadeCheque
    - valorBoleto, quantidadeBoleto
    - valorDOC, quantidadeDOC
    - valorCartaoCredito, quantidadeCartaoCredito
    - valorCartaoDebito, quantidadeCartaoDebito
    - valorCartaoPrePago, quantidadeCartaoPrePago
    - valorTransIntrabancaria, quantidadeTransIntrabancaria
    - valorConvenios, quantidadeConvenios
    - valorDebitoDireto, quantidadeDebitoDireto
    - valorSaques, quantidadeSaques

    Args:
        ano: String contendo o ano com 4 dígitos (Exemplo: "2023").
    """
    try:
        dfs = []
        # Itera pelos 4 trimestres do ano solicitado
        for i in range(1, 5):
            trimestre = f"{ano}{i}"
            df_tri = requestApiBcb(trimestre)
            if not df_tri.empty:
                dfs.append(df_tri)
        
        if not dfs:
            return json.dumps({"erro": f"Nenhum dado encontrado para o ano {ano}."})
            
        df_ano = pd.concat(dfs, ignore_index=True)
        # Soma apenas os valores numéricos, criando uma única linha de totais
        df_resumo = df_ano.select_dtypes(include='number').sum().to_frame().T
        df_resumo["ano"] = ano
        
        return df_resumo.to_json(orient="records")
    except Exception as e:
        return json.dumps({"erro": f"Falha ao consolidar os dados do BCB para o ano {ano}: {str(e)}"})

if __name__ == "__main__":
    mcp.run()
