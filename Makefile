.PHONY: help build push deploy restart logs clean

help:
	@echo "Доступные команды:"
	@echo "  make build      - Собрать Docker образы"
	@echo "  make push        - Запушить образы в Docker Hub"
	@echo "  make deploy      - Развернуть на production сервере"
	@echo "  make restart     - Перезапустить контейнеры"
	@echo "  make logs        - Показать логи контейнеров"
	@echo "  make clean       - Очистить неиспользуемые образы и контейнеры"

build:
	docker build -f env/backend/Dockerfile -t booking_backend:latest .
	cd frontend && docker build -f Dockerfile -t booking_frontend:build .
	docker build -f env/frontend/Dockerfile -t booking_frontend:latest .

push:
	docker tag booking_backend:latest ${DOCKER_USERNAME}/booking_backend:latest
	docker tag booking_frontend:latest ${DOCKER_USERNAME}/booking_frontend:latest
	docker push ${DOCKER_USERNAME}/booking_backend:latest
	docker push ${DOCKER_USERNAME}/booking_frontend:latest

deploy:
	docker compose -f docker-compose.production.yml pull
	docker compose -f docker-compose.production.yml down
	docker compose -f docker-compose.production.yml up -d

restart:
	docker compose -f docker-compose.production.yml restart

logs:
	docker compose -f docker-compose.production.yml logs -f

clean:
	docker system prune -f
	docker volume prune -f

