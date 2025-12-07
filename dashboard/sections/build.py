# dashboard/sections/build.py
from datetime import date
import streamlit as st
from core.api import api_post
from core.utils import tickers_from_str

def render_build():
    st.subheader("1) Construire ton univers d’actifs")
    st.write("Saisis les tickers (ETF/actions) séparés par des virgules. Choisis la source et la période, puis télécharge les prix.")

    tickers_text = st.text_input("Tickers", value=st.session_state.tickers_text)
    cL, cR = st.columns(2)
    with cL:
        start = st.date_input("Start", value=date(2024, 1, 1))
    with cR:
        end = st.date_input("End (optionnel)", value=None)

    source = st.selectbox("Source", options=["auto", "yahoo", "stooq"], index=0)

    if st.button("📥 Mettre à jour les prix"):
        try:
            body = {
                "tickers": tickers_from_str(tickers_text),
                "start": str(start),
                "end": str(end) if end else None,
                "source": source,
            }
            res = api_post("/data/update", body, token=st.session_state.token)
            st.success(f"Données mises à jour ✅  ({res['date_min']} → {res['date_max']})")
            st.json(res)
            st.session_state.tickers_text = tickers_text
        except Exception as e:
            st.error(str(e))

    st.caption("Astuce : commence avec 3–6 ETF max. Tu pourras élargir ensuite.")
