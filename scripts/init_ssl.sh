#!/bin/bash
# Скрипт для получения SSL сертификата для bookreg.ru

set -e

DOMAIN="bookreg.ru"
EMAIL="admin@bookreg.ru"  # Замените на ваш email

echo "🔐 Получение SSL сертификата для $DOMAIN..."

# Проверяем, что frontend контейнер запущен
if ! docker compose -f docker-compose.production.yml ps frontend | grep -q "Up"; then
    echo "❌ Frontend контейнер не запущен. Запустите сначала: docker compose -f docker-compose.production.yml up -d frontend"
    exit 1
fi

# Получаем сертификат
docker compose -f docker-compose.production.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

echo "✅ SSL сертификат получен!"
echo "🔄 Перезапускаем frontend для применения сертификата..."
docker compose -f docker-compose.production.yml restart frontend

echo "✅ Готово! Проверьте https://$DOMAIN"

