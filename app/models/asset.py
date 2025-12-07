# app/models/asset.py
from sqlalchemy import Column, Integer, String
from ..db.database import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    asset_class = Column(String, nullable=False)
