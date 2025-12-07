import numpy as np
import pandas as pd

FREQ = 252  # quotidien → annualisation

def to_log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    prices: DataFrame index=dates, columns=tickers, valeurs=Adj Close
    renvoie les log-returns quotidiens, alignés/propres.
    """
    return np.log(prices / prices.shift(1)).dropna()

def covariance_matrix(returns: pd.DataFrame) -> np.ndarray:
    """
    Matrice de covariance quotidienne (alignée sur l'ordre des colonnes).
    """  
    return returns.cov().values

def mean_returns(returns: pd.DataFrame) -> np.ndarray:
    """
    Moyenne quotidienne par actif (arithmétique).
    Renvoie un vecteur numpy aligné sur l'ordre des colonnes.
    """
    return returns.mean().values

def portfolio_metrics(weights: np.ndarray, returns: pd.DataFrame) -> dict:
    """
    Calcule mu_ann, vol_ann, sharpe pour un portefeuille donné.
    - weights: vecteur (somme=1) aligné sur rets.columns
    - rets: log-returns quotidiens
    - rf_ann: taux sans risque annualisé (optionnel, pour afficher un Sharpe ajusté)
    """
    mu = (returns @ weights).mean() * FREQ
    sigma = (returns @ weights).std() * np.sqrt(FREQ)
    sharpe = mu / sigma if sigma > 0 else 0.0
    return {"mu_ann": float(mu), "vol_ann": float(sigma), "sharpe": float(sharpe)}
