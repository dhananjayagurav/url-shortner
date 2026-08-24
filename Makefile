.PHONY: venv install up down db-shell run test lint fmt

venv:
	python3.12 -m venv .venv
	@echo "Activate with: source .venv/bin/activate"

install:
	pip install -e ".[dev]"

up:
	docker compose up -d

down:
	docker compose down

db-shell:
	docker compose exec postgres psql -U $${POSTGRES_USER:-urlshortener} -d $${POSTGRES_DB:-urlshortener}

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v

lint:
	ruff check .

fmt:
	ruff format .
