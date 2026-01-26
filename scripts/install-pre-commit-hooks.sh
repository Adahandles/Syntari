#!/usr/bin/env bash
# Pre-commit Hook Auto-Installer for Syntari
# This script automatically sets up pre-commit hooks in the development environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "================================================"
echo "  Syntari Pre-Commit Hook Installation"
echo "================================================"
echo

cd "$PROJECT_ROOT"

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "📦 Installing pre-commit..."
    pip install pre-commit
else
    echo "✅ pre-commit already installed"
fi

# Install the pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install

# Install commit-msg hook for conventional commits
echo "🔧 Installing commit-msg hook..."
pre-commit install --hook-type commit-msg

# Update hooks to latest versions
echo "📥 Updating hooks to latest versions..."
pre-commit autoupdate

# Run hooks on all files to verify
echo "🧪 Running hooks on all files (this may take a moment)..."
if pre-commit run --all-files; then
    echo
    echo "================================================"
    echo "✅ Pre-commit hooks installed successfully!"
    echo "================================================"
    echo
    echo "Hooks will now run automatically before each commit."
    echo "To skip hooks (not recommended): git commit --no-verify"
    echo "To run hooks manually: pre-commit run --all-files"
    echo
else
    echo
    echo "⚠️  Some hooks failed on existing files."
    echo "This is normal for existing code."
    echo "Hooks are installed and will run on new commits."
    echo
fi

exit 0
