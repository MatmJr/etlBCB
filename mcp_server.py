from mcp.server.fastmcp import FastMCP
from src.extractTransform import requestApiBcb
import json
import pandas as pd


# Inicializa o servidor FastMCP
mcp = FastMCP("BCB_MeiosPagamento")


@mcp.tool()
def obter_meios_pagamento_bcb(trimestre: str) -> str:
    """
    Busca os dados de transações (PIX, TED, Cartões, etc.) do Banco Central para um ÚNICO TRIMESTRE.
    Use esta ferramenta APENAS quando a pergunta for especificamente sobre um trimestre.
    
    Retorna um JSON contendo 'valor' (em Milhões de R$) e 'quantidade' (em Milhares de unidades) para os meios:
    Pix, TED, TEC, Cheque, Boleto, DOC, CartaoCredito, CartaoDebito, CartaoPrePago, TransIntrabancaria, Convenios, DebitoDireto e Saques.

    Args:
        trimestre: String de 5 dígitos no formato AAAAT (Ex: "20231" para o 1º trimestre de 2023).
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
    Busca o total consolidado de transações (PIX, TED, Cartões, etc.) do Banco Central para um ANO COMPLETO.
    Use esta ferramenta APENAS quando a pergunta for sobre o fechamento de um ano inteiro.
    
    Retorna um JSON contendo a soma anual de 'valor' (em Milhões de R$) e 'quantidade' (em Milhares de unidades) para os meios:
    Pix, TED, TEC, Cheque, Boleto, DOC, CartaoCredito, CartaoDebito, CartaoPrePago, TransIntrabancaria, Convenios, DebitoDireto e Saques.

    Args:
        ano: String de 4 dígitos representando o ano (Ex: "2023").
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
