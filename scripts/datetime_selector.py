import streamlit as st
from datetime import timedelta, datetime
import pyield as pyd

def dt_selector():

    end_date = datetime.now()
    input_date = pyd.bday.offset(dates=end_date, offset=-7)

    titulo_list = ["LTN", "NTN-F", "NTN-B", "LFT", 'DI']

    st.session_state.columns_datetime = st.columns([2,2,2,1,4,3,8])

    st.session_state.start_date = (
        st.session_state.columns_datetime[0].date_input("Data de Início", input_date).strftime("%Y-%m-%d")
    )

    st.session_state.end_date = (
        st.session_state.columns_datetime[1].date_input("Data Final", end_date).strftime("%Y-%m-%d")
    )

    st.session_state.titulo = (
        st.session_state.columns_datetime[2].selectbox("Instrumento", titulo_list)
    )

    st.session_state.radio_taxa_1 = st.session_state.columns_datetime[4].radio('tipo', ['taxa', 'prêmio'], horizontal=True)
    if st.session_state.radio_taxa_1 == 'taxa':
        st.session_state.toggle_taxa_1 = True
    else:
        st.session_state.toggle_taxa_1 = False

    if st.session_state.titulo == "NTN-B":
        st.session_state.on = st.session_state.columns_datetime[5].toggle('taxas $< 6$ meses')

    elif st.session_state.titulo == 'NTN-F':
        if not st.session_state.toggle_taxa_1:
            st.session_state.radio_premio_limpo = st.session_state.columns_datetime[5].radio('', ['sujo','limpo'], horizontal=True)
        if st.session_state.radio_premio_limpo == 'limpo':
            st.session_state.toggle_premio_limpo = True
        else:
            st.session_state.toggle_premio_limpo = False

