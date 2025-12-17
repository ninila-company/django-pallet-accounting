# 1. Использование официального образа Python
FROM python:3.12-slim

# 2. Установка переменных окружения для Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Установка системных зависимостей, которые могут понадобиться для psycopg2
# и WeasyPrint (для генерации PDF)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev netcat-openbsd \
    libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 4. Установка рабочей директории
WORKDIR /app

# Добавляем /app в PYTHONPATH, чтобы Gunicorn мог найти модуль проекта
ENV PYTHONPATH /app

# 5. Установка зависимостей Python
# Сначала копируем только файл с зависимостями, чтобы использовать кэш Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Копирование кода проекта и скриптов запуска
COPY . /app
COPY entrypoint.sh /entrypoint.sh
COPY entrypoint-dev.sh /entrypoint-dev.sh
RUN chmod +x /entrypoint.sh /entrypoint-dev.sh

# 7. Сбор статических файлов
# Django требует SECRET_KEY для запуска любой manage.py команды.
# Мы устанавливаем временные значения только на время сборки, чтобы команда могла выполниться.
# Django также требует настройки базы данных, даже если команда ее не использует.
# Настоящие значения будут взяты из .env при запуске контейнера.
RUN SECRET_KEY="dummy-key-for-build" \
    DEBUG=0 \
    ALLOWED_HOSTS="*" \
    POSTGRES_DB="build_db" POSTGRES_USER="build_user" POSTGRES_PASSWORD="build_password" POSTGRES_HOST="localhost" \
    python manage.py collectstatic --noinput

# 8. Запуск приложения через entrypoint скрипт
ENTRYPOINT ["/entrypoint.sh"]

# Команда, которая будет выполнена, если entrypoint завершится успешно
CMD ["gunicorn", "pallet_accounting.wsgi:application", "--bind", "0.0.0.0:8000"]
