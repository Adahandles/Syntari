#!/bin/bash
# Syntari Repository Cleanup Script
# This script removes temporary files, build artifacts, and ensures a clean repository

set -e

echo "🧹 Syntari Repository Cleanup"
echo "=============================="
echo ""

# Function to safely remove files/directories
safe_remove() {
    if [ -e "$1" ]; then
        echo "Removing: $1"
        rm -rf "$1"
    fi
}

# Remove Python cache files
echo "📦 Cleaning Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.py[cod]" -delete 2>/dev/null || true
find . -type f -name "*$py.class" -delete 2>/dev/null || true

# Remove build artifacts
echo "🏗️  Cleaning build artifacts..."
safe_remove "build/"
safe_remove "dist/"
safe_remove "*.egg-info"
safe_remove "src/syntari.egg-info"
safe_remove ".eggs/"
safe_remove "*.egg"

# Remove test/coverage artifacts
echo "🧪 Cleaning test artifacts..."
safe_remove ".pytest_cache/"
safe_remove ".coverage"
safe_remove "htmlcov/"
safe_remove ".tox/"
safe_remove ".hypothesis/"
safe_remove "coverage.xml"
safe_remove ".cache/"

# Remove bytecode files
echo "📝 Cleaning Syntari bytecode files..."
find . -type f -name "*.sbc" -delete 2>/dev/null || true
find . -type f -name "*.syn.bak" -delete 2>/dev/null || true
find . -type f -name "*.syn~" -delete 2>/dev/null || true

# Remove temporary files
echo "🗑️  Cleaning temporary files..."
safe_remove "tmp/"
safe_remove "temp/"
find . -type f -name "*.tmp" -delete 2>/dev/null || true
find . -type f -name "*.bak" -delete 2>/dev/null || true
find . -type f -name "*.orig" -delete 2>/dev/null || true
find . -type f -name "*~" -delete 2>/dev/null || true

# Remove log files
echo "📋 Cleaning log files..."
find . -type f -name "*.log" -delete 2>/dev/null || true
safe_remove "logs/"

# Remove OS-specific files
echo "💻 Cleaning OS-specific files..."
find . -type f -name ".DS_Store" -delete 2>/dev/null || true
find . -type f -name "Thumbs.db" -delete 2>/dev/null || true
find . -type f -name "Desktop.ini" -delete 2>/dev/null || true

# Remove security scan reports (keep .gitignored)
echo "🔒 Cleaning security scan reports..."
safe_remove "security-report.json"
safe_remove "security-scan-report.json"
safe_remove "bandit-report.json"
safe_remove "safety-report.json"

# Remove editor swap files
echo "✏️  Cleaning editor swap files..."
find . -type f -name "*.swp" -delete 2>/dev/null || true
find . -type f -name "*.swo" -delete 2>/dev/null || true
find . -type f -name "*.swn" -delete 2>/dev/null || true

# Check for leftover virtual environments
echo "🐍 Checking for virtual environments..."
if [ -d "venv" ] || [ -d ".venv" ] || [ -d "env" ]; then
    echo "⚠️  Warning: Virtual environment directories found"
    echo "   These should not be in the repository"
    echo "   Consider: rm -rf venv/ .venv/ env/"
fi

# Check for sensitive files
echo "🔐 Checking for sensitive files..."
SENSITIVE_FOUND=false

if [ -f ".env" ]; then
    echo "⚠️  Warning: .env file found (should be .gitignored)"
    SENSITIVE_FOUND=true
fi

if find . -name "*.pem" -o -name "*.key" | grep -q .; then
    echo "⚠️  Warning: Key files found (*.pem, *.key)"
    SENSITIVE_FOUND=true
fi

if [ "$SENSITIVE_FOUND" = true ]; then
    echo ""
    echo "❌ Sensitive files detected!"
    echo "   Ensure these are listed in .gitignore"
    echo "   Never commit secrets to the repository"
fi

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Repository status:"
du -sh . 2>/dev/null || echo "Cannot determine size"

echo ""
echo "Next steps:"
echo "  - Run 'git status' to see what's changed"
echo "  - Run 'make test' to ensure everything still works"
echo "  - Run 'make security' to check for security issues"
