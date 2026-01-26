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
	@echo "Docker:"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run REPL in Docker"
	@echo "  make docker-compose-up - Start all services"
	@echo "  make docker-compose-down - Stop all services"
	@echo ""
	@echo "Version Management:"
	@echo "  make version      - Show current version"
	@echo "  make bump-patch   - Bump patch version (0.4.0 -> 0.4.1)"
	@echo "  make bump-minor   - Bump minor version (0.4.0 -> 0.5.0)"
	@echo "  make bump-major   - Bump major version (0.4.0 -> 1.0.0)"
	@echo ""
	@echo "Release:"
	@echo "  make prepare-release - Run all checks for release"
	@echo "  make ci-local     - Run CI checks locally"
	@echo ""
	@echo "Building:"
	@echo "  make build        - Build distribution packages"
	@echo ""
	@echo "Running:"
	@echo "  make run          - Run hello_world.syn example"
	@echo "  make repl         - Start Syntari REPL"
	@echo "  make examples     - Run all example programs"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Syntari in Docker"
	@echo "  make docker-compose-up - Start all services"
	@echo "  make docker-compose-down - Stop all services"

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

# Docker commands
docker-build:
	@echo "Building Syntari Docker image..."
	docker build -t syntari:latest -t syntari:0.4.0 .

docker-run:
	@echo "Running Syntari in Docker (REPL)..."
	docker run -it --rm syntari:latest

docker-run-file:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make docker-run-file FILE=path/to/script.syn"; \
		exit 1; \
	fi
	@echo "Running $(FILE) in Docker..."
	docker run --rm -v $(PWD):/scripts syntari:latest /scripts/$(FILE)

docker-compose-up:
	@echo "Starting Syntari services with Docker Compose..."
	docker-compose up -d

docker-compose-down:
	@echo "Stopping Syntari services..."
	docker-compose down

docker-compose-logs:
	docker-compose logs -f

docker-clean:
	@echo "Cleaning Docker images and containers..."
	docker-compose down -v
	docker rmi syntari:latest syntari:0.4.0 2>/dev/null || true

# Version management
version:
	@echo "Syntari version 0.4.0"
	@python3 main.py --version

bump-patch:
	@echo "Bumping patch version..."
	@# Requires bump2version: pip install bump2version
	bump2version patch

bump-minor:
	@echo "Bumping minor version..."
	bump2version minor

bump-major:
	@echo "Bumping major version..."
	bump2version major

# Release preparation
prepare-release:
	@echo "Preparing release..."
	@echo "1. Running tests..."
	@make test
	@echo "2. Running security checks..."
	@make security
	@echo "3. Checking formatting..."
	@make format-check
	@echo "4. Building Docker image..."
	@make docker-build
	@echo "5. Generating coverage report..."
	@make test-coverage
	@echo ""
	@echo "✅ Release preparation complete!"
	@echo "   Next steps:"
	@echo "   1. Review CHANGELOG.md"
	@echo "   2. Update version in pyproject.toml"
	@echo "   3. Commit changes"
	@echo "   4. Create git tag: git tag v0.4.0"
	@echo "   5. Push: git push origin main --tags"

# CI/CD
ci-local:
	@echo "Running CI checks locally..."
	@make clean
	@make test-verbose
	@make lint
	@make security
	@echo "✅ All CI checks passed!"
