FROM python:3.13-slim

# Définit le dossier de travail
WORKDIR /app

# Copie le script dans le conteneur
COPY main.py .

# Désactive le buffering de Python pour voir les "print" en temps réel dans Docker
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]