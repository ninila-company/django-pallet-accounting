# Настройка Self-hosted Runner на Synology

## Обзор

Self-hosted runner позволяет запускать GitHub Actions прямо на вашем Synology NAS, что решает проблему доступа к локальной сети.

## Преимущества

✅ **Безопасность** - не нужно открывать порты наружу  
✅ **Скорость** - быстрая сборка и развертывание  
✅ **Контроль** - полный контроль над окружением  
✅ **Стоимость** - бесплатно (GitHub Actions минуты не тратятся)  

## Настройка Self-hosted Runner

### Шаг 1: Создание Runner в GitHub

1. Перейдите в ваш репозиторий → **Settings** → **Actions** → **Runners**
2. Нажмите **"New self-hosted runner"**
3. Выберите **Linux** (x64)
4. Скопируйте команды настройки

### Шаг 2: Установка на Synology

#### Вариант A: Через SSH (рекомендуется)

```bash
# Подключитесь к Synology по SSH
ssh admin@your-synology-ip

# Создайте папку для runner
mkdir -p /volume1/github-runner
cd /volume1/github-runner

# Скачайте runner (замените URL на ваш)
wget https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz

# Распакуйте
tar xzf actions-runner-linux-x64-2.311.0.tar.gz

# Настройте runner (используйте команды из GitHub)
./config.sh --url https://github.com/your-username/django-pallet-accounting --token YOUR_TOKEN

# Запустите runner
./run.sh
```

#### Вариант B: Через Docker

```bash
# Создайте docker-compose.yml для runner
cat > /volume1/docker/github-runner/docker-compose.yml << 'EOF'
version: '3.8'
services:
  github-runner:
    image: myoung34/github-runner:latest
    container_name: github-runner
    restart: unless-stopped
    environment:
      - REPO_URL=https://github.com/your-username/django-pallet-accounting
      - RUNNER_TOKEN=YOUR_TOKEN
      - RUNNER_NAME=synology-runner
      - RUNNER_WORKDIR=/tmp/_work
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /volume1/docker:/volume1/docker
EOF

# Запустите
cd /volume1/docker/github-runner
docker compose up -d
```

### Шаг 3: Автозапуск Runner

Создайте systemd сервис для автозапуска:

```bash
# Создайте файл сервиса
sudo nano /etc/systemd/system/github-runner.service
```

```ini
[Unit]
Description=GitHub Actions Runner
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/volume1/github-runner
ExecStart=/volume1/github-runner/run.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Включите автозапуск
sudo systemctl enable github-runner
sudo systemctl start github-runner
```

## Альтернативные решения

### Решение 1: VPN (если нужен доступ извне)

```bash
# На Synology установите VPN Server
# Package Center → VPN Server → Install

# Настройте OpenVPN или L2TP
# GitHub Actions будет подключаться через VPN
```

### Решение 2: Reverse SSH Tunnel

```bash
# На Synology создайте постоянное соединение
ssh -R 2222:localhost:22 user@external-server.com -N

# GitHub Actions подключается к external-server.com:2222
```

### Решение 3: Webhook + локальный скрипт

```bash
# GitHub отправляет webhook на внешний сервер
# Внешний сервер пересылает команду в локальную сеть
```

## Рекомендуемая архитектура

```
GitHub Repository
    ↓ (webhook)
Self-hosted Runner (на Synology)
    ↓
Docker Compose
    ↓
Django Application
```

## Безопасность

1. **Ограничьте доступ** к runner только вашему репозиторию
2. **Используйте токены** с минимальными правами
3. **Регулярно обновляйте** runner
4. **Мониторьте логи** на предмет подозрительной активности

## Мониторинг

```bash
# Проверка статуса runner
sudo systemctl status github-runner

# Просмотр логов
sudo journalctl -u github-runner -f

# Проверка в GitHub
# Settings → Actions → Runners
```

## Устранение неполадок

### Runner не запускается:
```bash
# Проверьте права доступа
chmod +x /volume1/github-runner/*.sh

# Проверьте токен
./config.sh --url https://github.com/your-username/django-pallet-accounting --token YOUR_TOKEN
```

### Docker недоступен:
```bash
# Добавьте пользователя в группу docker
usermod -aG docker $USER

# Перезапустите Docker
sudo systemctl restart docker
```

## Заключение

Self-hosted runner - это лучшее решение для развертывания на устройствах в локальной сети. Он обеспечивает безопасность, скорость и контроль над процессом развертывания. 