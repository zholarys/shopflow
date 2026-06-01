.PHONY: up down build logs ps restart seed shell-backend shell-db

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose up --build -d

logs:
	docker compose logs -f

ps:
	docker compose ps

restart:
	docker compose restart

seed:
	docker exec -w /app shopflow-backend python -m app.seed

init-db:
	docker exec -w /app shopflow-backend python -m app.init_db

shell-backend:
	docker exec -it shopflow-backend bash

shell-db:
	docker exec -it shopflow-db psql -U shopflow -d shopflow

clean:
	docker compose down -v
