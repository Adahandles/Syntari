#!/bin/bash
# Syntari Quick Deploy Script
# Usage: ./deploy.sh [production|development|test]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ENV=${1:-production}

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Syntari Deployment Script v0.4.0    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

# Validate environment
if [[ "$ENV" != "production" && "$ENV" != "development" && "$ENV" != "test" ]]; then
    echo -e "${RED}Error: Invalid environment '$ENV'${NC}"
    echo "Usage: ./deploy.sh [production|development|test]"
    exit 1
fi

echo -e "${YELLOW}Deploying to: $ENV${NC}"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Warning: Docker not found (optional)${NC}"
fi

echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# Run health check
echo "🏥 Running health checks..."
if python3 health_check.py; then
    echo -e "${GREEN}✓ Health checks passed${NC}"
else
    echo -e "${RED}✗ Health checks failed${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
if [ "$ENV" == "production" ]; then
    pip install -q -e ".[web]"
else
    pip install -q -e ".[web]"
    pip install -q pytest pytest-cov black flake8 mypy
fi
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Run tests
if [ "$ENV" != "production" ]; then
    echo "🧪 Running tests..."
    if make test > /dev/null 2>&1; then
        echo -e "${GREEN}✓ All tests passed${NC}"
    else
        echo -e "${YELLOW}⚠ Some tests failed${NC}"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    echo ""
fi

# Security check
if [ "$ENV" == "production" ]; then
    echo "🔒 Running security checks..."
    if make security > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Security checks passed${NC}"
    else
        echo -e "${YELLOW}⚠ Security warnings found${NC}"
    fi
    echo ""
fi

# Build Docker image (if Docker available)
if command -v docker &> /dev/null; then
    echo "🐳 Building Docker image..."
    if docker build -t syntari:0.4.0 -t syntari:latest . > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Docker image built${NC}"
    else
        echo -e "${YELLOW}⚠ Docker build failed (continuing...)${NC}"
    fi
    echo ""
fi

# Deployment complete
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✓ Deployment Successful!          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

echo "Next steps:"
echo ""

if [ "$ENV" == "production" ]; then
    echo "  • Start services: docker-compose up -d"
    echo "  • Check status: docker-compose ps"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Run Syntari: python3 main.py <file.syn>"
    echo ""
    echo "  Web REPL: http://localhost:8765"
    echo "  Admin Dashboard: http://localhost:8765/admin"
else
    echo "  • Run tests: make test"
    echo "  • Start REPL: make repl"
    echo "  • Run examples: make examples"
    echo "  • Profile code: make profile FILE=script.syn"
    echo "  • Debug code: make debug FILE=script.syn"
fi

echo ""
echo -e "${GREEN}Happy coding with Syntari! 🚀${NC}"
