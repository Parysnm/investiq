"""
Tests pour le router d'optimisation /optimize
"""
from fastapi.testclient import TestClient


def _get_token(client):
    """Inscription + récupération d'un token JWT valide."""
    payload = {"email": "user@test.com", "password": "pass123"}
    r = client.post("/auth/register", json=payload)
    return r.json()["access_token"]


def test_min_variance_success(client):
    """
    Test de l'optimisation min-variance avec succès.

    Scénario : utilisateur authentifié, tickers valides présents dans prices.csv.
    Résultat attendu : un JSON contenant allocations + métriques.
    """

    # Arrange
    token = _get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"tickers": ["SPY", "AGG"], "max_weight": 0.7}

    # Act
    response = client.post("/optimize/min-variance", json=payload, headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert "allocations" in data
    assert "metrics" in data
    assert len(data["allocations"]) == 2

    weights = [a["weight"] for a in data["allocations"]]
    assert 0.99 <= sum(weights) <= 1.01


def test_min_variance_unauthorized(client):
    """
    Test d'appel non authentifié à /optimize/min-variance.

    Scénario : aucun token envoyé.
    Résultat attendu : erreur 403 ou 422 selon FastAPI.
    """

    # Arrange
    payload = {"tickers": ["SPY", "AGG"], "max_weight": 0.6}

    # Act
    response = client.post("/optimize/min-variance", json=payload)

    # Assert
    assert response.status_code in (401, 403, 422)
