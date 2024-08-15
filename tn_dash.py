import pandas as pd
import altair as alt
import streamlit as st
import pyield as pyd
from pyield.interpolator import Interpolator
# import config as cfg
from scripts.datetime_selector import dt_selector
from scripts.plotting_functions import chart_curves
from scripts.basic_processing import process_df
from scripts.interpolate_interval import interpolate_rates_for_dates
import titulos


st.markdown(
    """<style>.block-container{max-width: 86rem !important;}</style>""",
    unsafe_allow_html=True,
)

def run_interface():

    # Título do painel
    st.markdown("## Títulos do Tesouro Nacional")
    st.write("---")

    dt_selector()

    st.write("---")
    columns_titulo = st.columns([1,5,1,3])
    columns_titulo[0].markdown(f'### {st.session_state.titulo}')
    if st.session_state.titulo == "NTN-B":
        on = columns_titulo[1].toggle('Retirar as taxas menores do que 6 meses.')

    else:
        on = False

    # bond_list = ["LTN", "NTN-F", "LFT", "NTN-B"]
    columns_containers = st.columns([5,5])
    containers = [columns_containers[i].container(border=True) for i in range(2)]

    df_rates = process_df(
            st.session_state.start_date,
            st.session_state.end_date,
            st.session_state.titulo
            )

    st.write("---")

    column_curves = st.columns([1, 6, 1])
    # df_rates['Date'] = pd.to_datetime(df_rates['Date'], format='%Y-%m-%d')
    # df_rates['Date'] = df_rates['Date'].astype('str')

    # slider_start, slider_end = containers[0].slider(
    #         '',
    #         min_value=df_rates['Days to Expiration'].min(),
    #         max_value=df_rates['Days to Expiration'].max(),
    #         value=(
    #             df_rates['Days to Expiration'].min(),
    #             df_rates['Days to Expiration'].max(),
    #             ),
    #         # format='DD/MM/YYYY'
    #         )

    if on:
        df_rates = df_rates[df_rates['Days to Expiration'] >= 0.5]

    # cl = chart_curves(df_rates[(df_rates['Days to Expiration'] >= slider_start) & (df_rates['Days to Expiration'] <= slider_end)])

    cl = chart_curves(df_rates)
    # column_curves[1].altair_chart(cl, use_container_width=True)

    containers[0].altair_chart(cl, use_container_width=True)

    # st.dataframe(df_rates[['Date', 'Days to Expiration', 'reference_date', 'premio']])
    venc_interp = float(st.session_state.columns_datetime[4].text_input('vencimento interpolação','1'))
    # st.write(df_rates)

    if st.session_state.titulo == 'LTN' or st.session_state.titulo == 'NTN-F':
        df_rates['premio_taxa'] = df_rates['premio'] / 100
    else:
        df_rates['premio_taxa'] = df_rates['IndicativeRate'] / 100

    list_interpolations, list_dates = interpolate_rates_for_dates(df_rates, venc_interp, st.session_state.start_date, st.session_state.end_date)
    df_interpolation = pd.DataFrame({'Date':list_dates, 'premio': list_interpolations})
    df_interpolation['premio'] = df_interpolation['premio'] * 100
    # st.dataframe(df_interpolation)

    # st.write(list_interpolations)

    # containers[1].dataframe(df_rates_vencimentos)
    # st.dataframe(df_rates)

    chart_lines = alt.Chart(df_interpolation, title='Série histórica').mark_line(interpolate='monotone', size=4).encode(
            alt.X('Date', title='Data'),
            alt.Y(
                'premio:Q',
                title='Taxa',
                scale=alt.Scale(
                    domain=[
                        df_interpolation["premio"].min(),
                        df_interpolation["premio"].max(),
                    ],),
                ),
            tooltip = ['Date', 'premio']
            ).properties(width=600, height=520)

    containers[1].altair_chart(chart_lines, use_container_width=False)


    # st.dataframe(df_rates_vencimentos)

def main():
    # init_session()
    run_interface()


if __name__ == "__main__":
    main()

