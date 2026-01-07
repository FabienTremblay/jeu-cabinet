# services/commande_moteur/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# dépendances partagées du projet
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# code du worker
COPY services/commande_moteur ./commande_moteur

CMD ["python", "-m", "commande_moteur.worker_moteur"]
