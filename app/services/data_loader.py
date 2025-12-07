import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/prices.csv")

def load_prices(tickers: list[str]) -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])  # columns: date,ticker,adj_close
    wide = df.pivot(index="date", columns="ticker", values="adj_close").sort_index()
    # garder uniquement les tickers demandés
    cols = [t for t in tickers if t in wide.columns]
    wide = wide[cols].dropna()
    if wide.shape[0] < 3 or len(cols) < 2:
        raise ValueError("Not enough data or tickers")
    return wide


