#!/bin/sh

# Этот скрипт является точкой входа для Docker-контейнера.

# Выход из скрипта при любой ошибке
set -e

echo "Waiting for postgres..."

# Проверяем доступность хоста и порта базы данных.
# netcat (nc) будет пытаться подключиться, пока не получится.
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    sleep 0.1
done

echo "PostgreSQL started"

echo "Running tests..."
# Устанавливаем переменную окружения, чтобы Django знал, что мы запускаем тесты
RUNNING_TESTS=1 python manage.py test

echo "Tests passed. Starting server..."
exec "$@"
