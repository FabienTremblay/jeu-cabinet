# services/api_moteur/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# On copie toute la hiérarchie "services" telle quelle
COPY services /app/services

RUN pip install --no-cache-dir \
      fastapi uvicorn[standard] httpx kafka-python pydantic pydantic-settings

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

# On lance l'app via le package complet
CMD ["uvicorn", "services.api_moteur.app:app", "--host", "0.0.0.0", "--port", "8080"]

