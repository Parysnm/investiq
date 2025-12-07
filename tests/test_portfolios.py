"""
Tests pour le router /portfolios – création, liste et suppression
"""
from fastapi.testclient import TestClient


def _token(client):
    """Retourne un token JWT valide."""
    r = client.post("/auth/register", json={"email": "me@you.com", "password": "pass"})
    return r.json()["access_token"]


def test_create_portfolio_success(client):
    """
    Test de création d'un portefeuille avec succès.

    Scénario : utilisateur authentifié envoie un portefeuille avec tickers/poids valides.
    Résultat attendu : portefeuille créé (status 201).
    """

    # Arrange
    token = _token(client)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "name": "Portefeuille Test",
        "tickers": ["SPY", "AGG", "GLD"],
        "weights": [0.4, 0.4, 0.2],
        "metrics": {"mu_ann": 0.07, "vol_ann": 0.12, "sharpe": 0.6},
    }

    # Act
    response = client.post("/portfolios/", json=payload, headers=headers)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Portefeuille Test"
    assert data["tickers"] == payload["tickers"]


def test_list_portfolios(client):
    """
    Test de listing des portefeuilles.

    Scénario : utilisateur authentifié possédant au moins un portefeuille.
    Résultat attendu : liste non vide.
    """

    # Arrange
    token = _token(client)
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/portfolios/", json={
        "name": "Test1",
        "tickers": ["SPY", "AGG"],
        "weights": [0.5, 0.5]
    }, headers=headers)

    # Act
    response = client.get("/portfolios/", headers=headers)

    # Assert
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_delete_portfolio_success(client):
    """
    Test de suppression d'un portefeuille par son propriétaire.

    Scénario : utilisateur authentifié supprime un portefeuille existant.
    Résultat attendu : suppression réussie (deleted=True).
    """

    # Arrange
    token = _token(client)
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post("/portfolios/", json={
        "name": "A supprimer",
        "tickers": ["SPY", "AGG"],
        "weights": [0.5, 0.5]
    }, headers=headers)
    portfolio_id = r.json()["id"]

    # Act
    response = client.delete(f"/portfolios/{portfolio_id}", headers=headers)

    # Assert
    assert response.status_code == 200
    assert response.json()["deleted"] is True
