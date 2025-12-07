# dashboard/app.py
import os, json
import requests
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
st.set_page_config(page_title="InvestIQ — Portfolio Assistant", layout="wide")

# ----------------- Helpers -----------------
def api_post(path, payload=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.post(f"{API_BASE}{path}", json=payload or {}, headers=headers, timeout=90)
    if r.status_code >= 400:
        raise RuntimeError(f"{path} → {r.status_code}: {r.text}")
    return r.json()

def tickers_from_str(s: str) -> list[str]:
    return [t.strip().upper() for t in s.split(",") if t.strip()]

def pretty_percent(x: float) -> str:
    try:
        return f"{x*100:.2f}%"
    except Exception:
        return "-"

def kpi_card(label: str, value: str, help_txt: str = ""):
    st.markdown(
        f"""
        <div style="padding:14px;border-radius:14px;background:#111317;border:1px solid #23262d">
          <div style="font-size:13px;color:#9aa4b2">{label}</div>
          <div style="font-size:24px;font-weight:700;margin-top:4px">{value}</div>
          <div style="font-size:11px;color:#778090;margin-top:6px">{help_txt}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------- Sidebar (Auth + Presets) -----------------
st.sidebar.header("🔐 Auth")
email = st.sidebar.text_input("Email", value=os.getenv("INVESTIQ_EMAIL",""))
pwd = st.sidebar.text_input("Password", type="password", value=os.getenv("INVESTIQ_PWD",""))
if "token" not in st.session_state:
    st.session_state.token = None

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

if not st.session_state.token:
    st.stop()

st.sidebar.success("Token chargé ✅")

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Presets rapides")
PRESETS = {
    "60/40 (US Stocks/Bonds)": "SPY,AGG",
    "Global Diversifié": "SPY,EFA,AGG,GLD,VNQ",
    "All Weather (simplifié)": "SPY,AGG,GLD",
}
chosen = st.sidebar.selectbox("Choisir un preset", list(PRESETS.keys()), index=1)
if "tickers_text" not in st.session_state:
    st.session_state.tickers_text = PRESETS[chosen]
if st.sidebar.button("Appliquer preset", use_container_width=True):
    st.session_state.tickers_text = PRESETS[chosen]
st.sidebar.caption("Tu peux ensuite rajouter/retirer des tickers dans l’onglet Construire.")

# ----------------- Header -----------------
st.markdown("# 💼 InvestIQ — Portfolio Assistant")
st.caption("Guidé en 3 étapes : **Construire** ton univers d'actifs → **Optimiser** l'allocation → **Backtester** la performance.")

# ----------------- Onglets -----------------
tab_overview, tab_build, tab_opt, tab_bt = st.tabs(["Vue d’ensemble", "Construire", "Optimiser", "Backtest"])

# ========== VUE D’ENSEMBLE ==========
with tab_overview:
    st.subheader("Vue d’ensemble du portefeuille")
    st.caption("Commence dans l’onglet **Construire** si c’est ta première fois, puis reviens ici après optimisation / backtest.")

    # Afficher derniers résultats s'ils existent en session
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

# ========== CONSTRUIRE ==========
with tab_build:
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

# ========== OPTIMISER ==========
with tab_opt:
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

# ========== BACKTEST ==========
with tab_bt:
    st.subheader("3) Backtest")
    st.write("Teste la stratégie dans le passé pour voir la régularité, le drawdown et le Sharpe.")
    tickers = tickers_from_str(st.session_state.tickers_text)

    col1, col2, col3 = st.columns(3)
    method = col1.selectbox("Méthode", ["max-sharpe", "min-variance", "custom weights"], index=0)
    rebalance = col2.selectbox("Rebalancing", ["M", "Q", "A", "None"], index=0)
    rb = None if rebalance == "None" else rebalance
    custom_weights = None
    if method == "custom weights":
        w_str = col3.text_input("Poids custom (somme≈1)", placeholder="ex: 0.4,0.3,0.2,0.1")
        if w_str:
            try:
                custom_weights = [float(x.strip()) for x in w_str.split(",") if x.strip()]
            except Exception:
                st.warning("Format de poids invalide.")

    run_bt = st.button("▶️ Lancer le backtest", type="primary")
    if run_bt:
        try:
            body = {"tickers": tickers, "rebalance": rb, "max_weight": 0.60, "risk_free": 0.02}
            if method == "custom weights":
                body["weights"] = custom_weights
            else:
                body["method"] = method

            res = api_post("/backtest/run", body, token=st.session_state.token)
            eq = pd.DataFrame(res["equity"])
            eq["date"] = pd.to_datetime(eq["date"])
            eq = eq.set_index("date").sort_index()

            st.markdown("### Évolution du portefeuille (base 1.0)")
            fig = px.line(eq, x=eq.index, y="value", labels={"value":"Equity"})
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Indicateurs clés")
            stats = res["stats"]
            st.session_state.last_stats = stats
            c1, c2, c3 = st.columns(3)
            with c1: kpi_card("CAGR", pretty_percent(stats["cagr"]), "Rendement annualisé composé.")
            with c2: kpi_card("Sharpe", f"{stats['sharpe']:.2f}", "Rendement / Risque (annualisé).")
            with c3: kpi_card("Max Drawdown", pretty_percent(stats["mdd"]), "Perte max depuis un pic.")
        except Exception as e:
            st.error(str(e))
