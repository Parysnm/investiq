from __future__ import annotations
from pathlib import Path
import time
from typing import List, Literal
import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr  # Stooq

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CSV_PATH = DATA_DIR / "prices.csv"

def _pick_price_table(raw: pd.DataFrame) -> pd.DataFrame:
    if raw is None or raw.empty:
        return pd.DataFrame()
    cols = raw.columns
    if isinstance(cols, pd.MultiIndex):
        lvl0 = cols.get_level_values(0)
        # yfinance récents: Price -> Close
        if "Price" in set(lvl0):
            pb = raw["Price"]
            if "Close" in pb.columns:
                return pb["Close"]
        # anciens: Adj Close puis Close
        if "Adj Close" in set(lvl0):
            return raw.xs("Adj Close", axis=1, level=0, drop_level=True)
        if "Close" in set(lvl0):
            return raw.xs("Close", axis=1, level=0, drop_level=True)
        return pd.DataFrame()
    # mono-ticker
    for c in ("Adj Close","Close","Price"):
        if c in raw.columns:
            s = raw[c]
            return s.to_frame("TICKER") if not isinstance(s, pd.DataFrame) else s
    if raw.shape[1] == 1:
        return raw
    return pd.DataFrame()

def _yf_download(tickers: List[str], start: str, end: str | None) -> pd.DataFrame:
    try:
        raw = yf.download(
            tickers, start=start, end=end,
            interval="1d", progress=False,
            group_by="column", threads=False  # calmer le rate-limit
        )
        return _pick_price_table(raw)
    except Exception:
        return pd.DataFrame()

def _stooq_download(tickers: List[str], start: str, end: str | None) -> pd.DataFrame:
    frames = []
    for t in tickers:
        try:
            df = pdr.DataReader(t, "stooq", start=start, end=end)
            if "Close" in df.columns:
                frames.append(df["Close"].sort_index().to_frame(t))
        except Exception:
            pass
        time.sleep(0.4)  # doux avec Stooq
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, axis=1)

def fetch_prices(
    tickers: list[str],
    start: str,
    end: str | None = None,
    source: Literal["auto","yahoo","stooq"]="auto",
) -> pd.DataFrame:
    """
    Retourne un DataFrame long: [date, ticker, adj_close]
    source:
      - "yahoo": force yfinance (peut 429)
      - "stooq": force Stooq (EOD)
      - "auto": essaie Yahoo puis fallback Stooq
    """
    if not tickers:
        raise ValueError("No tickers provided")
    tickers = [t.strip().upper() for t in tickers if t.strip()]

    wide = pd.DataFrame()
    if source in ("auto","yahoo"):
        wide = _yf_download(tickers, start, end)
    if (wide is None or wide.empty) and source in ("auto","stooq"):
        wide = _stooq_download(tickers, start, end)

    if wide is None or wide.empty:
        return pd.DataFrame(columns=["date","ticker","adj_close"])

    long_df = (wide.sort_index()
                    .stack()
                    .reset_index())
    long_df.columns = ["date","ticker","adj_close"]
    long_df["date"] = pd.to_datetime(long_df["date"]).dt.date
    long_df = long_df.dropna(subset=["adj_close"])
    return long_df

def upsert_prices_csv(new_long_df: pd.DataFrame) -> None:
    if new_long_df is None or new_long_df.empty:
        return
    if CSV_PATH.exists():
        old = pd.read_csv(CSV_PATH, parse_dates=["date"])
        old["date"] = old["date"].dt.date
        combined = pd.concat([old, new_long_df], ignore_index=True)
    else:
        combined = new_long_df.copy()
    combined = (combined
                .drop_duplicates(subset=["date","ticker"], keep="last")
                .sort_values(["date","ticker"]))
    combined.to_csv(CSV_PATH, index=False)
