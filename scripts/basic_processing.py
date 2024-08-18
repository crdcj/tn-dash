import pandas as pd
import pyield as pyd
import config as cfg

def process_df(start_date, end_date, titulo):

    df_rates = cfg.df_anbima.copy()
    # df_rates['ReferenceDate'] = df_rates['ReferenceDate'].astype('str')
    # df_rates['MaturityDate'] = df_rates['MaturityDate'].astype('str')

    df_rates.rename(columns={'ReferenceDate':'Date'}, inplace=True)

    df_rates = df_rates.query(f"Date >= '{start_date}' and Date <='{end_date}'")
    df_rates = df_rates.query(f"BondType == '{titulo}'")

    df_rates.reset_index(drop=True, inplace=True)

    df_rates['Date'] = df_rates['Date'].dt.strftime('%d-%m-%Y')
    df_rates['MaturityDate'] = df_rates['MaturityDate'].dt.strftime('%d-%m-%Y')

    df_rates['Date'] = pd.to_datetime(df_rates['Date'], format='%d-%m-%Y')

    df_rates['bdays'] = pyd.bday.count(start=df_rates['Date'], end=df_rates['MaturityDate'])

    df_rates['Days to Expiration'] = pyd.bday.count(start=df_rates['Date'], end=df_rates['MaturityDate']) / 252

    if titulo == 'LTN' or titulo == 'NTN-F':

        # df_rates.rename(columns={'MaturityDate': 'expiration'}, inplace=True)
        df_rates['expiration_mY'] = df_rates['MaturityDate']
        df_rates['expiration_mY'] = pd.to_datetime(df_rates['expiration_mY'], format='%d-%m-%Y')
        df_rates['expiration_mY'] = df_rates['expiration_mY'].dt.strftime('%m-%y')
        # df_rates.rename(columns={'Date':'reference_date'}, inplace=True)
        df_rates['reference_date'] = df_rates['Date']

        df_rates = pd.merge(
                df_rates,
                cfg.df_di[['reference_date', 'expiration_mY', 'settlement_rate']],
                on=['reference_date', 'expiration_mY'],
                how='left'
                )

        df_rates['premio'] = (df_rates['IndicativeRate'] - df_rates['settlement_rate']) * 100

    return df_rates

def update_di_data():
    # Load di data

    df_di = cfg.df_di.copy()

    # Gerar uma série de dias úteis
    start_date = df_di["reference_date"].iloc[-1] - pd.Timedelta(days=1)
    # Today
    end_date = pd.Timestamp("today")
    bdays = pyd.bday.generate(start=start_date, end=end_date)

    if start_date.date() != end_date.date():
        # Get DI date in business_days DatetimeIndex
        processed_dfs = []

        for date in bdays:
            dfp = pyd.futures(contract_code='DI1', reference_date=date)

            processed_dfs.append(dfp)

        dfp = pd.concat(processed_dfs, ignore_index=True)

        column_names = {
            'TradeDate': 'reference_date',
            'TickerSymbol': 'contract_code',
            'ExpirationDate': 'expiration',
            'BDaysToExp': 'bdays',
            'OpenContracts': 'open_contracts',
            'TradeVolume': 'trading_volume',
            'SettlementPrice': 'settlement_price',
            'SettlementRate': 'settlement_rate'
            }

        dfp.rename(columns=column_names, inplace=True)

        dfp = dfp[
            [
                "reference_date",
                "contract_code",
                "expiration",
                "bdays",
                "open_contracts",
                "trading_volume",
                "settlement_price",
                "settlement_rate",
            ]
        ]

        df_di = pd.concat([df_di, dfp], ignore_index=True)

        # multiply by 100 only the values in the column less than 1
        df_di.loc[df_di["settlement_rate"] < 1, "settlement_rate"] *= 100
        df_di.drop_duplicates(inplace=True)
        df_di.reset_index(drop=True, inplace=True)

        df_di.to_feather(cfg.DI_DATA_FILE, compression="zstd")
        cfg.df_di = df_di

