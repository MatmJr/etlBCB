import requests
import pandas as pd


def requestApiBcb(data: str) -> pd.DataFrame:
    """
    Função para extrair os dados da API do Banco Central.

    Parâmetros:
    data - string - AAAAT (Exemplo: 20191)

    Saída:
    DataFrame - Estrutura de dados do pandas
    """
    url = f"https://olinda.bcb.gov.br/olinda/servico/MPV_DadosAbertos/versao/v1/odata/MeiosdePagamentosTrimestralDA(trimestre=@trimestre)?@trimestre=%27{data}%27&$format=json"
    req = requests.get(url)
    req.raise_for_status()
    dados = req.json()

    df = pd.json_normalize(dados["value"])
    if not df.empty and "datatrimestre" in df.columns:
        df["datatrimestre"] = pd.to_datetime(df["datatrimestre"])

    return df
