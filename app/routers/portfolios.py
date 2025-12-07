# app/routers/portfolios.py

import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..db.database import get_db, Base, engine
from ..models.portfolio import Portfolio

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


# --------- Schemas Pydantic ---------

class PortfolioCreate(BaseModel):
    name: str
    tickers: List[str]
    weights: List[float]
    metrics: Optional[dict] = None

    @field_validator("tickers")
    @classmethod
    def tickers_non_empty(cls, v: List[str]):
        if not v:
            raise ValueError("La liste des tickers ne doit pas être vide.")
        return v

    @field_validator("weights")
    @classmethod
    def weights_non_empty(cls, v: List[float]):
        if not v:
            raise ValueError("La liste des poids ne doit pas être vide.")
        return v

    @field_validator("weights")
    @classmethod
    def validate_weights_sum_to_one(cls, weights, info):
        """
        Validator Pydantic v2 pour vérifier :
        - même longueur tickers / weights
        - somme des poids ≈ 1
        """
        tickers = info.data.get("tickers") or []

        if len(tickers) != len(weights):
            raise ValueError("tickers et weights doivent avoir la même longueur.")

        total = sum(weights)
        if not (0.99 <= total <= 1.01):
            raise ValueError("La somme des poids doit être ≈ 1.")

        return weights


class PortfolioOut(BaseModel):
    id: int
    name: str
    tickers: List[str]
    weights: List[float]
    metrics: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PortfolioDeleteOut(BaseModel):
    id: int
    deleted: bool


# --------- Routes ---------

@router.post("/", response_model=PortfolioOut, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    payload: PortfolioCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    db_obj = Portfolio(
        user_id=user.id,
        name=payload.name,
        tickers=json.dumps(payload.tickers),
        weights=json.dumps(payload.weights),
        metrics=json.dumps(payload.metrics) if payload.metrics is not None else None,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    return PortfolioOut(
        id=db_obj.id,
        name=db_obj.name,
        tickers=payload.tickers,
        weights=payload.weights,
        metrics=payload.metrics,
        created_at=db_obj.created_at,
    )


@router.get("/", response_model=List[PortfolioOut])
def list_portfolios(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    rows = (
        db.query(Portfolio)
        .filter(Portfolio.user_id == user.id)
        .order_by(Portfolio.created_at.desc())
        .all()
    )

    out: List[PortfolioOut] = []
    for p in rows:
        out.append(
            PortfolioOut(
                id=p.id,
                name=p.name,
                tickers=json.loads(p.tickers),
                weights=json.loads(p.weights),
                metrics=json.loads(p.metrics) if p.metrics else None,
                created_at=p.created_at,
            )
        )
    return out


@router.delete("/{portfolio_id}", response_model=PortfolioDeleteOut)
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    p = (
        db.query(Portfolio)
        .filter(Portfolio.id == portfolio_id, Portfolio.user_id == user.id)
        .first()
    )
    if not p:
        raise HTTPException(status_code=404, detail="Portefeuille introuvable.")

    db.delete(p)
    db.commit()
    return PortfolioDeleteOut(id=portfolio_id, deleted=True)
