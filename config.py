import pandas as pd
from pathlib import Path
import pyarrow.feather as feather
from scripts.data_functions import load_di_rates, load_anbima_rates, get_benchmarks

DATA_PATH = Path("__file__").parent / "data"
PYIELD_DATA_URL = "https://raw.githubusercontent.com/crdcj/pyield-data/main/"
ANBIMA_RATES = f"{PYIELD_DATA_URL}anbima_data.parquet"


df_di = load_di_rates()

df_anbima_rates = load_anbima_rates()

try:
    df_benchmarks = get_benchmarks()
except:
    df_benchmarks = pd.DataFrame()
