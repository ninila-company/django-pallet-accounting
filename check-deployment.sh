#!/bin/bash

# Скрипт для проверки статуса развертывания на Synology
# Использование: ./check-deployment.sh

set -e

echo "🔍 Проверяем статус развертывания на Synology..."

# Проверяем наличие переменных окружения
if [ -z "$SYNOLOGY_HOST" ] || [ -z "$SYNOLOGY_USERNAME" ] || [ -z "$SYNOLOGY_PASSWORD" ]; then
    echo "❌ Ошибка: Не установлены переменные окружения для подключения к Synology"
    echo "Установите: SYNOLOGY_HOST, SYNOLOGY_USERNAME, SYNOLOGY_PASSWORD"
    exit 1
fi

# Проверяем подключение к Synology
echo "🔗 Проверяем подключение к Synology..."
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $SYNOLOGY_USERNAME@$SYNOLOGY_HOST "echo '✅ Подключение успешно'" || {
    echo "❌ Не удалось подключиться к Synology"
    exit 1
}

# Проверяем статус контейнеров
echo "📊 Проверяем статус контейнеров..."
ssh $SYNOLOGY_USERNAME@$SYNOLOGY_HOST << 'EOF'
    cd /volume1/docker/django-pallet-accounting
    
    echo "🐳 Статус Docker контейнеров:"
    docker compose ps
    
    echo ""
    echo "📈 Использование ресурсов:"
    docker stats --no-stream
    
    echo ""
    echo "📝 Последние логи web контейнера:"
    docker compose logs --tail=20 web
    
    echo ""
    echo "🌐 Проверка доступности приложения:"
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:80 | grep -q "200\|302"; then
        echo "✅ Приложение доступно на порту 80"
    else
        echo "❌ Приложение недоступно на порту 80"
    fi
EOF

echo "✅ Проверка завершена!" 