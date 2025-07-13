.PHONY: help install install-dev test lint format clean setup-dev sync

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies (uv)
	uv sync --no-dev

install-dev:  ## Install development dependencies (uv)
	uv sync --all-extras

sync:  ## Sync dependencies with lock file (uv)
	uv sync

setup-dev: install-dev  ## Set up development environment (modern uv workflow)
	uv run pre-commit install
	@echo "Development environment set up successfully with uv!"

test:  ## Run tests (uv)
	PYTHONPATH=src uv run pytest --cov-fail-under=20

test-cov:  ## Run tests with coverage (uv)
	PYTHONPATH=src uv run pytest --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=20

lint:  ## Run linting checks (ruff + mypy)
	uv run ruff check src tests
	uv run mypy src

format:  ## Format code (ruff)
	uv run ruff format src tests

format-check:  ## Check if code is formatted correctly (ruff)
	uv run ruff format --check src tests

clean:  ## Clean up generated files
	find . -type d -name __pycache__ -delete
	find . -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	rm -rf build/ dist/ *.egg-info/

run:  ## Run the main application (uv)
	PYTHONPATH=src uv run python -m pro_photo_processor.cli

docker-build:  ## Build Docker image
	docker build -t photo-processor .

docker-run:  ## Run Docker container
	docker run -v $(PWD)/input:/app/input -v $(PWD)/output:/app/output photo-processor
