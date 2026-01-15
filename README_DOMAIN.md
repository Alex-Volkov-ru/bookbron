# Настройка домена bookreg.ru с SSL

## Шаг 1: Настройка DNS записей

В панели ADMINVPS для домена `bookreg.ru` добавьте следующие DNS записи:

### A записи:
- `bookreg.ru` → `5.35.125.194`
- `www.bookreg.ru` → `5.35.125.194`

### Или используйте CNAME для www:
- `www.bookreg.ru` → `bookreg.ru` (CNAME)

**Важно:** Дождитесь распространения DNS (обычно 5-30 минут). Проверьте:
```bash
nslookup bookreg.ru
nslookup www.bookreg.ru
```

## Шаг 2: Варианты настройки

### Вариант A: Использовать существующий bigs-nginx как reverse proxy (РЕКОМЕНДУЕТСЯ)

Если `bigs-nginx` уже работает на портах 80/443, добавьте в его конфигурацию:

```nginx
# /etc/nginx/sites-available/bookreg.ru (или в основной конфиг)
server {
    listen 80;
    server_name bookreg.ru www.bookreg.ru;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name bookreg.ru www.bookreg.ru;
    
    ssl_certificate /etc/letsencrypt/live/bookreg.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bookreg.ru/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Затем получите SSL сертификат:
```bash
certbot certonly --nginx -d bookreg.ru -d www.bookreg.ru
```

### Вариант B: Использовать frontend контейнер на портах 80/443

**ВНИМАНИЕ:** Это потребует остановки или перенастройки `bigs-nginx`!

1. Остановите `bigs-nginx` или перенастройте его на другие порты
2. Обновите `docker-compose.production.yml` (уже обновлен)
3. Получите SSL сертификат:

```bash
cd /opt/booking
chmod +x scripts/init_ssl.sh
./scripts/init_ssl.sh
```

Или вручную:
```bash
docker compose -f docker-compose.production.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@bookreg.ru \
    --agree-tos \
    --no-eff-email \
    -d bookreg.ru \
    -d www.bookreg.ru
```

4. Перезапустите frontend:
```bash
docker compose -f docker-compose.production.yml restart frontend
```

## Шаг 3: Проверка

После настройки проверьте:

```bash
# Проверьте доступность
curl -I https://bookreg.ru
curl -I https://www.bookreg.ru

# Проверьте SSL сертификат
openssl s_client -connect bookreg.ru:443 -servername bookreg.ru
```

## Автоматическое обновление сертификатов

Certbot контейнер автоматически обновляет сертификаты каждые 12 часов.

## Важные замечания

1. **Конфликт портов:** Если `bigs-nginx` использует порты 80/443, выберите Вариант A
2. **DNS:** Убедитесь, что DNS записи правильно настроены перед получением SSL
3. **Firewall:** Убедитесь, что порты 80 и 443 открыты в firewall

