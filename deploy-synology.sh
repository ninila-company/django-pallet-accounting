#!/bin/bash

# Скрипт для развертывания Django приложения на Synology NAS
# Использование: ./deploy-synology.sh

set -e

echo "🚀 Начинаем развертывание на Synology..."

# Проверяем наличие переменных окружения
if [ -z "$DOCKERHUB_USERNAME" ]; then
    echo "❌ Ошибка: DOCKERHUB_USERNAME не установлен"
    exit 1
fi

# Создаем .env.prod файл для production
if [ ! -f .env.prod ]; then
    echo "📝 Создаем .env.prod файл..."
    cat > .env.prod << EOF
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-synology-ip,localhost,127.0.0.1

# Database settings
POSTGRES_DB=pallet_accounting_prod
POSTGRES_USER=pallet_user
POSTGRES_PASSWORD=your-secure-password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Docker Hub
DOCKERHUB_USERNAME=$DOCKERHUB_USERNAME
EOF
    echo "⚠️  Не забудьте изменить значения в .env.prod файле!"
fi

# Собираем и пушим Docker образы
echo "🔨 Собираем Docker образы..."
docker compose build

echo "🏷️  Тегируем образы..."
docker tag django-pallet-accounting_web $DOCKERHUB_USERNAME/django-pallet-accounting_web:latest
docker tag django-pallet-accounting_nginx $DOCKERHUB_USERNAME/django-pallet-accounting_nginx:latest

echo "📤 Пушим образы в Docker Hub..."
docker push $DOCKERHUB_USERNAME/django-pallet-accounting_web:latest
docker push $DOCKERHUB_USERNAME/django-pallet-accounting_nginx:latest

echo "✅ Развертывание завершено!"
echo "📋 Следующие шаги:"
echo "1. Скопируйте .env.prod файл на ваш Synology NAS"
echo "2. Скопируйте docker-compose.prod.yml на Synology"
echo "3. Запустите на Synology: docker compose -f docker-compose.prod.yml up -d" 