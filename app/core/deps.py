# app/core/deps.py
"""
Dépendances réutilisables dans l’application.

Ici : récupération du user courant via JWT.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from .config import settings
from ..db.database import get_db
from ..models.user import User


# Dépendance HTTPBearer standard pour récupérer le header Authorization
security = HTTPBearer()


def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dépendance utilisée dans toutes les routes protégées.

    - Vérifie la validité du token JWT
    - Extrait le champ 'sub' (email)
    - Récupère l'utilisateur associé en base
    """

    try:
        payload = jwt.decode(
            token.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG]
        )
        email: str = payload.get("sub")

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide."
        )

    # Vérification en base
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé."
        )

    return user
