FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y netcat-openbsd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

COPY . .


# Comando padrão removido porque será sobrescrito no docker-compose
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
