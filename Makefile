.PHONY: help install install-dev clean test lint format run docker-build docker-run

help:
	@echo "RepoMesh AI - Available Commands"
	@echo "================================="
	@echo "install          - Install production dependencies"
	@echo "install-dev      - Install development dependencies"
	@echo "clean            - Remove build artifacts and cache"
	@echo "test             - Run tests"
	@echo "test-cov         - Run tests with coverage"
	@echo "lint             - Run linting checks"
	@echo "format           - Format code"
	@echo "type-check       - Run type checking"
	@echo "run              - Run the API server"
	@echo "run-dev          - Run the API server in development mode"
	@echo "docker-build     - Build Docker image"
	@echo "docker-run       - Run Docker container"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test:
	pytest tests/

test-cov:
	pytest --cov=src/repomesh --cov-report=html --cov-report=term tests/

lint:
	ruff check src/ tests/

format:
	black src/ tests/
	ruff check --fix src/ tests/

type-check:
	mypy src/

run:
	uvicorn repomesh.api.main:app --host 0.0.0.0 --port 8000

run-dev:
	uvicorn repomesh.api.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t repomesh-ai:latest .

docker-run:
	docker run -p 8000:8000 \
		-e OPENAI_API_KEY=${OPENAI_API_KEY} \
		-v $(PWD)/repos:/app/repos \
		-v $(PWD)/data:/app/data \
		repomesh-ai:latest

# Made with Bob
