.PHONY: help install install-dev test test-unit test-integration lint format clean docker-build docker-up docker-down

help:
	@echo "Modern RAG System - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-cov         Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint             Run linters (ruff, mypy)"
	@echo "  format           Format code with black"
	@echo "  format-check     Check code formatting"
	@echo "  security         Run security checks"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build     Build Docker images"
	@echo "  docker-up        Start services with Docker Compose"
	@echo "  docker-down      Stop Docker Compose services"
	@echo "  docker-test      Test inside Docker"
	@echo ""
	@echo "Utilities:"
	@echo "  clean            Clean up cache and build files"
	@echo "  pre-commit       Install pre-commit hooks"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

test-unit:
	pytest tests/unit -v -m "unit and not requires_api_key"

test-integration:
	pytest tests/integration -v -m "integration"

test-cov:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	ruff check src/ tests/ examples/ api/
	mypy src/ --install-types --non-interactive || true

format:
	black src/ tests/ examples/ api/
	ruff check --fix src/ tests/ examples/ api/

format-check:
	black --check src/ tests/ examples/ api/
	ruff check src/ tests/ examples/ api/

security:
	bandit -r src/ -f json
	safety check --json

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d qdrant
	@echo "Qdrant started at http://localhost:6333"

docker-down:
	docker-compose down -v

docker-test:
	docker-compose up -d qdrant
	sleep 5
	pytest tests/integration -v
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov/ .mypy_cache .ruff_cache
	rm -rf build/ dist/

pre-commit:
	pre-commit install
	@echo "Pre-commit hooks installed"

.DEFAULT_GOAL := help
