FROM python:3.11-slim

# Définir l’emplacement de travail
WORKDIR /app

# Empêcher Python de créer des fichiers .pyc et activer le flush stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --- Install dependencies nécessaires pour le wait-for-db (netcat) ---
RUN apt-get update && apt-get install -y netcat-openbsd

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY app ./app
COPY data ./data
COPY scripts ./scripts

# Exposer le port API
EXPOSE 8000

# Commande par défaut quand on lance le conteneur 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
