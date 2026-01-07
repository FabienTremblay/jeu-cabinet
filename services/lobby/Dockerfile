# services/lobby/Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances
COPY services/lobby/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code de l'application dans le package "lobby"
COPY services/lobby /app/lobby

EXPOSE 8080

# On démarre uvicorn sur le module lobby.app
CMD ["uvicorn", "lobby.app:app", "--host", "0.0.0.0", "--port", "8080"]
