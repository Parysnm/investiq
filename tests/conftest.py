"""
Configuration globale pour pytest – version 100% compatible FastAPI + SQLite.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------
# 1) Forcer SQLite pour les tests AVANT d'importer app.main
# ---------------------------------------------------------
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Ajouter le dossier racine dans le PYTHONPATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Maintenant on peut importer app
from app.main import app
import app.db.database as database
from app.db.database import Base, get_db


# ---------------------------------------------------------
# 2) Création moteur SQLite isolé pour les tests
# ---------------------------------------------------------
test_engine = create_engine(
    "sqlite:///./test.db",
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)

# Override global du moteur SQLAlchemy
database.engine = test_engine
database.SessionLocal = TestingSessionLocal


# ---------------------------------------------------------
# 3) Session DB isolée par test
# ---------------------------------------------------------
@pytest.fixture(scope="function")
def test_db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


# ---------------------------------------------------------
# 4) Override de la dépendance get_db
# ---------------------------------------------------------
@pytest.fixture(scope="function", autouse=True)
def override_get_db(test_db_session):

    def _override():
        yield test_db_session

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()


# ---------------------------------------------------------
# 5) Client API
# ---------------------------------------------------------
@pytest.fixture(scope="function")
def client():
    return TestClient(app)
