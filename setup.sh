#!/usr/bin/env bash
# Development setup script for Syntari

set -e

echo "================================================"
echo "Syntari Development Environment Setup"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if pip is available
echo "Checking pip..."
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "Error: pip is not installed"
    exit 1
fi

# Upgrade pip
echo ""
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install the package in development mode
echo ""
echo "Installing Syntari in development mode..."
pip install -e .

# Verify installation
echo ""
echo "Verifying installation..."
if python3 -c "import src.interpreter" &> /dev/null; then
    echo "✓ Syntari installed successfully"
else
    echo "✗ Installation verification failed"
    exit 1
fi

# Check if pytest is available
echo ""
echo "Checking test environment..."
if python3 -m pytest --version &> /dev/null; then
    echo "✓ pytest is available"
else
    echo "✗ pytest is not available"
fi

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Run tests:          make test"
echo "  2. Run hello world:    make run"
echo "  3. Start REPL:         make repl"
echo "  4. Run examples:       make examples"
echo "  5. Format code:        make format"
echo "  6. Run linters:        make lint"
echo ""
echo "For more commands, run: make help"
echo ""
