#!/bin/bash

# Логирование всего вывода в файл
LOGFILE="/var/log/deploy.log"
exec > >(tee -a "$LOGFILE") 2>&1

echo "=============================="
echo "$(date): Начало деплоя"

set -e  # Остановить скрипт при ошибке

# Переходим в директорию проекта (если нужно)
# cd /volume1/docker/django-pallet-accounting

# Проверяем наличие изменений в удалённом репозитории
git fetch
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "Нет новых изменений. Деплой не требуется."
    exit 0
fi

echo "Обнаружены новые изменения. Обновляем код..."
git pull

echo "Останавливаем dev-контейнеры (если запущены)..."
docker compose -f docker-compose.dev.yml down || true

echo "Перезапускаем production окружение..."
docker compose up -d --build

echo "$(date): Деплой завершён успешно!"
echo "=============================="
