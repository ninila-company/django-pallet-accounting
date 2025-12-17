#!/bin/sh

# Этот скрипт является точкой входа для Docker-контейнера в режиме разработки.

# Выход из скрипта при любой ошибке
set -e

echo "DEV: Waiting for postgres..."

# Проверяем доступность хоста и порта базы данных.
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    sleep 0.1
done

echo "DEV: PostgreSQL started"

echo "DEV: Running tests..."
# Устанавливаем переменную окружения, чтобы Django знал, что мы запускаем тесты
RUNNING_TESTS=1 python manage.py test

echo "DEV: Tests passed. Starting development server..."
# Запускаем сервер разработки Django
python manage.py runserver 0.0.0.0:8000
