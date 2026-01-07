FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# on copie le package Python dans l'image
COPY adapter_evenements ./adapter_evenements

CMD ["python", "-m", "adapter_evenements.worker_adapter"]

