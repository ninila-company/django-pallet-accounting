#!/bin/bash

echo "Starting development environment..."

# Остановим production контейнеры если они запущены
docker compose down

# Запустим базу данных
echo "Starting database..."
docker compose up -d db

# Запустим Django в режиме разработки
echo "Starting Django development server..."
docker compose -f docker-compose.dev.yml up web
