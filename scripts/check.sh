#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Running pre-push checks...${NC}\n"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Poetry is not installed. Please install it first:${NC}"
    echo "curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Ensure we're in the project root (where pyproject.toml is)
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Please run this script from the project root directory${NC}"
    exit 1
fi

echo -e "${GREEN}1. Installing dependencies...${NC}"
poetry install
poetry sync

echo -e "\n${GREEN}2. Running linting with ruff...${NC}"
poetry run ruff check .

echo -e "\n${GREEN}3. Running tests with coverage...${NC}"
poetry run pytest --cov --cov-report=term-missing

echo -e "\n${GREEN}All checks passed!${NC}" 