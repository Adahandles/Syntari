# Contributing to Syntari

Thank you for your interest in contributing to Syntari! This document provides guidelines and instructions for setting up your development environment.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- git

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Adahandles/Syntari.git
   cd Syntari
   ```

2. **Run the setup script:**
   ```bash
   ./setup.sh
   ```
   
   Or manually:
   ```bash
   pip install -e .
   ```

3. **Verify installation:**
   ```bash
   make test
   ```

### Development Workflow

#### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-verbose

# Run specific test file
pytest tests/test_interpreter.py
```

#### Code Quality

```bash
# Format code
make format

# Check formatting
make format-check

# Run linters
make lint
```

#### Running Syntari

```bash
# Run a Syntari program
python3 main.py hello_world.syn

# Start interactive REPL
make repl

# Run all examples
make examples
```

### Development Commands

We use Make for common development tasks. Run `make help` to see all available commands.

Key commands:
- `make install` - Install in development mode
- `make test` - Run tests
- `make lint` - Run linters
- `make format` - Format code with Black
- `make clean` - Clean build artifacts
- `make build` - Build distribution packages

### Code Style

- **Python**: We follow PEP 8 with a line length of 100 characters
- **Formatting**: Use Black for automatic formatting
- **Linting**: Code must pass flake8 checks
- **Type hints**: Encouraged where appropriate

### Testing

- All new features should include tests
- Tests should be placed in the `tests/` directory
- Use pytest for writing tests
- Aim for good test coverage

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run tests and linters (`make test && make lint`)
5. Format your code (`make format`)
6. Commit your changes
7. Push to your fork
8. Open a Pull Request

### Project Structure

```
Syntari/
├── src/
│   ├── core/          # Core modules
│   └── interpreter/   # Interpreter implementation
├── tests/             # Test files
├── examples/          # Example Syntari programs
├── docs/              # Documentation (coming soon)
└── requirements.txt   # Python dependencies
```

### Getting Help

- Read the [Getting Started Guide](GETTING_STARTED.md)
- Check the [Development Summary](DEVELOPMENT_SUMMARY.md)
- Review [Action Items](ACTION_ITEMS.md) for current priorities

## License

Syntari is proprietary software owned by DeuOS, LLC. By contributing, you agree that your contributions will be licensed under the same terms.

## Questions?

Contact: legal@deuos.io
