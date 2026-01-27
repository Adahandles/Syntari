#!/usr/bin/env bash
# Quick Setup Script for Syntari Development Environment
# One-command setup for developers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "================================================"
echo "  Syntari Development Environment Setup"
echo "================================================"
echo
echo "This script will:"
echo "  1. Check Python version"
echo "  2. Create/activate virtual environment"
echo "  3. Install dependencies"
echo "  4. Install pre-commit hooks"
echo "  5. Run initial tests"
echo "  6. Display quick start guide"
echo
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

cd "$PROJECT_ROOT"

# Step 1: Check Python version
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Step 1/6: Checking Python version..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"
python3 -c "import sys; sys.exit(0 if sys.version_info >= tuple(map(int, '$REQUIRED_VERSION'.split('.'))) else 1)" || {
    echo "❌ Python ${REQUIRED_VERSION}+ required (found: $PYTHON_VERSION)"
    exit 1
}
echo "✅ Python $PYTHON_VERSION detected"

# Step 2: Setup virtual environment
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐍 Step 2/6: Setting up virtual environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Step 3: Install dependencies
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Step 3/6: Installing dependencies..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install --upgrade pip > /dev/null
pip install -e ".[web]" > /dev/null
echo "✅ Dependencies installed"

# Step 4: Install pre-commit hooks
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 Step 4/6: Installing pre-commit hooks..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
bash scripts/install-pre-commit-hooks.sh

# Step 5: Run initial tests
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Step 5/6: Running initial tests..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if pytest tests/ -q --tb=no; then
    echo "✅ All tests passing"
else
    echo "❌ Test suite failed during setup."
    echo "Please review the pytest output above, fix the failing tests, and then re-run:"
    echo "  make test"
    echo "Aborting setup to avoid running with a potentially unstable development environment."
    exit 1
fi

# Step 6: Display quick start guide
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 Step 6/6: Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "✅ Development environment ready!"
echo
echo "Quick Start Commands:"
echo "  • Run REPL:        python3 main.py --repl"
echo "  • Run program:     python3 main.py examples/functions.syn"
echo "  • Run tests:       pytest tests/"
echo "  • Run linters:     make lint"
echo "  • Build project:   make build"
echo "  • Format code:     make format"
echo
echo "Helpful Resources:"
echo "  • Getting Started: GETTING_STARTED.md"
echo "  • Contributing:    CONTRIBUTING.md"
echo "  • Quick Reference: QUICK_REFERENCE.md"
echo
echo "To activate the virtual environment in future sessions:"
echo "  source venv/bin/activate"
echo
echo "================================================"
echo "  Happy coding! 🚀"
echo "================================================"
