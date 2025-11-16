.PHONY: help build up down logs test test-backend test-e2e clean

help:
	@echo "Mood App - Make Commands"
	@echo ""
	@echo "  make build       - Build Docker images"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - View logs"
	@echo "  make test        - Run all tests"
	@echo "  make test-backend - Run backend tests"
	@echo "  make test-e2e    - Run E2E tests"
	@echo "  make clean       - Clean up containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services starting..."
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

test: test-backend test-e2e

test-backend:
	cd backend && pytest

test-e2e:
	@echo "Make sure services are running first (make up)"
	cd tests/e2e && pytest

clean:
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
