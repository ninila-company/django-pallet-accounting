# Развертывание на Synology NAS

## Обзор

Этот документ описывает процесс настройки CI/CD для автоматического развертывания Django приложения на Synology NAS.

## Предварительные требования

### 1. На Synology NAS:
- Установлен Docker
- Установлен Docker Compose
- SSH доступ включен
- Создана папка для проекта: `/volume1/docker/django-pallet-accounting`

### 2. На GitHub:
- Репозиторий с кодом
- Docker Hub аккаунт
- GitHub Actions включены

## Настройка GitHub Secrets

В настройках репозитория GitHub (`Settings` → `Secrets and variables` → `Actions`) добавьте следующие секреты:

### Docker Hub
- `DOCKERHUB_USERNAME` - ваше имя пользователя Docker Hub
- `DOCKERHUB_TOKEN` - токен доступа Docker Hub (не пароль!)

### Synology NAS
- `SYNOLOGY_HOST` - IP адрес вашего Synology NAS
- `SYNOLOGY_USERNAME` - имя пользователя для SSH
- `SYNOLOGY_PASSWORD` - пароль пользователя
- `SYNOLOGY_PORT` - порт SSH (обычно 22)

## Настройка Docker Hub

1. Создайте аккаунт на [Docker Hub](https://hub.docker.com)
2. Создайте Access Token:
   - Перейдите в `Account Settings` → `Security`
   - Нажмите `New Access Token`
   - Дайте токену имя (например, "GitHub Actions")
   - Скопируйте токен и сохраните его в GitHub Secrets

## Настройка Synology NAS

### 1. Установка Docker

1. Откройте Package Center на Synology
2. Найдите и установите "Docker"
3. Запустите Docker

### 2. Настройка SSH

1. Перейдите в `Control Panel` → `Terminal & SNMP`
2. Включите SSH
3. Установите порт (по умолчанию 22)

### 3. Создание структуры папок

```bash
# Подключитесь к Synology по SSH
ssh admin@your-synology-ip

# Создайте папку для проекта
mkdir -p /volume1/docker/django-pallet-accounting
cd /volume1/docker/django-pallet-accounting
```

### 4. Создание .env.prod файла

Создайте файл `.env.prod` на Synology:

```bash
# Django settings
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-synology-ip,your-domain.com,localhost,127.0.0.1

# Database settings
POSTGRES_DB=pallet_accounting_prod
POSTGRES_USER=pallet_user
POSTGRES_PASSWORD=your-very-secure-database-password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Docker Hub
DOCKERHUB_USERNAME=your-dockerhub-username
```

### 5. Копирование файлов

Скопируйте следующие файлы на Synology:
- `docker-compose.prod.yml` → `docker-compose.yml`
- `nginx/nginx.conf` → `nginx/nginx.conf`

## Настройка Nginx

Убедитесь, что файл `nginx/nginx.conf` настроен правильно:

```nginx
server {
    listen 80;
    server_name your-synology-ip;

    location /static/ {
        alias /app/staticfiles/;
    }

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Первый запуск

### 1. На Synology:

```bash
cd /volume1/docker/django-pallet-accounting

# Создайте и запустите контейнеры
docker compose up -d

# Проверьте статус
docker compose ps

# Посмотрите логи
docker compose logs -f
```

### 2. Выполните миграции:

```bash
# Войдите в контейнер web
docker compose exec web python manage.py migrate

# Создайте суперпользователя (опционально)
docker compose exec web python manage.py createsuperuser
```

## Автоматическое развертывание

После настройки всех секретов в GitHub, каждый push в ветку `main` будет автоматически:

1. Собирать Docker образы
2. Пушить их в Docker Hub
3. Подключаться к Synology по SSH
4. Останавливать старые контейнеры
5. Запускать новые контейнеры

## Мониторинг

### Проверка статуса развертывания:
1. Перейдите в GitHub → Actions
2. Найдите workflow "Deploy to Synology"
3. Проверьте логи выполнения

### Проверка работы приложения:
```bash
# На Synology
docker compose ps
docker compose logs -f web
docker compose logs -f nginx
```

## Устранение неполадок

### Проблемы с подключением к Synology:
- Проверьте SSH доступ
- Убедитесь, что порт 22 открыт
- Проверьте правильность учетных данных

### Проблемы с Docker Hub:
- Проверьте правильность токена
- Убедитесь, что образы публичные или у вас есть права доступа

### Проблемы с приложением:
- Проверьте логи: `docker compose logs -f`
- Убедитесь, что .env.prod настроен правильно
- Проверьте, что база данных запущена

## Безопасность

1. Используйте сильные пароли
2. Ограничьте доступ к SSH только необходимыми IP
3. Регулярно обновляйте Docker образы
4. Используйте HTTPS в production
5. Настройте firewall на Synology

## Обновление приложения

Для обновления приложения просто сделайте push в ветку `main`:

```bash
git add .
git commit -m "Update application"
git push origin main
```

GitHub Actions автоматически развернет обновления на Synology. 