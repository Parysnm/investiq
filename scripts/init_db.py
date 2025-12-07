# scripts/init_db.py

from sqlalchemy.orm import Session

from app.db.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.asset import Asset
from app.models.portfolio import Portfolio


def init_db():
    print("▶ Création des tables (si nécessaire)...")
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        # Initialisation basique des assets si vide
        if db.query(Asset).count() == 0:
            print("▶ Insertion d'assets de base...")
            assets = [
                Asset(ticker="SPY", name="S&P 500 ETF", asset_class="equity"),
                Asset(ticker="AGG", name="US Aggregate Bond", asset_class="bond"),
                Asset(ticker="EFA", name="MSCI EAFE ETF", asset_class="equity"),
                Asset(ticker="GLD", name="Gold ETF", asset_class="commodity"),
                Asset(ticker="VNQ", name="US REIT ETF", asset_class="real_estate"),
            ]
            db.add_all(assets)
            db.commit()
        else:
            print("▶ Assets déjà présents, pas de réinsertion.")

    finally:
        db.close()
    print("✅ init_db terminé.")


if __name__ == "__main__":
    init_db()
