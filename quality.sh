#!/bin/bash

# Code quality check script for the RAG Chatbot project
# Usage: ./quality.sh [format|check|fix]
#
# Commands:
#   format  - Run black and isort to auto-format code
#   check   - Run flake8 and mypy to check for issues
#   fix     - Alias for format

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo "=================================="
    echo "$1"
    echo "=================================="
    echo ""
}

# Default command
COMMAND=${1:-check}

case "$COMMAND" in
    format|fix)
        print_header "Running code formatters..."

        echo -e "${GREEN}Running black...${NC}"
        uv run black backend/ *.py --line-length 100

        echo -e "${GREEN}Running isort...${NC}"
        uv run isort backend/ *.py --profile black --line-length 100

        echo -e "${GREEN}✅ Code formatted successfully!${NC}"
        ;;

    check)
        print_header "Running code quality checks..."

        echo -e "${YELLOW}Running black (check mode)...${NC}"
        if uv run black backend/ *.py --line-length 100 --check --diff; then
            echo -e "${GREEN}✅ Black checks passed${NC}"
        else
            echo -e "${RED}❌ Black formatting issues found${NC}"
            echo "Run './quality.sh format' to fix automatically"
            exit 1
        fi

        echo ""
        echo -e "${YELLOW}Running isort (check mode)...${NC}"
        if uv run isort backend/ *.py --profile black --line-length 100 --check --diff; then
            echo -e "${GREEN}✅ Isort checks passed${NC}"
        else
            echo -e "${RED}❌ Isort issues found${NC}"
            echo "Run './quality.sh format' to fix automatically"
            exit 1
        fi

        echo ""
        echo -e "${YELLOW}Running flake8...${NC}"
        if uv run flake8 backend/ *.py --max-line-length 100 --extend-ignore=E203,W503,E402; then
            echo -e "${GREEN}✅ Flake8 checks passed${NC}"
        else
            echo -e "${RED}❌ Flake8 issues found${NC}"
            exit 1
        fi

        echo ""
        echo -e "${GREEN}==================================${NC}"
        echo -e "${GREEN}✅ All quality checks passed!${NC}"
        echo -e "${GREEN}==================================${NC}"
        ;;

    *)
        echo "Usage: $0 [format|check|fix]"
        echo ""
        echo "Commands:"
        echo "  format  - Run black and isort to auto-format code"
        echo "  check   - Run flake8, black and isort to check for issues (default)"
        echo "  fix     - Alias for format"
        exit 1
        ;;
esac
