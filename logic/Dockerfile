FROM python:3.13-slim

# On installe gcc (nécessaire pour compiler influxdb sur ARM/v7)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installation de la dépendance
RUN pip install --no-cache-dir influxdb RPi.GPIO

# Copie le script dans le conteneur
COPY main.py .

# Désactive le buffering pour voir les logs
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]