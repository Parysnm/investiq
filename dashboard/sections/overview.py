# dashboard/sections/overview.py
import streamlit as st
import plotly.express as px
from core.utils import kpi_card, pretty_percent

def render_overview():
    st.subheader("Vue d’ensemble du portefeuille")
    st.caption("Commence dans **Construire** si c’est ta première fois, puis reviens ici après optimisation/backtest.")

    col1, col2 = st.columns([1, 1])

    with col1:
        alloc_df = st.session_state.get("last_alloc")
        if alloc_df is not None and not alloc_df.empty:
            st.markdown("**Allocation courante**")
            fig = px.pie(alloc_df, names="ticker", values="weight", hole=0.35)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(alloc_df.style.format({"weight": "{:.2%}"}), use_container_width=True)
        else:
            st.info("Aucune allocation calculée pour l’instant. Va dans **Optimiser** pour en générer une.")

    with col2:
        stats = st.session_state.get("last_stats")
        if stats:
            st.markdown("**Indicateurs clés**")
            c1, c2, c3 = st.columns(3)
            kpi_card("CAGR", pretty_percent(stats.get("cagr", float("nan"))), "Rendement annualisé composé.")
            kpi_card("Sharpe", f"{stats.get('sharpe', float('nan')):.2f}", "Rendement / Risque (annualisé).")
            kpi_card("Max Drawdown", pretty_percent(stats.get("mdd", float("nan"))), "Perte max depuis un pic.")
        else:
            st.info("Aucun backtest n’a été exécuté. Va dans **Backtest** pour visualiser la courbe et les KPI.")
