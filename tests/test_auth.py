"""
Tests pour le router d'authentification /auth
"""
from fastapi.testclient import TestClient


def test_register_success(client):
    """
    Test d'inscription avec succès.

    Scénario : un utilisateur envoie un email et un mot de passe valides.
    Résultat attendu : un token JWT est retourné (status 200).
    """

    # Arrange
    payload = {"email": "test@example.com", "password": "secret123"}

    # Act
    response = client.post("/auth/register", json=payload)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_success(client):
    """
    Test de connexion avec succès.

    Scénario : l'utilisateur existe et fournit le bon mot de passe.
    Résultat attendu : un token JWT valide (status 200).
    """

    # Arrange
    client.post("/auth/register", json={"email": "aa@bb.com", "password": "pass"})

    # Act
    response = client.post("/auth/login", json={"email": "aa@bb.com", "password": "pass"})

    # Assert
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(client):
    """
    Test d'échec de connexion avec mauvais mot de passe.

    Scénario : l’utilisateur existe mais le mot de passe fourni est incorrect.
    Résultat attendu : erreur 401 (Invalid credentials).
    """

    # Arrange
    client.post("/auth/register", json={"email": "toto@ex.com", "password": "correct"})

    # Act
    response = client.post("/auth/login", json={"email": "toto@ex.com", "password": "wrong"})

    # Assert
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
