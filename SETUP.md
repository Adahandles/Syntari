# Syntari Repository Setup Documentation

This document describes the repository setup and development infrastructure for the Syntari Programming Language.

## What Has Been Set Up

### 1. Python Package Configuration

#### `setup.py`
- Traditional setuptools configuration
- Defines package metadata (name, version, description, author)
- Configures entry points for the `syntari` CLI command
- Lists all dependencies from `requirements.txt`
- Supports Python 3.8+

#### `pyproject.toml`
- Modern Python packaging configuration (PEP 518)
- Includes all package metadata and dependencies
- Configures development tools:
  - **pytest**: Testing framework configuration
    - Test discovery settings
    - Coverage reporting (term and HTML)
    - Verbose output by default
  - **black**: Code formatter settings
    - Line length: 100 characters
    - Target Python versions: 3.8-3.12
  - **mypy**: Type checker configuration
    - Strict equality checks
    - Warning for unused ignores and redundant casts
  - **coverage**: Code coverage settings
    - Source tracking in `src/` directory
    - Excludes test files and common non-testable code

### 2. GitHub Actions CI/CD

#### `.github/workflows/ci.yml`
Automated continuous integration workflow that runs on:
- Push to `main` and `develop` branches
- Pull requests to `main` and `develop` branches
- Manual workflow dispatch

**Three Jobs:**

1. **Test Job**
   - Runs on: Ubuntu, macOS, and Windows
   - Python versions: 3.8, 3.9, 3.10, 3.11, 3.12
   - Installs dependencies and runs pytest with coverage
   - Uploads coverage to Codecov (for Ubuntu + Python 3.12)

2. **Lint Job**
   - Runs on: Ubuntu with Python 3.12
   - Checks code formatting with Black
   - Lints code with flake8
   - Type checks with mypy

3. **Build Job**
   - Runs after test and lint jobs pass
   - Builds distribution packages (wheel and source)
   - Validates packages with twine
   - Uploads build artifacts

### 3. Development Tools

#### `.gitignore`
Comprehensive ignore patterns for:
- Python bytecode and cache files
- Virtual environments
- Distribution and build artifacts
- IDE configuration files
- Test coverage reports
- Syntari-specific files (*.sbc, *.syn.bak)

#### `Makefile`
Quick access to common development commands:
- **Setup**: `install`, `dev-install`
- **Testing**: `test`, `test-verbose`, `test-coverage`
- **Quality**: `lint`, `format`, `format-check`
- **Building**: `build`, `clean`
- **Running**: `run`, `repl`, `examples`

#### `setup.sh`
Automated setup script that:
- Checks Python and pip installation
- Upgrades pip to latest version
- Installs Syntari in development mode
- Verifies the installation
- Displays next steps for developers

### 4. Documentation

#### `CONTRIBUTING.md`
Complete guide for contributors covering:
- Development setup instructions
- Quick setup with `./setup.sh`
- Development workflow
- Testing guidelines
- Code style requirements
- Pull request process
- Project structure overview

#### Updated `README.md`
Added installation section with:
- Clone and setup instructions
- Usage examples
- Links to development resources

## Quick Start for Developers

### Initial Setup
```bash
# Clone the repository
git clone https://github.com/Adahandles/Syntari.git
cd Syntari

# Run setup script (recommended)
./setup.sh

# Or manually
pip install -e .
```

### Development Workflow
```bash
# Run tests
make test

# Run tests with coverage
make test-verbose

# Format code
make format

# Run linters
make lint

# Run Syntari programs
make run                    # runs hello_world.syn
python3 main.py file.syn    # run specific file
make repl                   # start REPL
make examples               # run all examples
```

### Building and Distribution
```bash
# Build distribution packages
make build

# Clean build artifacts
make clean
```

## CI/CD Pipeline

The GitHub Actions workflow automatically:
1. Tests code on multiple Python versions and operating systems
2. Checks code quality (formatting, linting, type checking)
3. Builds distribution packages
4. Reports test coverage

All checks must pass before code can be merged.

## Testing Infrastructure

- **Framework**: pytest 7.0+
- **Coverage**: pytest-cov 4.0+ with HTML reports
- **Current Status**: 245 tests passing
- **Test Files**: Located in `tests/` directory

## Code Quality Tools

- **Formatter**: Black (line length: 100)
- **Linter**: flake8 (complexity: 10)
- **Type Checker**: mypy (strict mode)

## Package Structure

```
Syntari/
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/CD configuration
├── src/
│   ├── core/                # Core modules
│   └── interpreter/         # Interpreter implementation
├── tests/                   # Test suite
├── examples/                # Example programs
├── .gitignore              # Git ignore patterns
├── CONTRIBUTING.md         # Contribution guide
├── Makefile               # Development commands
├── pyproject.toml         # Modern Python config
├── README.md              # Main documentation
├── requirements.txt       # Dependencies
├── setup.py              # Package setup
└── setup.sh              # Setup script
```

## Dependencies

### Runtime
- None (pure Python implementation)

### Development
- pytest >= 7.0.0 (testing)
- pytest-cov >= 4.0.0 (coverage)
- black >= 23.0.0 (formatting)
- flake8 >= 6.0.0 (linting)
- mypy >= 1.0.0 (type checking)

## Benefits of This Setup

1. **Standardized Development**: All developers use the same tools and configurations
2. **Automated Testing**: CI runs on every PR to catch issues early
3. **Code Quality**: Automated formatting and linting ensure consistency
4. **Easy Onboarding**: New contributors can get started with `./setup.sh`
5. **Cross-Platform**: Tested on Linux, macOS, and Windows
6. **Python Version Support**: Tested on Python 3.8-3.12
7. **Professional Package**: Proper packaging enables easy installation and distribution

## Next Steps

- Review CI workflow results on GitHub
- Ensure all tests pass locally before pushing
- Follow code style guidelines (run `make format` and `make lint`)
- Add tests for new features
- Update documentation as needed

## Support

For questions or issues with the setup:
- Check [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guides
- Review [GETTING_STARTED.md](GETTING_STARTED.md) for usage instructions
- Contact: legal@deuos.io
