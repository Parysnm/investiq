import numpy as np
from scipy.optimize import minimize

def min_variance_weights(cov: np.ndarray, max_weight: float = 1.0) -> np.ndarray:
    n = cov.shape[0]
    x0 = np.ones(n) / n

    def objective(w):
        return float(w.T @ cov @ w)

    cons = ({"type": "eq", "fun": lambda w: np.sum(w) - 1.0},)
    bounds = tuple((0.0, max_weight) for _ in range(n))

    res = minimize(objective, x0, bounds=bounds, constraints=cons, method="SLSQP")
    if not res.success:
        raise ValueError("Optimization failed: " + res.message)
    w = res.x
    # project small negatives due to numerical noise
    w[w < 0] = 0
    w = w / w.sum()
    return w

def max_sharpe_weights(mu: np.ndarray, cov: np.ndarray, max_weight: float = 1.0, rf: float = 0.0) -> np.ndarray:
    """
    Maximise (mu_p - rf) / sigma_p sous contraintes:
      - sum w = 1
      - 0 <= w <= max_weight
    mu et cov doivent être annualisés (mu en moyennes, cov sur ret. quotidiens * 252 via l’appelant).
    """
    n = cov.shape[0]
    x0 = np.ones(n) / n

    def neg_sharpe(w):
        port_mu = float(w @ mu)           # déjà annualisé
        port_sigma = float(np.sqrt(w @ cov @ w))  # cov doit être annualisée en amont
        if port_sigma <= 0:
            return 1e6
        return - (port_mu - rf) / port_sigma

    cons = ({"type": "eq", "fun": lambda w: np.sum(w) - 1.0},)
    bounds = tuple((0.0, max_weight) for _ in range(n))
    res = minimize(neg_sharpe, x0, bounds=bounds, constraints=cons, method="SLSQP")
    if not res.success:
        raise ValueError("Optimization failed: " + res.message)
    w = res.x
    w[w < 0] = 0
    w = w / w.sum()
    return w