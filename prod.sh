#!/bin/bash

echo "Starting production environment..."

# Остановим development контейнеры если они запущены
docker compose -f docker-compose.dev.yml down

# Запустим production окружение
docker compose up -d 