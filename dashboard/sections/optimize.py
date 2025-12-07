# dashboard/sections/optimize.py
import pandas as pd
import streamlit as st
import plotly.express as px
from core.api import api_post
from core.utils import tickers_from_str

def render_optimize():
    st.subheader("2) Optimiser l’allocation")
    st.write("Choisis l’objectif et les contraintes. L’allocation est calculée à partir des prix téléchargés à l’étape 1.")

    colL, colR = st.columns([1,1])
    with colL:
        tickers = tickers_from_str(st.session_state.tickers_text)
        st.write("**Tickers sélectionnés** :", ", ".join(tickers) if tickers else "—")
        objective = st.radio("Objectif", ["Max Sharpe", "Min Variance"], index=0, horizontal=True)
        max_weight = st.slider("Poids max par actif", 0.10, 1.00, 0.60, 0.05)
        rf = st.number_input("Taux sans risque (annualisé)", min_value=0.0, max_value=0.1, value=0.02, step=0.005, format="%.3f")
        go = st.button("Calculer l’allocation optimale", type="primary")
    with colR:
        st.info("**Guide rapide**\n\n- *Max Sharpe* : meilleur compromis rendement/risque.\n- *Min Variance* : risque minimal.\n- *Poids max* : limite par actif pour éviter la concentration.\n- *Taux sans risque* : 0.02 = 2%/an.")

    if go:
        try:
            if objective == "Max Sharpe":
                payload = {"tickers": tickers, "max_weight": float(max_weight), "risk_free": float(rf)}
                res = api_post("/optimize/max-sharpe", payload, token=st.session_state.token)
            else:
                payload = {"tickers": tickers, "max_weight": float(max_weight)}
                res = api_post("/optimize/min-variance", payload, token=st.session_state.token)

            alloc = pd.DataFrame(res["allocations"])
            mets = res["metrics"]
            st.session_state.last_alloc = alloc
            st.session_state.last_mets = mets

            st.markdown("### Allocation proposée")
            fig = px.pie(alloc, names="ticker", values="weight", hole=0.35)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(alloc.style.format({"weight": "{:.2%}"}), use_container_width=True)

            st.markdown("### Métriques (annualisées)")
            st.json({k: round(v, 4) for k, v in mets.items()})
        except Exception as e:
            st.error(str(e))
