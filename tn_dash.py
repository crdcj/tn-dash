import pandas as pd
import altair as alt
import streamlit as st
import pyield as pyd
from pyield.interpolator import Interpolator
import config as cfg
from scripts.datetime_selector import dt_selector
from scripts.plotting_functions import chart_curves, chart_lines
from scripts.basic_processing import process_df
from scripts.interpolate_interval import interpolate_rates_for_dates


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

    columns_containers = st.columns([5,5])
    containers = [columns_containers[i].container(border=True, height=700) for i in range(2)]
     
# --------------- Container 1 -----------------------------

    containers_painel_1 = [containers[0].container(border=False) for i in range(2)]
    # containers[0].write('Curvas')

    columns_painel_1 = containers_painel_1[1].columns([2,8])

    df_rates = process_df(
            st.session_state.start_date,
            st.session_state.end_date,
            st.session_state.titulo
            )

    st.write("---")

    column_curves = st.columns([1, 6, 1])

    if st.session_state.on:
        df_rates = df_rates[df_rates['Days to Expiration'] >= 0.5]

    cl = chart_curves(df_rates, st.session_state.toggle_taxa_1, st.session_state.toggle_premio_limpo)

    containers_painel_1[0].altair_chart(cl, use_container_width=True)

# --------------- Container 2 -----------------------------

    containers_painel_2 = [containers[1].container(border=False) for i in range(2)]

    columns_painel_2 = containers_painel_2[1].columns(3)

    list_venc_interp = []

    venc_interp = float(columns_painel_2[0].text_input('Vértices de referência (em anos)','1.5').replace(',','.'))
    if venc_interp == int(venc_interp):
        venc_interp = int(venc_interp)
    list_venc_interp.append(venc_interp)
    venc_interp_2 = float(columns_painel_2[1].text_input('','0').replace(',', '.'))
    if venc_interp_2 == int(venc_interp_2):
        venc_interp_2 = int(venc_interp_2)
    venc_interp_3 = float(columns_painel_2[2].text_input(' ','0').replace(',', '.'))
    if venc_interp_3 == int(venc_interp_3):
        venc_interp_3 = int(venc_interp_3)


    if st.session_state.titulo == 'LTN' or st.session_state.titulo == 'NTN-F':
        if st.session_state.toggle_taxa_1:
            df_rates['premio_taxa'] = df_rates['IndicativeRate'] / 100
        else:
            if st.session_state.titulo == 'NTN-F':
                if st.session_state.toggle_premio_limpo:
                    df_rates['premio_taxa'] = df_rates['NetDISpread'] / 100
                else:
                    df_rates['premio_taxa'] = df_rates['premio'] / 100

            else:
                df_rates['premio_taxa'] = df_rates['premio'] / 100
    elif st.session_state.titulo == 'NTN-B':
        df_rates['premio_taxa'] = df_rates['IndicativeRate'] / 100

    elif st.session_state.titulo == 'LFT':
        df_rates['premio_taxa'] = df_rates['IndicativeRate'] / 100

    elif st.session_state.titulo == 'DI':
        df_rates['premio_taxa'] = df_rates['IndicativeRate'] / 100

    list_interpolations, list_dates = interpolate_rates_for_dates(df_rates, venc_interp, st.session_state.start_date, st.session_state.end_date)
    df_interpolation = pd.DataFrame({'Date':list_dates, 'premio': list_interpolations})
    df_interpolation['premio'] = df_interpolation['premio'] * 100
    df_interpolation['vertice'] = str(venc_interp)

    if venc_interp_2 > 0:
        list_venc_interp.append(venc_interp_2)
        list_interpolations, list_dates = interpolate_rates_for_dates(df_rates, venc_interp_2, st.session_state.start_date, st.session_state.end_date)
        df_temp = pd.DataFrame({'Date':list_dates, 'premio': list_interpolations})
        df_temp['premio'] = df_temp['premio'] * 100
        df_temp['vertice'] = str(venc_interp_2)

        df_interpolation = pd.concat([df_interpolation, df_temp])

    if venc_interp_3 > 0:
        list_venc_interp.append(venc_interp_3)
        list_interpolations, list_dates = interpolate_rates_for_dates(df_rates, venc_interp_3, st.session_state.start_date, st.session_state.end_date)
        df_temp = pd.DataFrame({'Date':list_dates, 'premio': list_interpolations})
        df_temp['premio'] = df_temp['premio'] * 100
        df_temp['vertice'] = str(venc_interp_3)

        df_interpolation = pd.concat([df_interpolation, df_temp])


    columns_toggle = containers_painel_2[1].columns(3)
    toggle_bps = columns_toggle[0].toggle('variação em bps')

    if toggle_bps:
        df_interpolation = df_interpolation.sort_values(by=['vertice', 'Date'])

    # Define a function to calculate the basis point change
    def calculate_basis_point_change(group):
        # Get the 'premio' value of the first date
        reference_premio = group['premio'].iloc[0]
        # Calculate the change in 'premio' relative to the reference
        if st.session_state.toggle_taxa_1:
            group['basis_point_change'] = (group['premio'] - reference_premio) * 100
        else:
            if st.session_state.titulo == 'NTN-B' or st.session_state.titulo == 'LFT':
                group['basis_point_change'] = (group['premio'] - reference_premio) * 100
            else:
                group['basis_point_change'] = (group['premio'] - reference_premio)

        return group

    # Group by 'vertice' and apply the function to each group
    df_interpolation = df_interpolation.groupby('vertice').apply(calculate_basis_point_change).reset_index(drop=True)

    
    chart_interpolation = chart_lines(df_interpolation, list_venc_interp, st.session_state.toggle_taxa_1, em_bps=toggle_bps)
    containers_painel_2[0].altair_chart(chart_interpolation, use_container_width=False)

    if cfg.df_benchmarks.empty:
        pass
    else:
        with st.expander('Títulos On-the-Run'):
            if st.session_state.titulo == 'DI':
                st.dataframe(cfg.df_benchmarks)

            else:
                st.dataframe(cfg.df_benchmarks[cfg.df_benchmarks['BENCHMARK'].str.contains(st.session_state.titulo)].reset_index(drop=True))


def init_session():
    if 'on' not in st.session_state:
        st.session_state.on = False

    if 'toggle_premio_limpo' not in st.session_state:
        st.session_state.toggle_premio_limpo = False

def main():
    init_session()
    run_interface()


if __name__ == "__main__":
    main()

