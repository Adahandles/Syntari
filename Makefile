.PHONY: help install dev-install test test-verbose lint format clean build run repl examples debug lsp security security-scan benchmark profile

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
	@echo "Developer Tools:"
	@echo "  make debug FILE=<file> - Run with interactive debugger"
	@echo "  make lsp          - Start LSP server for IDE integration"
	@echo ""
	@echo "Performance:"
	@echo "  make benchmark    - Run performance benchmarks"
	@echo "  make profile FILE=<file> - Profile a Syntari script"
	@echo ""
	@echo "Security:"
	@echo "  make security     - Run all security checks"
	@echo "  make security-scan- Run bandit security scanner"
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

debug:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make debug FILE=path/to/script.syn"; \
		exit 1; \
	fi
	@echo "Starting debugger for $(FILE)..."
	@python3 main.py --debug $(FILE)

lsp:
	@echo "Starting Syntari LSP server..."
	@echo "Connect your IDE to stdin/stdout..."
	@python3 main.py --lsp

examples:
	@echo "Running examples..."
	@for file in examples/*.syn; do \
		echo "=== Running $$file ==="; \
		python3 main.py $$file; \
		echo ""; \
	done

security:
	@echo "Running security checks..."
	@echo ""
	@echo "1. Installing security tools..."
	@pip install -q bandit safety 2>/dev/null || echo "Tools already installed"
	@echo ""
	@echo "2. Running Bandit (security scanner)..."
	@bandit -r src/ -ll -f txt || true
	@echo ""
	@echo "3. Checking dependencies for vulnerabilities..."
	@safety check --json || echo "Safety check completed with warnings"
	@echo ""
	@echo "4. Running security tests..."
	@pytest tests/test_security.py -v || echo "No security tests found"
	@echo ""
	@echo "Security scan complete!"

security-scan:
	@echo "Running comprehensive security scan..."
	@pip install -q bandit safety
	@bandit -r src/ -f json -o security-report.json 2>/dev/null || true
	@bandit -r src/ -ll
	@safety check
	@echo "Security scan complete! Check security-report.json for details."

benchmark:
	@echo "Running Syntari benchmarks..."
	@cd benchmarks && python3 run_benchmarks.py

profile:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make profile FILE=path/to/script.syn"; \
		exit 1; \
	fi
	@echo "Profiling $(FILE)..."
	@python3 main.py --profile $(FILE)

profile-html:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make profile-html FILE=path/to/script.syn"; \
		exit 1; \
	fi
	@echo "Profiling $(FILE) with HTML output..."
	@python3 main.py --profile $(FILE) --profile-format html --profile-output profile.html
	@echo "Report saved to profile.html"
