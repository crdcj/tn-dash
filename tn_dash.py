import pandas as pd
import plotly.express as px
import streamlit as st

# Configurações e constantes
RATES_URL = (
    "https://raw.githubusercontent.com/crdcj/pyield-data/main/anbima_rates.csv.gz"
)

df = pd.read_csv(RATES_URL, parse_dates=["ReferenceDate", "MaturityDate"])

# Título do painel
st.markdown("## Títulos do Tesouro Nacional")

# Determinar a última data disponível no conjunto de dados
last_date = df["ReferenceDate"].max().date()

# Criar colunas para os campos
col1, col2, col3 = st.columns(3)

# Campo de data de referência
with col1:
    selected_reference_date = st.date_input(
        "Data de referência", value=last_date, format="DD/MM/YYYY"
    )

# Filtrar os dados com base na data de referência selecionada
available_bonds = df[df["ReferenceDate"].dt.date == selected_reference_date]

# Filtro por tipo de título
bond_types = available_bonds["BondType"].unique()
with col2:
    selected_bond_type = st.selectbox("Tipo de título", bond_types)

# Filtro por data de vencimento baseado no tipo de título selecionado
maturity_dates = (
    available_bonds[available_bonds["BondType"] == selected_bond_type]["MaturityDate"]
    .dt.strftime("%d/%m/%Y")
    .unique()
)
with col3:
    selected_maturity_date = st.selectbox("Data de vencimento", maturity_dates)

# Converter a data de vencimento selecionada para datetime
selected_maturity_date = pd.to_datetime(selected_maturity_date, format="%d/%m/%Y")

# Filtrar os dados para o gráfico
filtered_df = df[
    (df["BondType"] == selected_bond_type)
    & (df["MaturityDate"] == selected_maturity_date)
]

# Gráfico de taxas indicativas ao longo do tempo
fig = px.line(
    filtered_df,
    x="ReferenceDate",
    y="IndicativeRate",
    title=f"Taxas Indicativas da {selected_bond_type} com vencimento em {selected_maturity_date.strftime('%d/%m/%Y')}",
    labels={"IndicativeRate": "Taxa Indicativa (%)", "ReferenceDate": "Data"},
)

# Configurar o eixo X
fig.update_layout(
    xaxis=dict(showgrid=True, tickformat="%Y", dtick="M12"),
    xaxis_title="Data",
)

st.plotly_chart(fig)
