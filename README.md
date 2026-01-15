# Система бронирования мест в кафе

Веб-приложение для управления бронированием столов в кафе. Состоит из FastAPI backend и React frontend.

## Технологический стек

- **Backend**: Python 3.11, FastAPI, PostgreSQL, SQLAlchemy 2.0
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Очереди**: Celery + RabbitMQ
- **Кэш**: Redis
- **Развертывание**: Docker Compose

## Быстрый старт

### 1. Запуск всех сервисов

```bash
docker-compose up -d --build
```

### 2. Инициализация базы данных

После запуска контейнеров выполните скрипт инициализации:

```bash
chmod +x init.sh
./init.sh
```

Скрипт выполнит:
- Применение миграций базы данных
- Создание администратора (если его нет)

### 3. Доступ к приложению

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Документация (Swagger)**: http://localhost:8000/docs
- **Flower (Celery мониторинг)**: http://localhost:5555
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

## Тестовые аккаунты

После инициализации создаются следующие пользователи:

### Администратор
- **Email**: `admin@example.com`
- **Password**: `admin`
- **Права**: Полный доступ (создание кафе, управление пользователями и т.д.)

### Менеджер
- **Email**: `manager@example.com`
- **Password**: `manager`
- **Права**: Управление своими кафе (не может создавать/удалять кафе)

### Пользователь
- **Email**: `user@example.com`
- **Password**: `user`
- **Права**: Создание и управление своими бронированиями

⚠️ **Важно**: Измените пароли в продакшене!

## Создание пользователей

### Создание админа
```bash
docker-compose exec backend python scripts/create_user.py \
  --username admin2 \
  --email admin2@example.com \
  --password admin2 \
  --role admin
```

### Создание менеджера
```bash
docker-compose exec backend python scripts/create_user.py \
  --username manager1 \
  --email manager1@example.com \
  --password manager1 \
  --role manager
```

### Проверка прав пользователей
```bash
docker-compose exec backend python scripts/check_permissions.py
```

## Права доступа

### Кто может создавать кафе?
**Только АДМИН** может создавать кафе (POST /cafes)

### Кто может обновлять кафе?
**АДМИН и МЕНЕДЖЕР** могут обновлять кафе (PATCH /cafes/{id})
- Менеджер может обновлять только свои кафе

### Кто может удалять кафе?
**Только АДМИН** может удалять кафе (DELETE /cafes/{id})

## Структура проекта

```
booking/
├── app/                    # Backend (FastAPI)
│   ├── api/               # API роутеры
│   ├── models/            # SQLAlchemy модели
│   ├── schemas/           # Pydantic схемы
│   ├── core/              # Аутентификация и безопасность
│   ├── services/          # Бизнес-логика
│   ├── tasks/             # Celery задачи
│   └── utils/             # Утилиты
├── frontend/              # Frontend (React)
├── alembic/               # Миграции БД
├── scripts/               # Скрипты инициализации
├── docker-compose.yml     # Конфигурация Docker Compose
├── init.sh                # Скрипт инициализации
└── README.md              # Этот файл
```

## Основные команды

### Остановка сервисов
```bash
docker-compose down
```

### Просмотр логов
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Пересоздание контейнеров
```bash
docker-compose down -v  # Удаляет volumes
docker-compose up -d --build
./init.sh
```

## API Эндпоинты

- `/auth` - Аутентификация
- `/users` - Управление пользователями
- `/cafes` - Управление кафе
- `/cafe/tables` - Управление столами
- `/cafe/slots` - Управление временными слотами
- `/booking` - Управление бронированиями
- `/dishes` - Управление блюдами
- `/actions` - Управление акциями
- `/media` - Загрузка изображений

## Роли пользователей

- **admin** - Полный доступ ко всем операциям
- **manager** - Управление своими кафе, столами, слотами
- **user** - Создание и управление своими бронированиями

## Разработка

### Создание миграций
```bash
docker-compose exec backend alembic revision --autogenerate -m "Описание изменений"
docker-compose exec backend alembic upgrade head
```

### Локальная разработка (без Docker)

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте переменные окружения в `.env`

3. Запустите миграции:
```bash
alembic upgrade head
```

4. Запустите сервер:
```bash
uvicorn app.main:app --reload
```

5. В другом терминале запустите Celery worker:
```bash
celery -A app.celery_app worker --loglevel=info
```

## Troubleshooting

### Проблемы с портами
Если порты заняты, измените их в `docker-compose.yml`

### Проблемы с БД
- Проверьте что контейнер `db` запущен: `docker-compose ps`
- Проверьте логи: `docker-compose logs db`

### Проблемы с миграциями
- Убедитесь что БД запущена: `docker-compose ps db`
- Проверьте логи: `docker-compose logs backend | grep alembic`
