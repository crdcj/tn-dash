import pandas as pd
import altair as alt
import streamlit as st
import pyield as pyd
import config as cfg
from scripts.datetime_selector import dt_selector
from scripts.plotting_functions import chart_curves


st.markdown(
    """<style>.block-container{max-width: 86rem !important;}</style>""",
    unsafe_allow_html=True,
)

def run_interface():

    # Título do painel
    st.markdown("## Títulos do Tesouro Nacional")

    dt_selector()

    bond_list = ["LTN", "NTN-F", "LFT", "NTN-B"]
    columns_containers = st.columns([6,4])
    containers = [columns_containers[i].container(border=True) for i in range(2)]

    df_rates = cfg.df_rates.copy()
    # df_rates['ReferenceDate'] = df_rates['ReferenceDate'].astype('str')
    # df_rates['MaturityDate'] = df_rates['MaturityDate'].astype('str')

    df_rates.rename(columns={'ReferenceDate':'Date'}, inplace=True)

    df_rates = df_rates.query(f"Date >= '{st.session_state.start_date}' and Date <='{st.session_state.end_date}'")
    df_rates = df_rates.query(f"BondType == '{st.session_state.titulo}'")

    df_rates.reset_index(drop=True, inplace=True)

    df_rates['Date'] = df_rates['Date'].dt.strftime('%d-%m-%Y')
    df_rates['MaturityDate'] = df_rates['MaturityDate'].dt.strftime('%d-%m-%Y')

    df_rates['Date'] = pd.to_datetime(df_rates['Date'], format='%d-%m-%Y')

    df_rates['Days to Expiration'] = pyd.bday.count(start=df_rates['Date'], end=df_rates['MaturityDate']) / 252

    # df_rates["Date"] = df_rates["Date"].dt.strftime("%Y/%m/%d")

    column_curves = st.columns([1, 6, 1])

    cl = chart_curves(df_rates)
    # column_curves[1].altair_chart(cl, use_container_width=True)
    containers[0].altair_chart(cl, use_container_width=True)

    # st.dataframe(df_rates)

    # sel_vencimento = st.session_state.columns_datetime[5].selectbox('Vencimento',df_rates['MaturityDate'].unique())

    # chart_venc = alt.Chart(df_rates.query(f'MaturityDate == "{sel_vencimento}"')).mark_line().encode(alt.X('Date:T'), alt.Y('IndicativeRate', scale = alt.Scale(domain=[df_rates.query(f'MaturityDate == "{sel_vencimento}"')['IndicativeRate'].min(), df_rates.query(f'MaturityDate == "{sel_vencimento}"')['IndicativeRate'].max()]))).properties(width=300, height=300)

    # st.session_state.columns_titulo = st.columns(7)
    # st.session_state.titulo = (
    #     st.session_state.columns_titulo[0].selectbox("Título", ['LTN', "NTN-F", "NTN-B", "LFT"])
    # )

    # chart_venc = (
    #         alt.Chart(df_rates).mark_line(interpolate='basis').encode(
    #             alt.X('Date:T'),
    #             alt.Y(
    #                 'IndicativeRate',
    #                 scale=alt.Scale(
    #                     domain=[
    #                         df_rates['IndicativeRate'].min(),
    #                         df_rates['IndicativeRate'].max()
    #                         ]
    #                     )
    #                 ),
    #             facet=alt.Facet('MaturityDate').columns(5)
    #             ).properties(
    #                 width=150,
    #                 height=150
    #                 )
    #         )
    #
    # column_lines = st.columns([5, 1, 5])
    # column_lines[0].altair_chart(chart_venc, use_container_width=False)



def main():
    # init_session()
    run_interface()


if __name__ == "__main__":
    main()

