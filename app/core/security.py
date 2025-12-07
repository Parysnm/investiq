# app/core/security.py
"""
Fonctions liées à la sécurité :
- Hashing des mots de passe
- Vérification des mots de passe
- Création de tokens JWT

"""

from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from .config import settings


# Contexte de hashing conforme aux bonnes pratiques
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# -------------------------
#     Password hashing
# -------------------------

def hash_password(password: str) -> str:
    """
    Hash un mot de passe en utilisant bcrypt.

    Retourne une chaîne sécurisée qui sera stockée en base.
    """
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Compare un mot de passe brut avec son hash.

    Retourne True si le mot de passe est correct.
    """
    return pwd_context.verify(password, password_hash)


# -------------------------
#       JWT Token
# -------------------------

def create_access_token(
    sub: str,
    expires_minutes: Optional[int] = None
) -> str:
    """
    Génère un token JWT signé contenant :
    - sub : l'identifiant utilisateur (email ici)
    - exp : date d’expiration

    Le token est signé avec SECRET + ALG définis dans settings.
    """
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": sub,
        "exp": expire
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALG
    )
