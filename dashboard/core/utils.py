# dashboard/core/utils.py
import streamlit as st

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
