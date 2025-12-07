from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import numpy as np
from ..core.deps import get_current_user
from ..services.data_loader import load_prices
from ..services.metrics import to_log_returns, covariance_matrix, portfolio_metrics, mean_returns,FREQ
from ..services.optimizer import min_variance_weights, max_sharpe_weights

router = APIRouter(prefix="/optimize", tags=["optimize"])

class OptimizeIn(BaseModel):
    tickers: list[str]
    max_weight: float = 0.6

class OptimizeSharpeIn(OptimizeIn):
    risk_free: float = 0.0  # taux sans risque annualisé

class AllocationOut(BaseModel):
    ticker: str
    weight: float

class OptimizeOut(BaseModel):
    allocations: list[AllocationOut]
    metrics: dict

@router.post("/min-variance", response_model=OptimizeOut)
def optimize_min_variance(payload: OptimizeIn, user=Depends(get_current_user)):
    try:
        prices = load_prices(payload.tickers)
        rets = to_log_returns(prices)
        cov = covariance_matrix(rets)
        w = min_variance_weights(cov, max_weight=payload.max_weight)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    alloc = [AllocationOut(ticker=t, weight=float(w[i])) for i, t in enumerate(prices.columns)]
    mets = portfolio_metrics(np.array(w), rets)
    return OptimizeOut(allocations=alloc, metrics=mets)

@router.post("/max-sharpe", response_model=OptimizeOut)
def optimize_max_sharpe(payload: OptimizeSharpeIn, user=Depends(get_current_user)):
    try:
        prices = load_prices(payload.tickers)
        rets = to_log_returns(prices)
        mu_daily = mean_returns(rets)
        cov_daily = covariance_matrix(rets)
        # annualiser
        mu_ann = mu_daily * FREQ
        cov_ann = cov_daily * FREQ
        w = max_sharpe_weights(mu_ann, cov_ann, max_weight=payload.max_weight, rf=payload.risk_free)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    alloc = [AllocationOut(ticker=t, weight=float(w[i])) for i, t in enumerate(prices.columns)]
    mets = portfolio_metrics(np.array(w), rets)  # retourne mu_ann, vol_ann, sharpe
    return OptimizeOut(allocations=alloc, metrics=mets)
