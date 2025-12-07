# app/routers/assets.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db.database import get_db, Base, engine
from ..models.asset import Asset
from ..core.deps import get_current_user

# Création des tables si nécessaire
Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/assets",
    tags=["assets"]
)

# -------------------------------
#         SCHEMAS (Pydantic)
# -------------------------------

class AssetIn(BaseModel):
    """
    Représente les données nécessaires pour créer un asset.
    """
    ticker: str
    name: str
    asset_class: str


class AssetOut(BaseModel):
    """
    Représentation d’un asset renvoyé au client.
    """
    id: int
    ticker: str
    name: str
    asset_class: str

    class Config:
        from_attributes = True


# -------------------------------
#         ROUTES API
# -------------------------------

@router.get("/", response_model=list[AssetOut], status_code=status.HTTP_200_OK)
def list_assets(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    GET /assets
    Récupère la liste de tous les assets enregistrés.
    (Route protégée par authentification)
    """
    return db.query(Asset).all()


@router.post("/", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
def add_asset(
    payload: AssetIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    POST /assets
    Ajoute un nouvel asset en base si le ticker n’existe pas déjà.
    (Route protégée par authentification)
    """
    # Vérifier l’unicité du ticker
    existing = db.query(Asset).filter(Asset.ticker == payload.ticker).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"L’asset '{payload.ticker}' existe déjà."
        )

    # Création de l’objet Asset
    asset = Asset(**payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)

    return asset
