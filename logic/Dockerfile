FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir influxdb-client RPi.GPIO

COPY *.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]