#!/bin/sh

echo "⏳ Aguardando PostgreSQL iniciar em $DB_HOST..."

while ! nc -z $DB_HOST 5432; do
  sleep 1
done

echo "✅ PostgreSQL está pronto, iniciando o Django..."

exec "$@"
