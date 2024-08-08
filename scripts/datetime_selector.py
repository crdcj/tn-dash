import streamlit as st
from datetime import timedelta, datetime
import pyield as pyd

def dt_selector():

    end_date = datetime.now()
    input_date = pyd.bday.offset(dates=end_date, offset=-7)

    titulo_list = ["LTN", "NTN-F", "NTN-B", "LFT"]

    st.session_state.columns_datetime = st.columns(7)

    st.session_state.start_date = (
        st.session_state.columns_datetime[0].date_input("Data de Início", input_date).strftime("%Y-%m-%d")
    )

    st.session_state.end_date = (
        st.session_state.columns_datetime[1].date_input("Data Final", end_date).strftime("%Y-%m-%d")
    )

    st.session_state.titulo = (
        st.session_state.columns_datetime[3].selectbox("Título", titulo_list)
    )
