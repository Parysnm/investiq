# app/core/config.py
"""
Configuration centralisée de l’application.

Les valeurs proviennent des variables d’environnement,
avec des valeurs par défaut pour faciliter le développement local.
"""

import os
from pydantic import BaseModel


class Settings(BaseModel):
    """
    Réunit toutes les constantes de configuration
    utilisées dans l’application (base de données, JWT, etc.).
    """
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://app:app@localhost:5432/investiq"
    )

    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me")
    JWT_ALG: str = os.getenv("JWT_ALG", "HS256")

    # Durée de validité d’un token JWT : 24h par défaut
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24


# Instance unique disponible partout dans l’application
settings = Settings()
