import pandas as pd

# Configurações e constantes
RATES_URL = (
    "https://raw.githubusercontent.com/crdcj/pyield-data/main/anbima_rates.csv.gz"
)

df_rates = pd.read_csv(RATES_URL, parse_dates=["ReferenceDate", "MaturityDate"])
