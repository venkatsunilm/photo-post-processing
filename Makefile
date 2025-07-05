.PHONY: help install install-dev test lint format clean setup-dev

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

setup-dev: install-dev  ## Set up development environment
	pre-commit install
	@echo "Development environment set up successfully!"

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=src --cov-report=html --cov-report=term-missing

lint:  ## Run linting checks
	flake8 src tests
	mypy src

format:  ## Format code
	black src tests
	isort src tests

format-check:  ## Check if code is formatted correctly
	black --check src tests
	isort --check-only src tests

clean:  ## Clean up generated files
	find . -type d -name __pycache__ -delete
	find . -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	rm -rf build/ dist/ *.egg-info/

run:  ## Run the main application
	python src/process_photos.py

docker-build:  ## Build Docker image
	docker build -t photo-processor .

docker-run:  ## Run Docker container
	docker run -v $(PWD)/input:/app/input -v $(PWD)/output:/app/output photo-processor
