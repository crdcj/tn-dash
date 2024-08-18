import datetime as dt
import pandas as pd
import streamlit as st
from pyield import bday
from pytz import timezone

# Constantes comuns (se necessário)
TIMEZONE_BZ = timezone("America/Sao_Paulo")
PYIELD_DATA_URL = "https://raw.githubusercontent.com/crdcj/pyield-data/main/"
ANBIMA_RATES_URL = f"{PYIELD_DATA_URL}anbima_rates.csv.gz"
DI_DATA_URL = f"{PYIELD_DATA_URL}di_data.csv.gz"


@st.cache_data(ttl=28800)  # 8 horas de cache
def load_anbima_rates() -> pd.DataFrame:
    df = pd.read_csv(ANBIMA_RATES_URL, parse_dates=["ReferenceDate", "MaturityDate"])
    # Convert columns to datetime.date
    # df["ReferenceDate"] = df["ReferenceDate"].dt.date
    # df["MaturityDate"] = df["MaturityDate"].dt.date
    return df
    # return adjust_pre_rates(df)


@st.cache_data(ttl=28800)  # 8 horas de cache
def load_di_rates() -> pd.DataFrame:
    df = pd.read_csv(DI_DATA_URL, parse_dates=["TradeDate", "ExpirationDate"])
    # keep_columns = ["TradeDate", "ExpirationDate", "SettlementRate"]
    # df = df[keep_columns].copy()
    # # Convert columns to datetime.date
    # df["TradeDate"] = df["TradeDate"].dt.date
    # df["SettlementRate"] = (df["SettlementRate"] * 100).round(3)
    #
    # df["ExpirationDate"] = df["ExpirationDate"].apply(lambda x: x.replace(day=1))
    # df["ExpirationDate"] = df["ExpirationDate"].dt.date
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
