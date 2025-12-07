# ----------------------------------------
# Makefile – Commandes utiles du projet
# ----------------------------------------

# Lance l'application en Docker (API + DB)
up:
	 docker compose up --build

# Arrête les conteneurs
down:
	 docker compose down

# Reconstruit toute l'application de zéro
rebuild:
	 docker compose down
	 docker compose build --no-cache
	 docker compose up --build

# Lance les tests unitaires
test:
	 pytest -q

# Nettoie la base de test et le cache pytest
clean:
	 rm -f test.db
	 rm -rf __pycache__
	 rm -rf */__pycache__
	 rm -rf .pytest_cache

# Exécute les tests + relance l'app
fresh:
	 make clean
	 make test
	 make up
