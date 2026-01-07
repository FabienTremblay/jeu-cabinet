FROM python:3.12-slim

WORKDIR /app

# dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
 && rm -rf /var/lib/apt/lists/*

# requirements
COPY services/ui_etat_joueur/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# code applicatif
COPY services/ui_etat_joueur /app/services/ui_etat_joueur

ENV PYTHONPATH=/app
ENV UI_ETAT_HTTP_PORT=8080

CMD ["uvicorn", "services.ui_etat_joueur.app:app", "--host", "0.0.0.0", "--port", "8080"]
