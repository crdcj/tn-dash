import datetime as dt
import pandas as pd
import streamlit as st
import pyield as pyd
from pytz import timezone
import requests

# Constantes comuns (se necessário)
TIMEZONE_BZ = timezone("America/Sao_Paulo")
PYIELD_DATA_URL = "https://raw.githubusercontent.com/crdcj/pyield-data/main/"
ANBIMA_RATES_URL = f"{PYIELD_DATA_URL}anbima_data.parquet"
DI_DATA_URL = f"{PYIELD_DATA_URL}di_data.csv.gz"


@st.cache_data(ttl=28800)  # 8 horas de cache
def load_anbima_rates() -> pd.DataFrame:
    # df = pd.read_csv(ANBIMA_RATES_URL, parse_dates=["ReferenceDate", "MaturityDate"])
    df = pd.read_parquet(ANBIMA_RATES_URL, engine='pyarrow')
    # Convert columns to datetime.date
    # df["ReferenceDate"] = df["ReferenceDate"].dt.date
    # df["MaturityDate"] = df["MaturityDate"].dt.date
    return df
    # return adjust_pre_rates(df)


@st.cache_data(ttl=28800)  # 8 horas de cache
def load_di_rates() -> pd.DataFrame:
    df = pd.read_csv(DI_DATA_URL, parse_dates=["TradeDate", "ExpirationDate"])
    df.rename(columns={
        'TradeDate': "reference_date",
        'TickerSymbol': 'contract_code',
        'ExpirationDate': 'expiration',
        'BDaysToExp': 'bdays',
        'OpenContracts': 'open_contracts',
        'TradeVolume': 'trading_volume',
        'SettlementPrice': 'settlement_price',
        'SettlementRate': 'settlement_rate'
        }, inplace=True)

    df['settlement_rate'] = df['settlement_rate'] * 100

    df['expiration_mY'] = df['expiration'].dt.strftime('%m-%y')

    return df

def adjust_pre_rates(df_anb: pd.DataFrame) -> pd.DataFrame:
    """Ajusta as taxas pré para o prêmio em relação ao DI."""
    di_df = load_di_rates()
    pre_df = df_anb.query("BondType in ['LTN', 'NTN-F']").copy()
    pre_df = pre_df.merge(
        di_df,
        how="inner",
        left_on=["ReferenceDate", "MaturityDate"],
        right_on=["TradeDate", "ExpirationDate"],
    )
    pre_df["IndicativeRate"] = pre_df["IndicativeRate"] - pre_df["SettlementRate"]
    # Passar para BPS
    pre_df["IndicativeRate"] = (pre_df["IndicativeRate"] * 100).round(2)

    not_pre_df = df_anb.query("BondType not in ['LTN', 'NTN-F']").copy()

    return pd.concat([not_pre_df, pre_df], ignore_index=True)

def get_benchmarks():

    STN_API_URL = {
        tipo_consulta: f"https://apiapex.tesouro.gov.br/aria/v1/api-leiloes-pub/custom/{tipo_consulta}?ano="
        for tipo_consulta in [
            "benchmarks",
            "comunicados",
            "portarias",
            "resultados",
            "dealers",
            "calendario",
            "troca",
        ]
    }

    STN_API_URL['benchmarks']

    stn_benchmarks = requests.get(STN_API_URL["benchmarks"]).json()
    stn_benchmarks['registros'][0]
    df_benchmarks = pd.DataFrame(stn_benchmarks['registros'])
    df_benchmarks['data_refencia'] = pd.Timestamp.today()
    df_benchmarks['data_refencia'] = df_benchmarks['data_refencia'].dt.strftime('%d-%m-%Y')
    df_benchmarks['VENCIMENTO'] = pd.to_datetime(df_benchmarks['VENCIMENTO'])
    df_benchmarks['VENCIMENTO'] = df_benchmarks['VENCIMENTO'].dt.strftime('%d-%m-%Y')
    df_benchmarks['TERMINO'] = pd.to_datetime(df_benchmarks['TERMINO'])
    df_benchmarks['TERMINO'] = df_benchmarks['TERMINO'].dt.strftime('%d-%m-%Y')

    df_benchmarks['VENCIMENTO (em anos)'] = (pyd.bday.count(start=df_benchmarks['data_refencia'], end=df_benchmarks['VENCIMENTO']) / 252).round(2)


    df_benchmarks.drop(columns=['data_refencia'], inplace=True)

    return df_benchmarks
