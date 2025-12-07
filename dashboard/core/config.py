# dashboard/core/config.py
import os
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

def setup_page():
    st.set_page_config(page_title="InvestIQ — Portfolio Assistant", layout="wide")
    # init session defaults
    if "token" not in st.session_state:
        st.session_state.token = None
    if "tickers_text" not in st.session_state:
        st.session_state.tickers_text = "SPY,EFA,AGG,GLD,VNQ"
