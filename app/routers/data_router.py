from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from datetime import date
from typing import Literal
from ..core.deps import get_current_user
from ..services.market_data import fetch_prices, upsert_prices_csv

router = APIRouter(prefix="/data", tags=["data"])

class UpdatePricesIn(BaseModel):
    tickers: list[str]
    start: date
    end: date | None = None
    source: Literal["auto","yahoo","stooq"] = "auto"

    @field_validator("tickers")
    @classmethod
    def non_empty(cls, v):
        if not v:
            raise ValueError("tickers must be non-empty")
        return v

@router.post("/update")
def update_prices(payload: UpdatePricesIn, user=Depends(get_current_user)):
    try:
        df_long = fetch_prices(
            tickers=payload.tickers,
            start=str(payload.start),
            end=str(payload.end) if payload.end else None,
            source=payload.source,
        )
        if df_long is None or df_long.empty:
            raise HTTPException(
                status_code=424,
                detail=("Aucune donnée reçue (yahoo/stooq). "
                        "Vérifie la source, les tickers, la période ou le réseau.")
            )
        upsert_prices_csv(df_long)
        return {
            "rows_added": int(len(df_long)),
            "tickers": sorted(df_long["ticker"].unique().tolist()),
            "date_min": str(min(df_long["date"])),
            "date_max": str(max(df_long["date"]))
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"update failed: {e}")
