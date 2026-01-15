#!/bin/bash
# Полная настройка сервера для booking системы

set -e

PROJECT_DIR="/opt/booking"
DOMAIN="bookreg.ru"

echo "🚀 Настройка сервера для booking системы..."
echo ""

# 1. Создаем необходимые директории
echo "📁 Создание директорий..."
mkdir -p "$PROJECT_DIR/env/frontend"
mkdir -p "$PROJECT_DIR/env/nginx"
mkdir -p "$PROJECT_DIR/scripts"

# 2. Проверяем наличие .env
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "⚠️  Файл .env не найден. Создаю базовый .env..."
    cat > "$PROJECT_DIR/.env" << 'ENVEOF'
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=booking_db
SECRET_KEY=change-this-secret-key-in-production
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
DOCKER_USERNAME=ximikat01
ENVEOF
    echo "✅ Создан .env файл. ОБЯЗАТЕЛЬНО измените SECRET_KEY!"
fi

# 3. Проверяем docker-compose.production.yml
if [ ! -f "$PROJECT_DIR/docker-compose.production.yml" ]; then
    echo "❌ docker-compose.production.yml не найден!"
    echo "   Скопируйте его вручную или через GitHub Actions"
    exit 1
fi

# 4. Проверяем nginx конфиги
if [ ! -f "$PROJECT_DIR/env/frontend/nginx.conf" ]; then
    echo "❌ env/frontend/nginx.conf не найден!"
    echo "   Скопируйте его вручную или через GitHub Actions"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/env/frontend/local.conf" ]; then
    echo "⚠️  env/frontend/local.conf не найден. Создаю базовый..."
    mkdir -p "$PROJECT_DIR/env/frontend"
    # Базовый local.conf будет создан через GitHub Actions
fi

# 5. Останавливаем старые контейнеры
echo "🛑 Остановка старых контейнеров..."
cd "$PROJECT_DIR"
docker compose -f docker-compose.production.yml down 2>/dev/null || true

# 6. Запускаем контейнеры
echo "🚀 Запуск контейнеров..."
export DOCKER_USERNAME=${DOCKER_USERNAME:-ximikat01}
docker compose -f docker-compose.production.yml pull
docker compose -f docker-compose.production.yml up -d

# 7. Ждем запуска
echo "⏳ Ожидание запуска сервисов (10 секунд)..."
sleep 10

# 8. Проверяем статус
echo ""
echo "📊 Статус контейнеров:"
docker compose -f docker-compose.production.yml ps

# 9. Проверяем логи
echo ""
echo "📋 Последние логи frontend:"
docker logs --tail 10 booking_system-frontend-1 2>&1 || echo "Контейнер не запущен"

echo ""
echo "📋 Последние логи backend:"
docker logs --tail 10 booking_system-backend-1 2>&1 || echo "Контейнер не запущен"

# 10. Проверяем доступность
echo ""
echo "🌐 Проверка доступности:"
curl -I http://localhost:8080 2>/dev/null | head -1 || echo "❌ Frontend недоступен на порту 8080"

echo ""
echo "✅ Настройка завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "   1. Проверьте DNS записи для $DOMAIN"
echo "   2. Настройте bigs-nginx как reverse proxy (если нужно)"
echo "   3. Получите SSL сертификат: certbot certonly --nginx -d $DOMAIN -d www.$DOMAIN"
echo ""
echo "🌐 Доступ к проекту:"
echo "   - По IP: http://5.35.125.194:8080"
echo "   - По домену: https://$DOMAIN (после настройки DNS и SSL)"

