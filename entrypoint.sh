#!/bin/sh

# Выход из скрипта при любой ошибке
set -e

# Ожидаем готовности базы данных
echo "Waiting for postgres..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    sleep 0.1
done
echo "PostgreSQL started"

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn server..."
export PYTHONPATH=/app
exec gunicorn --chdir /app pallet_accounting.wsgi:application --bind 0.0.0.0:8000
