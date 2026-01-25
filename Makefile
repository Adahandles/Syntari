.PHONY: help install dev-install test test-verbose lint format clean build run repl examples

help:
	@echo "Syntari Development Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install      - Install Syntari in development mode"
	@echo "  make dev-install  - Install with all development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test         - Run all tests"
	@echo "  make test-verbose - Run tests with verbose output"
	@echo "  make lint         - Run linters (flake8, mypy)"
	@echo "  make format       - Format code with black"
	@echo "  make clean        - Remove build artifacts and cache"
	@echo ""
	@echo "Building:"
	@echo "  make build        - Build distribution packages"
	@echo ""
	@echo "Running:"
	@echo "  make run          - Run hello_world.syn example"
	@echo "  make repl         - Start Syntari REPL"
	@echo "  make examples     - Run all example programs"

install:
	pip install -e ".[web]"

dev-install:
	pip install -e ".[web]"

test:
	pytest tests/

test-verbose:
	pytest tests/ -v --cov=src --cov-report=term-missing

test-coverage:
	pytest tests/ --cov=src --cov-report=html --cov-report=term

lint:
	@echo "Running flake8..."
	flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics
	@echo "Running mypy..."
	mypy src/ --ignore-missing-imports --explicit-package-bases || true

format:
	black src/ tests/

format-check:
	black --check src/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.sbc" -delete

build: clean
	pip install build
	python -m build

run:
	python3 main.py hello_world.syn

repl:
	python3 main.py --repl

examples:
	@echo "Running examples..."
	@for file in examples/*.syn; do \
		echo "=== Running $$file ==="; \
		python3 main.py $$file; \
		echo ""; \
	done
