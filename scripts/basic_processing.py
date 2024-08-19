import pandas as pd
import pyield as pyd
import config as cfg
import streamlit as st

def process_df(start_date, end_date, titulo):

    if titulo == 'DI':
        df_rates = cfg.df_di.copy()

        df_rates.rename(
                columns={
                    'reference_date':'Date',
                    'settlement_rate': 'IndicativeRate',
                    'expiration': 'MaturityDate',
                    },
                inplace=True)

        df_rates = df_rates.query(f"Date >= '{start_date}' and Date <='{end_date}'")

        df_rates.reset_index(drop=True, inplace=True)

        df_rates['Date'] = df_rates['Date'].dt.strftime('%d-%m-%Y')
        df_rates['MaturityDate'] = df_rates['MaturityDate'].dt.strftime('%d-%m-%Y')

        df_rates['Date'] = pd.to_datetime(df_rates['Date'], format='%d-%m-%Y')

        df_rates['Days to Expiration'] = pyd.bday.count(start=df_rates['Date'], end=df_rates['MaturityDate']) / 252

    else:
        df_rates = cfg.df_anbima_rates.copy()

        df_rates.rename(columns={'ReferenceDate':'Date', 'GrossDISpread': 'premio'}, inplace=True)

        df_rates = df_rates.query(f"Date >= '{start_date}' and Date <='{end_date}'")
        df_rates = df_rates.query(f"BondType == '{titulo}'")

        df_rates.reset_index(drop=True, inplace=True)

        df_rates['Date'] = df_rates['Date'].dt.strftime('%d-%m-%Y')
        df_rates['MaturityDate'] = df_rates['MaturityDate'].dt.strftime('%d-%m-%Y')

        df_rates['Date'] = pd.to_datetime(df_rates['Date'], format='%d-%m-%Y')

        df_rates['bdays'] = pyd.bday.count(start=df_rates['Date'], end=df_rates['MaturityDate'])

        df_rates['Days to Expiration'] = pyd.bday.count(start=df_rates['Date'], end=df_rates['MaturityDate']) / 252

    return df_rates

