.PHONY: help lint test sim format check clean install install-dev

help:  # Show this help
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*# .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*# "}; {printf "  %-15s %s\n", $$1, $$2}'

lint:  # Run linting (ruff check, black --check)
	ruff check src/mb_sim tests
	black --check src/mb_sim tests

format:  # Format code with black
	black src/mb_sim tests

test:  # Run tests with coverage
	pytest --cov=src/mb_sim --cov-report=term-missing

sim:  # Launch simulator CLI
	python -m mb_sim.cli

check: lint test  # Run all checks (lint + test)

clean:  # Clean up cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.pyc" -delete
	rm -rf .coverage .pytest_cache .ruff_cache

install:  # Install package in development mode
	pip install -e .

install-dev:  # Install with development dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"