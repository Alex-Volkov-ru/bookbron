#!/bin/bash

# Скрипт инициализации проекта
# Запускает миграции и создает администратора

set -e

echo "=========================================="
echo "Инициализация системы бронирования"
echo "=========================================="

# Проверка что контейнеры запущены
if ! docker-compose ps | grep -q "backend.*Up"; then
    echo "Ошибка: контейнер backend не запущен!"
    echo "Сначала выполните: docker-compose up -d --build"
    exit 1
fi

echo ""
echo "1. Запуск миграций базы данных..."
docker-compose exec -T backend alembic upgrade head

echo ""
echo "2. Создание пользователей (админ, менеджер, пользователь)..."
docker-compose exec -T backend python scripts/init_db.py

echo ""
echo "=========================================="
echo "Инициализация завершена!"
echo "=========================================="
echo ""
echo "Доступ к сервисам:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "Тестовые аккаунты:"
echo "  Админ:"
echo "    Email: admin@example.com"
echo "    Password: admin"
echo "  Менеджер:"
echo "    Email: manager@example.com"
echo "    Password: manager"
echo "  Пользователь:"
echo "    Email: user@example.com"
echo "    Password: user"
echo ""

