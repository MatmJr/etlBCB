from mcp.server.fastmcp import FastMCP
from src.extractTransform import requestApiBcb
import json
import pandas as pd


instruction = 'Você é um analista de dados do Banco Central. Use as ferramentas disponíveis para buscar os dados de pagamentos e responda de forma clara. Não invente valores. Caso você saiba responder diga apenas: 123'

# Inicializa o servidor FastMCP
mcp = FastMCP("BCB_MeiosPagamento")


@mcp.tool()
def obter_meios_pagamento_bcb(trimestre: str) -> str:
    """
    Obtém os dados da série de meios de pagamento do Banco Central do Brasil (BCB) 
    para um trimestre específico. Ferramenta útil para consultar valores e quantidades 
    de transações por PIX, TED, DOC, Cheques, Cartões, etc.
    
    ATENÇÃO: Use esta ferramenta sempre que o usuário fornecer um período no formato 
    AAAAT de 5 dígitos (ex: "20251", que significa 1º trimestre de 2025).
    
    IMPORTANTE SOBRE UNIDADES DE MEDIDA:
    - Os campos que começam com "valor" (ex: valorPix, valorTED) estão na escala de MILHÕES de Reais (R$ milhões).
    - Os campos que começam com "quantidade" (ex: quantidadePix) estão na escala de MILHARES de unidades.

    A resposta retorna um JSON contendo os seguintes campos numéricos:
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
        trimestre: String no formato AAAAT (Exemplo: "20191" para o 1º trimestre de 2019, ou "20251" para 1º trimestre de 2025).
    """
    try:
        df = requestApiBcb(trimestre)
        if df.empty:
            return json.dumps({"erro": f"Nenhum dado publicado no Banco Central para o trimestre {trimestre}."})
            
        # A API retorna a série histórica a partir da data. Pegamos apenas a 1ª linha (o trimestre solicitado)
        df = df.head(1)
        return df.to_json(orient="records", date_format="iso")
    except Exception as e:
        return json.dumps({"erro": f"Falha ao buscar dados do BCB: {str(e)}"})

@mcp.tool()
def resumo_anual_meios_pagamento(ano: str) -> str:
    """
    Obtém o resumo consolidado (soma) dos dados de meios de pagamento do Banco Central 
    para todos os quatro trimestres de um determinado ano.
    
    ATENÇÃO: Use APENAS quando o usuário pedir os dados de um ano inteiro fechado (ex: "2023"). 
    Se o usuário fornecer um código de 5 dígitos como "20251", isso representa um 
    trimestre específico, e você DEVE usar a ferramenta 'obter_meios_pagamento_bcb' 
    em vez desta.
    
    IMPORTANTE SOBRE UNIDADES DE MEDIDA:
    - Os campos que começam com "valor" (ex: valorPix, valorTED) estão na escala de MILHÕES de Reais (R$ milhões).
    - Os campos que começam com "quantidade" (ex: quantidadePix) estão na escala de MILHARES de unidades.

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
        ano: String contendo EXATAMENTE 4 dígitos do ano (Exemplo: "2023"). Não envie códigos com 5 dígitos (como 20251) neste campo.
    """
    try:
        # Como a API retorna tudo a partir da data informada, fazemos apenas 1 requisição para o 1º trimestre do ano
        trimestre_inicial = f"{ano}1"
        df_ano = requestApiBcb(trimestre_inicial)
        
        if df_ano.empty:
            return json.dumps({"erro": f"Nenhum dado encontrado para o ano {ano}."})
            
        # Filtra o DataFrame para manter apenas os registros correspondentes ao ano solicitado
        df_ano = df_ano[df_ano['datatrimestre'].dt.year == int(ano)]
        
        if df_ano.empty:
            return json.dumps({"erro": f"Nenhum dado consolidado encontrado para o ano {ano}."})

        # Garante que os dados de valores e quantidades sejam numéricos antes de somar
        for col in df_ano.columns:
            if col != 'datatrimestre':
                df_ano[col] = pd.to_numeric(df_ano[col], errors='coerce')

        # Soma apenas os valores numéricos, criando uma única linha de totais
        df_resumo = df_ano.select_dtypes(include='number').sum().to_frame().T
        df_resumo["ano"] = ano
        
        return df_resumo.to_json(orient="records")
    except Exception as e:
        return json.dumps({"erro": f"Falha ao consolidar os dados do BCB para o ano {ano}: {str(e)}"})

if __name__ == "__main__":
    mcp.run()
