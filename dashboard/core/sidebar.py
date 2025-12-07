# dashboard/core/sidebar.py
import os
import streamlit as st
from .api import api_post

PRESETS = {
    "60/40 (US Stocks/Bonds)": "SPY,AGG",
    "Global Diversifié": "SPY,EFA,AGG,GLD,VNQ",
    "All Weather (simplifié)": "SPY,AGG,GLD",
}

def render_sidebar():
    st.sidebar.header("🔐 Auth")
    email = st.sidebar.text_input("Email", value=os.getenv("INVESTIQ_EMAIL", ""))
    pwd = st.sidebar.text_input("Password", type="password", value=os.getenv("INVESTIQ_PWD", ""))

    colA, colB = st.sidebar.columns(2)
    if colA.button("Register", use_container_width=True):
        try:
            data = api_post("/auth/register", {"email": email, "password": pwd})
            st.session_state.token = data["access_token"]
            st.sidebar.success("Compte créé & connecté ✅")
        except Exception as e:
            st.sidebar.error(str(e))
    if colB.button("Login", use_container_width=True):
        try:
            data = api_post("/auth/login", {"email": email, "password": pwd})
            st.session_state.token = data["access_token"]
            st.sidebar.success("Connecté ✅")
        except Exception as e:
            st.sidebar.error(str(e))

    if st.session_state.get("token"):
        st.sidebar.success("Token chargé ✅")
    else:
        return

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎛️ Presets rapides")
    chosen = st.sidebar.selectbox("Choisir un preset", list(PRESETS.keys()), index=1)
    if st.sidebar.button("Appliquer preset", use_container_width=True):
        st.session_state.tickers_text = PRESETS[chosen]
    st.sidebar.caption("Tu peux ensuite rajouter/retirer des tickers dans l’onglet Construire.")
